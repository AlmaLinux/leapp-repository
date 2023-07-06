import os

from leapp.models import (
    CustomTargetRepositoryFile,
    CustomTargetRepository,
    UsedRepositories,
)
from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils

from leapp.libraries.common.cl_repofileutils import (
    is_rollout_repository,
    create_leapp_repofile_copy,
    REPO_DIR,
    REPOFILE_SUFFIX,
)


def process_repodata(rollout_repodata):
    for repo in rollout_repodata.data:
        # On some systems, $releasever gets replaced by a string like "8.6", but we want
        # specifically "8" for rollout repositories - URLs with "8.6" don't exist.
        repo.baseurl = repo.baseurl.replace("$releasever", "8")

    for repo in rollout_repodata.data:
        api.produce(
            CustomTargetRepository(
                repoid=repo.repoid,
                name=repo.name,
                baseurl=repo.baseurl,
                enabled=repo.enabled,
            )
        )

    rollout_reponame = rollout_repodata.file[:-len(REPOFILE_SUFFIX)]
    leapp_repocopy_path = create_leapp_repofile_copy(rollout_repodata, rollout_reponame)
    api.produce(CustomTargetRepositoryFile(file=leapp_repocopy_path))


def process_repofile(repofile, used_list):
    full_rollout_repo_path = os.path.join(REPO_DIR, repofile)
    rollout_repodata = repofileutils.parse_repofile(full_rollout_repo_path)

    # Ignore the repositories (and their files) that are enabled, but have no packages installed from them.
    if not any(repo.repoid in used_list for repo in rollout_repodata.data):
        api.current_logger().debug(
            "No used repositories found in {}, skipping".format(repofile)
        )
        return

    api.current_logger().debug("Rollout file {} has used repositories, adding".format(repofile))
    process_repodata(rollout_repodata)


def process():
    used_list = []
    for used_repos in api.consume(UsedRepositories):
        for used_repo in used_repos.repositories:
            used_list.append(used_repo.repository)

    for repofile in os.listdir(REPO_DIR):
        if not is_rollout_repository(repofile):
            continue

        api.current_logger().debug(
            "Detected a rollout repository file: {}".format(repofile)
        )

        process_repofile(repofile, used_list)
