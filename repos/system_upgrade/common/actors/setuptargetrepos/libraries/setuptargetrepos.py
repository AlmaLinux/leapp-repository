
from leapp.libraries.actor import setuptargetrepos_repomap
from leapp.libraries.common.config.version import get_source_major_version
from leapp.libraries.stdlib import api
from leapp.models import (
    CustomTargetRepository,
    RepositoriesBlacklisted,
    RepositoriesFacts,
    RepositoriesMapping,
    RepositoriesSetupTasks,
    RHELTargetRepository,
    RHUIInfo,
    SkippedRepositories,
    TargetRepositories,
    UsedRepositories,
    VendorCustomTargetRepositoryList
)


def _get_enabled_repoids():
    """
    Collects repoids of all enabled repositories on the source system.

    :param repositories_facts: Iterable of RepositoriesFacts containing info about repositories on the source system.
    :returns: Set of all enabled repository IDs present on the source system.
    :rtype: Set[str]
    """
    enabled_repoids = set()
    for repos in api.consume(RepositoriesFacts):
        for repo_file in repos.repositories:
            for repo in repo_file.data:
                if repo.enabled:
                    enabled_repoids.add(repo.repoid)
    return enabled_repoids


def _get_blacklisted_repoids():
    repos_blacklisted = set()
    for blacklist in api.consume(RepositoriesBlacklisted):
        repos_blacklisted.update(blacklist.repoids)
    return repos_blacklisted


def _get_custom_target_repos():
    custom_repos = []
    for repo in api.consume(CustomTargetRepository):
        custom_repos.append(repo)
    return custom_repos


def _get_used_repo_dict():
    """
    Return dict: {used_repoid: [installed_packages]}
    """
    used = {}
    for used_repos in api.consume(UsedRepositories):
        for used_repo in used_repos.repositories:
            used[used_repo.repository] = used_repo.packages
    return used


def _setup_repomap_handler(src_repoids, mapping_list):
    combined_mapping = []
    combined_repositories = []
    # Depending on whether there are any vendors present, we might get more than one message.
    for msg in mapping_list:
        combined_mapping.extend(msg.mapping)
        combined_repositories.extend(msg.repositories)

    combined_repomapping = RepositoriesMapping(
        mapping=combined_mapping,
        repositories=combined_repositories
    )

    rhui_info = next(api.consume(RHUIInfo), RHUIInfo(provider=''))
    repomap = setuptargetrepos_repomap.RepoMapDataHandler(combined_repomapping, cloud_provider=rhui_info.provider)
    # TODO(pstodulk): what about skip this completely and keep the default 'ga'..?
    default_channels = setuptargetrepos_repomap.get_default_repository_channels(repomap, src_repoids)
    repomap.set_default_channels(default_channels)
    return repomap


def _get_mapped_repoids(repomap, src_repoids):
    mapped_repoids = set()
    src_maj_ver = get_source_major_version()
    for repoid in src_repoids:
        if repomap.get_pesid_repo_entry(repoid, src_maj_ver):
            mapped_repoids.add(repoid)
    return mapped_repoids


def _get_vendor_custom_repos(enabled_repos, mapping_list):
    # Look at what source repos from the vendor mapping were enabled.
    # If any of them are in beta, include vendor's custom repos in the list.
    # Otherwise skip them.

    result = []

    # Build a dict of vendor mappings for easy lookup.
    map_dict = {mapping.vendor: mapping for mapping in mapping_list if mapping.vendor}

    for vendor_repolist in api.consume(VendorCustomTargetRepositoryList):
        vendor_repomap = map_dict[vendor_repolist.vendor]

        # Find the beta channel repositories for the vendor.
        beta_repos = [
            x.repoid for x in vendor_repomap.repositories if x.channel == "beta"
        ]
        api.current_logger().debug(
            "Vendor {} beta repos: {}".format(vendor_repolist.vendor, beta_repos)
        )

        # Are any of the beta repos present and enabled on the system?
        if any(rep in beta_repos for rep in enabled_repos):
            # If so, use all repos including beta in the upgrade.
            vendor_repos = vendor_repolist.repos
        else:
            # Otherwise filter beta repos out.
            vendor_repos = [repo for repo in vendor_repolist.repos if repo.repoid not in beta_repos]

        result.extend([CustomTargetRepository(
            repoid=repo.repoid,
            name=repo.name,
            baseurl=repo.baseurl,
            enabled=repo.enabled,
        ) for repo in vendor_repos])

    return result


def process():
    # load all data / messages
    used_repoids_dict = _get_used_repo_dict()
    enabled_repoids = _get_enabled_repoids()
    excluded_repoids = _get_blacklisted_repoids()

    mapping_list = list(api.consume(RepositoriesMapping))

    custom_repos = _get_custom_target_repos()
    vendor_repos = _get_vendor_custom_repos(enabled_repoids, mapping_list)

    api.current_logger().debug('Custom repos: {}'.format([f.repoid for f in custom_repos]))
    api.current_logger().debug('Vendor repos: {}'.format([f.repoid for f in vendor_repos]))

    custom_repos.extend(vendor_repos)

    api.current_logger().debug('Used repos: {}'.format(used_repoids_dict.keys()))
    api.current_logger().debug('Enabled repos: {}'.format(list(enabled_repoids)))

    # TODO(pstodulk): isn't that a potential issue that we map just enabled repos
    # instead of enabled + used repos??
    # initialise basic data
    repomap = _setup_repomap_handler(enabled_repoids, mapping_list)
    mapped_repoids = _get_mapped_repoids(repomap, enabled_repoids)
    api.current_logger().debug('Mapped repos: {}'.format(mapped_repoids))
    skipped_repoids = enabled_repoids & set(used_repoids_dict.keys()) - mapped_repoids

    # Now get the info what should be the target RHEL repositories
    expected_repos = repomap.get_expected_target_pesid_repos(enabled_repoids)
    api.current_logger().debug('Expected repos: {}'.format(expected_repos.keys()))
    target_rhel_repoids = set()
    for target_pesid, target_pesidrepo in expected_repos.items():
        if not target_pesidrepo:
            # With the original repomap data, this should not happen (this should
            # currently point to a problem in our data
            # TODO(pstodulk): add report? inhibitor? what should be in the report?
            api.current_logger().error(
                'Missing target repository from the {} family (PES ID).'
                .format(target_pesid)
            )
            continue
        if target_pesidrepo.repoid in excluded_repoids:
            api.current_logger().debug('Skipping the {} repo (excluded).'.format(target_pesidrepo.repoid))
            continue
        target_rhel_repoids.add(target_pesidrepo.repoid)

    # FIXME: this could possibly result into a try to enable multiple repositories
    # from the same family (pesid). But unless we have a bug in previous actors,
    # it should not happen :) it's not blocker error anyway, so survive it.
    # - We expect to deliver the fix as part of the refactoring when we merge
    # setuptargetrepos & peseventsscanner actors together (+ blacklistrepos?)
    for task in api.consume(RepositoriesSetupTasks):
        for repo in task.to_enable:
            if repo in excluded_repoids:
                api.current_logger().debug('Skipping the {} repo from setup task (excluded).'.format(repo))
                continue
            target_rhel_repoids.add(repo)

    # create the final lists and sort them (for easier testing)
    rhel_repos = [RHELTargetRepository(repoid=repoid) for repoid in sorted(target_rhel_repoids)]
    custom_repos = [repo for repo in custom_repos if repo.repoid not in excluded_repoids]
    custom_repos = sorted(custom_repos, key=lambda x: x.repoid)

    if skipped_repoids:
        pkgs = set()
        for repo in skipped_repoids:
            pkgs.update(used_repoids_dict[repo])
        api.produce(SkippedRepositories(repos=sorted(skipped_repoids), packages=sorted(pkgs)))

    api.produce(TargetRepositories(
        rhel_repos=rhel_repos,
        custom_repos=custom_repos,
    ))
