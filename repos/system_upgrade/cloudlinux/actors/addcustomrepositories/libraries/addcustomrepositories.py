import os
import os.path
import shutil
import logging

from leapp.libraries.stdlib import api

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"


def add_custom(log):
    # type: (logging.Logger) -> None
    custom_repo_dir = api.get_common_folder_path(CUSTOM_REPOS_FOLDER)

    repofiles = os.listdir(custom_repo_dir)
    # If folder is empty, halt
    if not repofiles:
        return

    for repofile in repofiles:
        full_repo_path = os.path.join(custom_repo_dir, repofile)

        log.debug("Copying repo file {} to {}".format(repofile, REPO_ROOT_PATH))

        shutil.copy(full_repo_path, REPO_ROOT_PATH)
