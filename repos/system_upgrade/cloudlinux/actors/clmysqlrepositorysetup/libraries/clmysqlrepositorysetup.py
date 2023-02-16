import os

from leapp.models import (
    CustomTargetRepositoryFile,
    CustomTargetRepository
)
from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils
from leapp import reporting

REPO_DIR = '/etc/yum.repos.d'
REPOFILE_SUFFIX = ".repo"
LEAPP_COPY_SUFFIX = "_leapp_custom.repo"
CL_MARKERS = ['cl-mysql', 'cl-mariadb', 'cl-percona']
MARIA_MARKERS = ['MariaDB']
MYSQL_MARKERS = ['mysql-community']
OLD_MYSQL_VERSIONS = ['5.7', '5.6', '5.5']


def produce_leapp_repofile_copy(repofile_data, repo_name):
    """
    Create a copy of an existing Yum repository config file, modified
    to be used during the Leapp transaction.
    It will be placed inside the isolated overlay environment Leapp runs the upgrade from.
    """
    leapp_repofile = repo_name + LEAPP_COPY_SUFFIX
    leapp_repo_path = os.path.join(REPO_DIR, leapp_repofile)
    if os.path.exists(leapp_repo_path):
        os.unlink(leapp_repo_path)
    repofileutils.save_repofile(repofile_data, leapp_repo_path)
    api.produce(CustomTargetRepositoryFile(file=leapp_repo_path))


def process():
    for repofile_full in os.listdir(REPO_DIR):
        # Don't touch non-repository files or copied repofiles created by Leapp.
        if repofile_full.endswith(LEAPP_COPY_SUFFIX) or not repofile_full.endswith(REPOFILE_SUFFIX):
            continue
        # Cut the .repo part to get only the name.
        repofile_name = repofile_full[:-5]
        full_repo_path = os.path.join(REPO_DIR, repofile_full)

        # Parse any repository files that may have something to do with MySQL or MariaDB.
        api.current_logger().debug('Processing repofile {}, full path: {}'.format(repofile_full, full_repo_path))

        # Process CL-provided options.
        if any(mark in repofile_name for mark in CL_MARKERS):
            repofile_data = repofileutils.parse_repofile(full_repo_path)
            api.current_logger().debug('Data from repofile: {}'.format(repofile_data.data))

            # Were any repositories enabled?
            for repo in repofile_data.data:
                # We don't want any duplicate repoid entries.
                repo.repoid = repo.repoid + '-8'
                # releasever may be something like 8.6, while only 8 is acceptable.
                repo.baseurl = repo.baseurl.replace('/cl$releasever/', '/cl8/')
                # mysqlclient is usually disabled when installed from CL MySQL Governor.
                # However, it should be enabled for the Leapp upgrade, seeing as some packages
                # from it won't update otherwise.

                if repo.enabled or repo.repoid == 'mysqclient-8':
                    api.current_logger().debug('Generating custom cl-mysql repo: {}'.format(repo.repoid))
                    api.produce(CustomTargetRepository(
                        repoid=repo.repoid,
                        name=repo.name,
                        baseurl=repo.baseurl,
                        enabled=True,
                    ))

            if any(repo.enabled for repo in repofile_data.data):
                produce_leapp_repofile_copy(repofile_data, repofile_name)

        # Process MariaDB options.
        elif any(mark in repofile_name for mark in MARIA_MARKERS):
            repofile_data = repofileutils.parse_repofile(full_repo_path)

            for repo in repofile_data.data:
                # Maria URLs look like this:
                # baseurl = https://archive.mariadb.org/mariadb-10.3/yum/centos/7/x86_64
                # baseurl = https://archive.mariadb.org/mariadb-10.7/yum/centos7-ppc64/
                # We want to replace the 7 in OS name after /yum/
                if repo.enabled:
                    url_parts = repo.baseurl.split('yum')
                    url_parts[1] = 'yum' + url_parts[1].replace('7', '8')
                    repo.baseurl = ''.join(url_parts)

                    api.current_logger().debug('Generating custom MariaDB repo: {}'.format(repo.repoid))
                    api.produce(CustomTargetRepository(
                        repoid=repo.repoid,
                        name=repo.name,
                        baseurl=repo.baseurl,
                        enabled=repo.enabled,
                    ))

            if any(repo.enabled for repo in repofile_data.data):
                # Since MariaDB URLs have major versions written in, we need a new repo file
                # to feed to the target userspace.
                produce_leapp_repofile_copy(repofile_data, repofile_name)

        # Process MySQL options.
        elif any(mark in repofile_name for mark in MYSQL_MARKERS):
            repofile_data = repofileutils.parse_repofile(full_repo_path)

            for repo in repofile_data.data:
                if repo.enabled:
                    # MySQL package repos don't have these versions available for EL8 anymore.
                    # There'll be nothing to upgrade to.
                    # CL repositories do provide them, though.
                    if any(ver in repo.name for ver in OLD_MYSQL_VERSIONS):
                        reporting.create_report([
                            reporting.Title('An old MySQL version will no longer be available in EL8'),
                            reporting.Summary(
                                'A yum repository for an old MySQL version is enabled on this system. '
                                'It will no longer be available on the target system. '
                                'This situation cannot be automatically resolved by Leapp. '
                                'Problematic repository: {0}'.format(repo.repoid)
                            ),
                            reporting.Severity(reporting.Severity.MEDIUM),
                            reporting.Tags([reporting.Tags.REPOSITORY]),
                            reporting.Flags([reporting.Flags.INHIBITOR]),
                            reporting.Remediation(hint=(
                                'Upgrade to a more recent MySQL version, '
                                'uninstall the deprecated MySQL packages and disable the repository, '
                                'or switch to CloudLinux MySQL Governor-provided version of MySQL to continue using '
                                'the old MySQL version.'
                                )
                            )
                        ])
                    else:
                        repo.baseurl = repo.baseurl.replace('/el/7/', '/el/8/')
                        api.current_logger().debug('Generating custom MySQL repo: {}'.format(repo.repoid))
                        api.produce(CustomTargetRepository(
                            repoid=repo.repoid,
                            name=repo.name,
                            baseurl=repo.baseurl,
                            enabled=repo.enabled,
                        ))

            if any(repo.enabled for repo in repofile_data.data):
                produce_leapp_repofile_copy(repofile_data, repofile_name)
