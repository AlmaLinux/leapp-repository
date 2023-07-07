import os
import os.path

from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils

ROLLOUT_MARKER = 'rollout'
CL_MARKERS = ['cloudlinux', 'imunify']

REPO_DIR = '/etc/yum.repos.d'
TEMP_DIR = '/var/lib/leapp/yum_custom_repofiles'
LEAPP_COPY_SUFFIX = "_leapp_custom.repo"
REPOFILE_SUFFIX = ".repo"


def is_rollout_repository(repofile):
    return ROLLOUT_MARKER in repofile and any(mark in repofile for mark in CL_MARKERS)


def create_leapp_repofile_copy(repofile_data, repo_name):
    """
    Create a copy of an existing Yum repository config file, modified
    to be used during the Leapp transaction.
    It will be placed inside the isolated overlay environment Leapp runs the upgrade from.
    """
    if not os.path.isdir(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    leapp_repofile = repo_name + LEAPP_COPY_SUFFIX
    leapp_repo_path = os.path.join(TEMP_DIR, leapp_repofile)
    if os.path.exists(leapp_repo_path):
        os.unlink(leapp_repo_path)

    api.current_logger().debug('Producing a Leapp repofile copy: {}'.format(leapp_repo_path))
    repofileutils.save_repofile(repofile_data, leapp_repo_path)
    return leapp_repo_path
