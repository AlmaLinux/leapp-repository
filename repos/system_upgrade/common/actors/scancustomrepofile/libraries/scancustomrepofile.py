import os

from leapp.libraries.common import repofileutils
from leapp.libraries.stdlib import api
from leapp.models import CustomTargetRepository, CustomTargetRepositoryFile

from leapp.reporting import create_report
from leapp import reporting

CUSTOM_REPO_PATH = "/etc/leapp/files/leapp_upgrade_repositories.repo"


def process():
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

    repos_with_missing_keys, missing_gpgkeys = repofileutils.check_gpgkey_existence(repofile.data)
    if repos_with_missing_keys:
        repos_related = [reporting.RelatedResource('repository', str(r)) for r in repos_with_missing_keys]
        gpgkeys_related = [reporting.RelatedResource('file', str(r)) for r in missing_gpgkeys]
        create_report([
            reporting.Title('GPG key for one or more custom target repositories is missing'),
            reporting.Summary(
                    'Some of the GPG keys for repositories listed in the custom repository '
                    'file weren\'t found in the system. '
                    'If the upgrade proceeds as-is, this will cause issues with retreiving packages '
                    'from said repositories. '
                    'Check the list of missing keys and ensure all of them are present on the system '
                    'before restarting the upgrade process.'
                ),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Tags([
                    reporting.Tags.FILESYSTEM,
                    reporting.Tags.REPOSITORY,
                    reporting.Tags.SECURITY
            ]),
            reporting.Remediation(hint='Add the missing keys to the system before continuing.'),
            reporting.Flags([reporting.Flags.INHIBITOR]),
            reporting.RelatedResource('file', '/etc/leapp/leapp_upgrade_repositories.repo')
        ] + gpgkeys_related + repos_related)

    else:
        for repo in repofile.data:
            api.produce(
                CustomTargetRepository(
                    repoid=repo.repoid,
                    name=repo.name,
                    baseurl=repo.baseurl,
                    enabled=repo.enabled,
                )
            )
        api.produce(CustomTargetRepositoryFile(file=CUSTOM_REPO_PATH))
        api.current_logger().info(
            "The {} file exists, custom repositories loaded.".format(CUSTOM_REPO_PATH)
        )
