import os
from leapp.actors import Actor
from leapp import reporting
from leapp.models import Report
from leapp.tags import ThirdPartyApplicationsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.backup import restore_file, CLSQL_BACKUP_FILES, BACKUP_DIR


class RestoreMySqlData(Actor):
    """
    Restore cl-mysql configuration data from an external folder.
    """

    name = 'restore_my_sql_data'
    consumes = ()
    produces = (Report,)
    tags = (ThirdPartyApplicationsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        failed_files = []

        for filepath in CLSQL_BACKUP_FILES:
            try:
                restore_file(os.path.basename(filepath), filepath)
            except OSError as e:
                failed_files.append(filepath)
                self.log.error('Could not restore file {}: {}'.format(filepath, e.strerror))

        if failed_files:
            title = "Failed to restore backed up configuration files"
            summary = (
                "Some backed up configuration files were unable to be restored automatically."
                " Please check the upgrade log for detailed error descriptions"
                " and restore the files from the backup directory {} manually if needed."
                " Files not restored: {}".format(BACKUP_DIR, failed_files)
            )
            reporting.create_report(
                [
                    reporting.Title(title),
                    reporting.Summary(summary),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags([reporting.Tags.UPGRADE_PROCESS]),
                ]
            )
