from hashlib import new
import os
import os.path
import shutil

from leapp.libraries.stdlib import api

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"

def build_repo_paths(name_with_rpmnew):
    base_filename = name_with_rpmnew[:-7]  # Clear ".rpmnew" from name
    new_repo_path = os.path.join(REPO_ROOT_PATH, name_with_rpmnew)
    base_repo_path = os.path.join(REPO_ROOT_PATH, base_filename)
    old_repo_path = os.path.join(REPO_ROOT_PATH, base_filename + ".rpmsave")
    return (base_repo_path, old_repo_path, new_repo_path)

def rename_rpmnew():
    for repofile in os.listdir(REPO_ROOT_PATH):
        if repofile.endswith(".rpmnew"):
            base_path, old_path, new_path = build_repo_paths(repofile)

            os.rename(base_path, old_path)
            os.rename(new_path, base_path)

def add_custom():
    custom_repo_dir = api.get_common_folder_path(CUSTOM_REPOS_FOLDER)

    for repofile in os.listdir(custom_repo_dir):
        full_repo_path = os.path.join(custom_repo_dir, repofile)
        shutil.copy(full_repo_path, REPO_ROOT_PATH)
