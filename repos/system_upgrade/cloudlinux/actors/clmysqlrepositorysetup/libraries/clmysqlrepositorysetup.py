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
CL_MARKERS = ['cl-mysql', 'cl-mariadb', 'cl-percona']
MARIA_MARKERS = ['MariaDB']
MYSQL_MARKERS = ['mysql-community']
OLD_MYSQL_VERSIONS = ['5.7', '5.6', '5.5']


def produce_leapp_repo(repofile_data, repo_name):
    leapp_repofile = repo_name + '_leapp.repo'
    leapp_repo_path = os.path.join(REPO_DIR, leapp_repofile)
    repofileutils.save_repofile(repofile_data, leapp_repo_path)
    api.produce(CustomTargetRepositoryFile(file=leapp_repo_path))


def process():
    for repofile_full in os.listdir(REPO_DIR):
        if not repofile_full.endswith(REPOFILE_SUFFIX):
            continue
        # Cut the .repo part to get only the name.
        repofile_name = repofile_full[:-5]
        full_repo_path = os.path.join(REPO_DIR, repofile_full)

        # Parse any repository files that may have something to do with MySQL or MariaDB.

        # Process CL-provided options.
        if any(mark in repofile_name for mark in CL_MARKERS):
            repofile_data = repofileutils.parse_repofile(full_repo_path)

            # Were any repositories enabled?
            for repo in repofile_data.data:
                # mysqlclient is usually disabled when installed from CL MySQL Governor.
                # However, it should be enabled for the Leapp upgrade, seeing as some packages
                # from it won't update otherwise.
                if repo.enabled or repo.repoid == 'mysqclient':
                    api.produce(CustomTargetRepository(
                        repoid=repo.repoid,
                        name=repo.name,
                        baseurl=repo.baseurl,
                        enabled=True,
                    ))

            # CL MySQL repositories use URLs with $releasever patterns.
            # We can directly provide them to the target userspace creator, no need to modify.
            if any(repo.enabled for repo in repofile_data.data):
                api.produce(CustomTargetRepositoryFile(file=full_repo_path))

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

                    api.produce(CustomTargetRepository(
                        repoid=repo.repoid,
                        name=repo.name,
                        baseurl=repo.baseurl,
                        enabled=repo.enabled,
                    ))

            if any(repo.enabled for repo in repofile_data.data):
                # Since MariaDB URLs have major versions written in, we need a new repo file
                # to feed to the target userspace.
                produce_leapp_repo(repofile_data, repofile_name)

        # Process MySQL options.
        elif any(mark in repofile_name for mark in MYSQL_MARKERS):
            repofile_data = repofileutils.parse_repofile(full_repo_path)

            for repo in repofile_data.data:
                if repo.enabled:
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
                        api.produce(CustomTargetRepository(
                            repoid=repo.repoid,
                            name=repo.name,
                            baseurl=repo.baseurl,
                            enabled=repo.enabled,
                        ))

            if any(repo.enabled for repo in repofile_data.data):
                produce_leapp_repo(repofile_data, repofile_name)
