import os

from leapp.models import (
    InstalledMySqlTypes,
    CustomTargetRepositoryFile,
    CustomTargetRepository,
    RpmTransactionTasks,
    InstalledRPM,
    Module
)
from leapp.libraries.stdlib import api
from leapp.libraries.common import repofileutils
from leapp import reporting
from leapp.libraries.common.clmysql import get_clmysql_type, get_pkg_prefix, MODULE_STREAMS

REPO_DIR = '/etc/yum.repos.d'
TEMP_DIR = '/var/lib/leapp/yum_custom_repofiles'
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
    if not os.path.isdir(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    leapp_repofile = repo_name + LEAPP_COPY_SUFFIX
    leapp_repo_path = os.path.join(TEMP_DIR, leapp_repofile)
    if os.path.exists(leapp_repo_path):
        os.unlink(leapp_repo_path)

    api.current_logger().debug('Producing a Leapp repofile copy: {}'.format(leapp_repo_path))
    repofileutils.save_repofile(repofile_data, leapp_repo_path)
    api.produce(CustomTargetRepositoryFile(file=leapp_repo_path))


def build_install_list(prefix):
    """
    Find the installed cl-mysql packages that match the active
    cl-mysql type as per Governor config.

    :param prefix: Package name prefix to search for.
    :return: List of matching packages.
    """
    to_upgrade = []
    if prefix:
        for rpm_pkgs in api.consume(InstalledRPM):
            for pkg in rpm_pkgs.items:
                if (pkg.name.startswith(prefix)):
                    to_upgrade.append(pkg.name)
        api.current_logger().debug('cl-mysql packages to upgrade: {}'.format(to_upgrade))
    return to_upgrade


def process():
    mysql_types = []
    clmysql_type = None

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
                # cl-mysql URLs look like this:
                # baseurl=http://repo.cloudlinux.com/other/cl$releasever/mysqlmeta/cl-mariadb-10.3/$basearch/
                # We don't want any duplicate repoid entries.
                repo.repoid = repo.repoid + '-8'
                # releasever may be something like 8.6, while only 8 is acceptable.
                repo.baseurl = repo.baseurl.replace('/cl$releasever/', '/cl8/')
                # mysqlclient is usually disabled when installed from CL MySQL Governor.
                # However, it should be enabled for the Leapp upgrade, seeing as some packages
                # from it won't update otherwise.

                if repo.enabled or repo.repoid == 'mysqclient-8':
                    mysql_types.append('cloudlinux')
                    clmysql_type = get_clmysql_type()
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
                repo.repoid = repo.repoid + '-8'
                if repo.enabled:
                    mysql_types.append('mariadb')
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
                    mysql_types.append('mysql')
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
                        # URLs look like this:
                        # baseurl = https://repo.mysql.com/yum/mysql-8.0-community/el/7/x86_64/
                        repo.repoid = repo.repoid + '-8'
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

    if len(mysql_types) == 0:
        api.current_logger().debug('No installed MySQL/MariaDB detected')
    else:
        reporting.create_report([
            reporting.Title('MySQL database backup recommended'),
            reporting.Summary(
                'A MySQL/MariaDB installation has been detected on this machine. '
                'It is recommended to make a database backup before proceeding with the upgrade.'
            ),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Tags([reporting.Tags.REPOSITORY]),
        ])

        if len(mysql_types) == 1:
            api.current_logger().debug(
                "Detected MySQL/MariaDB type: {}, version: {}".format(
                    mysql_types[0], clmysql_type
                )
            )
        else:
            api.current_logger().warning('Detected multiple MySQL types: {}'.format(", ".join(mysql_types)))
            reporting.create_report([
                reporting.Title('Multpile MySQL/MariaDB versions detected'),
                reporting.Summary(
                    'Package repositories for multiple distributions of MySQL/MariaDB '
                    'were detected on the system. '
                    'Leapp will attempt to update all distributions detected. '
                    'To update only the distribution you use, disable YUM package repositories for all '
                    'other distributions. '
                    'Detected: {0}'.format(", ".join(mysql_types))
                ),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags([reporting.Tags.REPOSITORY, reporting.Tags.OS_FACTS]),
            ])

    if 'cloudlinux' in mysql_types and clmysql_type in MODULE_STREAMS.keys():
        mod_name, mod_stream = MODULE_STREAMS[clmysql_type].split(':')
        modules_to_enable = [Module(name=mod_name, stream=mod_stream)]
        pkg_prefix = get_pkg_prefix(clmysql_type)

        api.current_logger().debug('Enabling DNF module: {}:{}'.format(mod_name, mod_stream))
        api.produce(RpmTransactionTasks(
                to_upgrade=build_install_list(pkg_prefix),
                modules_to_enable=modules_to_enable
            )
        )

    api.produce(InstalledMySqlTypes(
        types=mysql_types,
        version=clmysql_type,
    ))
