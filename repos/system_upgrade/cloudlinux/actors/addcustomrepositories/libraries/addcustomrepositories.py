import os
import os.path
import shutil

from leapp.libraries.stdlib import api

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"

def add_custom():
    custom_repo_dir = api.get_common_folder_path(CUSTOM_REPOS_FOLDER)

    for repofile in os.listdir(custom_repo_dir):
        full_repo_path = os.path.join(custom_repo_dir, repofile)
        shutil.copy(full_repo_path, REPO_ROOT_PATH)
