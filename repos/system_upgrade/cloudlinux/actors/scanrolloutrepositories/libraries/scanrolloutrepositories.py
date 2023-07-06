import os

from leapp.models import (
    CustomTargetRepositoryFile,
    CustomTargetRepository,
    UsedRepositories
)
from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils

REPO_DIR = '/etc/yum.repos.d'
ROLLOUT_MARKER = 'rollout'
CL_MARKERS = ['cloudlinux', 'imunify']


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

    for reponame in os.listdir(REPO_DIR):
        if ROLLOUT_MARKER not in reponame or not any(mark in reponame for mark in CL_MARKERS):
            continue

        api.current_logger().debug("Detected a rollout repository file: {}".format(reponame))

        full_repo_path = os.path.join(REPO_DIR, reponame)

        # On some systems, $releasever gets replaced by a string like "8.6", but we want specifically
        # "8" for rollout repositories - URLs with "8.6" don't exist.
        modify_inplace(full_repo_path)

        repofile = repofileutils.parse_repofile(full_repo_path)

        # Ignore the repositories that are enabled, but have no packages installed from them.
        if not any(repo.repoid in used_list for repo in repofile.data):
            api.current_logger().debug("No used repositories found in {}, skipping".format(reponame))
            continue
        else:
            api.current_logger().debug("Rollout file {} has used repositories, adding".format(reponame))

        for repo in repofile.data:
            api.produce(CustomTargetRepository(
                repoid=repo.repoid,
                name=repo.name,
                baseurl=repo.baseurl,
                enabled=repo.enabled,
            ))

        api.produce(CustomTargetRepositoryFile(file=full_repo_path))
