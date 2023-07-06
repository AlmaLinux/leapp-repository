import os

from leapp.models import (
    CustomTargetRepositoryFile,
    CustomTargetRepository,
    UsedRepositories,
)
from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils

from leapp.libraries.common.repositories import (
    is_rollout_repository,
    create_leapp_repofile_copy,
    REPO_DIR,
    REPOFILE_SUFFIX,
)


def replace_releasever(lines):
    return [line.replace("$releasever", "8") for line in lines]


def modify_inplace(filepath):
    with open(filepath, "r") as repo_f:
        lines = replace_releasever(repo_f.readlines())
    with open(filepath, "w") as repo_f:
        repo_f.writelines(lines)


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

        full_rollout_repo_path = os.path.join(REPO_DIR, repofile)
        rollout_repodata = repofileutils.parse_repofile(full_rollout_repo_path)

        # Ignore the repositories (and their files) that are enabled, but have no packages installed from them.
        if not any(repo.repoid in used_list for repo in rollout_repodata.data):
            api.current_logger().debug(
                "No used repositories found in {}, skipping".format(repofile)
            )
            continue
        else:
            api.current_logger().debug(
                "Rollout file {} has used repositories, adding".format(repofile)
            )

        for repo in rollout_repodata.data:
            # On some systems, $releasever gets replaced by a string like "8.6", but we want
            # specifically "8" for rollout repositories - URLs with "8.6" don't exist.
            repo.baseurl = repo.baseurl.replace("$releasever", "8")

        rollout_reponame = repofile[: -len(REPOFILE_SUFFIX)]
        leapp_repocopy_path = create_leapp_repofile_copy(rollout_repodata, rollout_reponame)

        for repo in rollout_repodata.data:
            api.produce(
                CustomTargetRepository(
                    repoid=repo.repoid,
                    name=repo.name,
                    baseurl=repo.baseurl,
                    enabled=repo.enabled,
                )
            )

        api.produce(CustomTargetRepositoryFile(file=leapp_repocopy_path))
