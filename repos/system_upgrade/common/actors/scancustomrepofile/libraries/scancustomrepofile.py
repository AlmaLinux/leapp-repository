import os

from leapp.libraries.common import repofileutils
from leapp.libraries.stdlib import api
from leapp.models import CustomTargetRepository, CustomTargetRepositoryFile


CUSTOM_REPO_PATH = "/etc/leapp/files/leapp_upgrade_repositories.repo"
BETA_REPO_TAG = "testing"


def process(target_type="stable"):
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
    repofile = repofileutils.parse_repofile(CUSTOM_REPO_PATH)
    if not repofile.data:
        api.current_logger().info("The {} file exists, but is empty. Nothing to do.".format(CUSTOM_REPO_PATH))
        return

    api.produce(CustomTargetRepositoryFile(file=CUSTOM_REPO_PATH))
    api.current_logger().debug("Current target system type: {}".format(target_type))
    for repo in repofile.data:
        # Enable beta repositories if we're upgrading to a beta target system.
        api.current_logger().debug("Processing repoid: {}".format(repo.repoid))
        if target_type == "beta" and BETA_REPO_TAG in repo.repoid:
            api.current_logger().debug("Repo considered to be beta and enabled")
            repo.enabled = True
        else:
            api.current_logger().debug("Repo processed as normal, enabled={}".format(repo.enabled))

        api.produce(CustomTargetRepository(
            repoid=repo.repoid,
            name=repo.name,
            baseurl=repo.baseurl,
            enabled=repo.enabled,
        ))
    api.current_logger().info("The {} file exists, custom repositories loaded.".format(CUSTOM_REPO_PATH))
