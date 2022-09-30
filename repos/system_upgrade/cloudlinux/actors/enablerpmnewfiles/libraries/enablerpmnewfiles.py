import os
import os.path
import logging

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"


def build_repo_paths(name_with_rpmnew):
    base_filename = name_with_rpmnew[:-7]  # Clear ".rpmnew" from name
    new_repo_path = os.path.join(REPO_ROOT_PATH, name_with_rpmnew)
    base_repo_path = os.path.join(REPO_ROOT_PATH, base_filename)
    old_repo_path = os.path.join(REPO_ROOT_PATH, base_filename + ".rpmsave")
    return (base_repo_path, old_repo_path, new_repo_path)


def rename_rpmnew(log):
    # type: (logging.Logger) -> None
    for repofile in os.listdir(REPO_ROOT_PATH):
        if repofile.endswith(".rpmnew"):
            base_path, old_path, new_path = build_repo_paths(repofile)

            log.debug("Renaming {} to {}, old file moved to {}".format(repofile, new_path, old_path))

            os.rename(base_path, old_path)
            os.rename(new_path, base_path)
