import os

from leapp.libraries.common import repofileutils
from leapp.libraries.stdlib import api
from leapp.models import (
    CustomTargetRepository,
    CustomTargetRepositoryFile,
    ActiveVendorList,
    VendorCustomTargetRepositoryList,
)
from leapp.reporting import create_report
from leapp import reporting

VENDORS_DIR = "/etc/leapp/files/vendors.d/"
REPOFILE_SUFFIX = ".repo"


def process():
    """
    Produce CustomTargetRepository msgs for the vendor repo files inside the
    <CUSTOM_REPO_DIR>.

    The CustomTargetRepository messages are produced only if a "from" vendor repository
    listed indide its map matched one of the repositories active on the system.
    """
    if not os.path.isdir(VENDORS_DIR):
        api.current_logger().debug(
            "The {} directory doesn't exist. Nothing to do.".format(VENDORS_DIR)
        )
        return

    for reponame in os.listdir(VENDORS_DIR):
        if not reponame.endswith(REPOFILE_SUFFIX):
            continue
        # Cut the .repo part to get only the name.
        vendor_name = reponame[:-5]

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        api.current_logger().debug("Active vendor list: {}".format(active_vendors))

        if vendor_name not in active_vendors:
            api.current_logger().debug(
                "Vendor {} not in active list, skipping".format(vendor_name)
            )
            continue

        api.current_logger().debug(
            "Vendor {} found in active list, processing file".format(vendor_name)
        )
        full_repo_path = os.path.join(VENDORS_DIR, reponame)
        repofile = repofileutils.parse_repofile(full_repo_path)

        repos_with_missing_keys, missing_gpgkeys = repofileutils.check_gpgkey_existence(repofile.data)

        if repos_with_missing_keys:
            repos_related = [reporting.RelatedResource('repository', str(r)) for r in repos_with_missing_keys]
            gpgkeys_related = [reporting.RelatedResource('file', str(r)) for r in missing_gpgkeys]
            create_report([
                reporting.Title('GPG key for one or more vendor target repositories is missing'),
                reporting.Summary(
                        'Some of the GPG keys for repositories listed in the vendor repository '
                        'file {} weren\'t found in the system. '
                        'If the upgrade proceeds as-is, this will cause issues with retreiving packages '
                        'from said repositories. '
                        'Check the list of missing keys and ensure all of them are present on the system '
                        'before restarting the upgrade process.'.format(reponame)
                    ),
                reporting.Summary(),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([
                        reporting.Tags.FILESYSTEM,
                        reporting.Tags.REPOSITORY,
                        reporting.Tags.SECURITY
                ]),
                reporting.Remediation(hint='Add the missing keys to the system before continuing.'),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.RelatedResource('file', full_repo_path)
            ] + gpgkeys_related + repos_related)

        else:
            custom_vendor_repos = [
                CustomTargetRepository(
                    repoid=repo.repoid,
                    name=repo.name,
                    baseurl=repo.baseurl,
                    enabled=repo.enabled,
                ) for repo in repofile.data
            ]
            api.produce(CustomTargetRepositoryFile(file=full_repo_path))

            api.produce(
                VendorCustomTargetRepositoryList(vendor=vendor_name, repos=custom_vendor_repos)
            )

    api.current_logger().info(
        "The {} directory exists, vendor repositories loaded.".format(VENDORS_DIR)
    )
