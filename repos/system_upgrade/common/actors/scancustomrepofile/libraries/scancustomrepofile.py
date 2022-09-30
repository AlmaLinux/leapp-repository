import os

from leapp.libraries.common import repofileutils
from leapp.libraries.stdlib import api
from leapp.models import CustomTargetRepository, CustomTargetRepositoryFile, TargetSystemType


CUSTOM_REPO_PATH = "/etc/leapp/files/leapp_upgrade_repositories.repo"
BETA_REPO_TAG = "testing"


def process():
    """
    Produce CustomTargetRepository msgs for the custom repo file if the file
    exists.

    The CustomTargetRepository msg is produced for every repository inside
    the <CUSTOM_REPO_PATH> file.
    """
    if not os.path.isfile(CUSTOM_REPO_PATH):
        api.current_logger().debug(
                "The {} file doesn't exist. Nothing to do."
                .format(CUSTOM_REPO_PATH))
        return
    api.current_logger().info("The {} file exists.".format(CUSTOM_REPO_PATH))
    repofile = repofileutils.parse_repofile(CUSTOM_REPO_PATH)
    if not repofile.data:
        return

    type_message = next(api.consume(TargetSystemType), None)
    if not type_message:
        api.current_logger().info(('The current configuration does not provide a target system type, assuming stable'))
        target_type = "stable"
    else:
        target_type = type_message.system_type

    api.produce(CustomTargetRepositoryFile(file=CUSTOM_REPO_PATH))
    for repo in repofile.data:
        # Enable beta repositories if we're upgrading to a beta target system.
        if target_type == "beta" and BETA_REPO_TAG in repo.repoid:
            repo.enabled = True
        api.produce(CustomTargetRepository(
            repoid=repo.repoid,
            name=repo.name,
            baseurl=repo.baseurl,
            enabled=repo.enabled,
        ))
