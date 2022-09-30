import os

from leapp.libraries.common import repofileutils
from leapp.libraries.stdlib import api
from leapp.models import CustomTargetRepository, CustomTargetRepositoryFile


CUSTOM_REPO_PATH = "/etc/leapp/files/leapp_upgrade_repositories.repo"
CUSTOM_REPO_BETA_PATH = "/etc/leapp/files/leapp_upgrade_repositories_beta.repo"
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
            "The {} file doesn't exist. Nothing to do.".format(CUSTOM_REPO_PATH)
        )
        return

    repofile = repofileutils.parse_repofile(CUSTOM_REPO_PATH)
    if not repofile.data:
        api.current_logger().info(
            "The {} file exists, but is empty. Nothing to do.".format(CUSTOM_REPO_PATH)
        )
        return
    api.produce(CustomTargetRepositoryFile(file=CUSTOM_REPO_PATH))

    api.current_logger().debug("Current target system type: {}".format(target_type))
    if target_type == "beta":
        api.current_logger().info(
            "Beta target type, loading the auxillary custom repo file {}.".format(CUSTOM_REPO_BETA_PATH)
        )

        beta_repofile = repofileutils.parse_repofile(CUSTOM_REPO_PATH)
        if not beta_repofile.data:
            api.current_logger().info(
                "Beta repo file {} exists, but is empty. Nothing to do.".format(CUSTOM_REPO_BETA_PATH)
            )
        else:
            repofile.data.extend(beta_repofile.data)

    for repo in repofile.data:
        api.produce(
            CustomTargetRepository(
                repoid=repo.repoid,
                name=repo.name,
                baseurl=repo.baseurl,
                enabled=repo.enabled,
            )
        )
    api.current_logger().info(
        "The {} file exists, custom repositories loaded.".format(CUSTOM_REPO_PATH)
    )
