import os
from leapp.actors import Actor
from leapp.tags import InterimPreparationPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.backup import backup_file, CLSQL_BACKUP_FILES


class BackupMySqlData(Actor):
    """
    Backup cl-mysql configuration data to an external folder.
    """

    name = 'backup_my_sql_data'
    consumes = ()
    produces = ()
    tags = (InterimPreparationPhaseTag.Before, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        for filename in CLSQL_BACKUP_FILES:
            if os.path.isfile(filename):
                backup_file(filename, os.path.basename(filename))
