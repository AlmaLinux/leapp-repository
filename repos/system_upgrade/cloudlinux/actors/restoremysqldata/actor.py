import os
from leapp.actors import Actor
from leapp.tags import ThirdPartyApplicationsPhase, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.backup import backup_file, CLSQL_BACKUP_FILES


class RestoreMySqlData(Actor):
    """
    Restore cl-mysql configuration data from an external folder.
    """

    name = 'restore_my_sql_data'
    consumes = ()
    produces = ()
    tags = (ThirdPartyApplicationsPhase, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        for filename in CLSQL_BACKUP_FILES:
            if os.path.isfile(filename):
                backup_file(filename, os.path.basename(filename))
