import os
import shutil
from leapp.libraries.stdlib import api

CLSQL_BACKUP_FILES = [
    "/etc/container/dbuser-map",
    "/etc/container/ve.cfg",
    "/etc/container/mysql-governor.xml",
    "/etc/container/governor_package_limit.json"
]

BACKUP_DIR = "/var/lib/leapp/cl_backup"


def backup_file(source, destination, backup_directory=None):
    # type: (str, str, str) -> None
    """
    Backup file to a backup directory.

    :param source: Path of the file to backup.
    :param destination: Destination name of a file in the backup directory.
    :param dir: Backup directory override, defaults to None
    """
    if not backup_directory:
        backup_directory = BACKUP_DIR
    if not os.path.isdir(backup_directory):
        os.makedirs(backup_directory)

    dest_path = os.path.join(backup_directory, destination)

    api.current_logger().debug('Backing up file: {} to {}'.format(source, dest_path))
    shutil.copy(source, dest_path)


def restore_file(source, destination, backup_directory=None):
    # type: (str, str, str) -> None
    """
    Restore file from a backup directory.

    :param source: Name of a file in the backup directory.
    :param destination: Destination path to restore the file to.
    :param dir: Backup directory override, defaults to None
    """
    if not backup_directory:
        backup_directory = BACKUP_DIR
    src_path = os.path.join(backup_directory, source)

    api.current_logger().debug('Restoring file: {} to {}'.format(src_path, destination))
    shutil.copy(src_path, destination)
