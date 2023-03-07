import os
from leapp.actors import Actor
from leapp.tags import ThirdPartyApplicationsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.backup import restore_file, CLSQL_BACKUP_FILES


class RestoreMySqlData(Actor):
    """
    Restore cl-mysql configuration data from an external folder.
    """

    name = 'restore_my_sql_data'
    consumes = ()
    produces = ()
    tags = (ThirdPartyApplicationsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        for filename in CLSQL_BACKUP_FILES:
            if os.path.isfile(filename):
                restore_file(filename, os.path.basename(filename))
