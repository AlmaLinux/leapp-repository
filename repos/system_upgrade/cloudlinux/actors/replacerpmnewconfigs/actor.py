from __future__ import print_function
import os
import fileinput

from leapp.actors import Actor
from leapp.tags import ApplicationsPhaseTag, IPUWorkflowTag
from leapp import reporting
from leapp.reporting import Report
from leapp.libraries.common.cllaunch import run_on_cloudlinux

REPO_DIR = '/etc/yum.repos.d'
REPO_DELETE_MARKERS = ['cloudlinux', 'imunify', 'epel']
REPO_BACKUP_MARKERS = []
RPMNEW = '.rpmnew'
LEAPP_BACKUP_SUFFIX = '.leapp-backup'


class ReplaceRpmnewConfigs(Actor):
    """
    Replace CloudLinux-related repository config .rpmnew files.
    """

    name = 'replace_rpmnew_configs'
    consumes = ()
    produces = (Report,)
    tags = (ApplicationsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        deleted_repofiles = []
        renamed_repofiles = []

        for reponame in os.listdir(REPO_DIR):
            if any(mark in reponame for mark in REPO_DELETE_MARKERS) and RPMNEW in reponame:
                base_reponame = reponame[:-len(RPMNEW)]
                base_path = os.path.join(REPO_DIR, base_reponame)
                new_file_path = os.path.join(REPO_DIR, reponame)

                os.unlink(base_path)
                os.rename(new_file_path, base_path)
                deleted_repofiles.append(base_reponame)
                self.log.debug('Yum repofile replaced: {}'.format(base_path))

            if any(mark in reponame for mark in REPO_BACKUP_MARKERS) and RPMNEW in reponame:
                base_reponame = reponame[:-len(RPMNEW)]
                base_path = os.path.join(REPO_DIR, base_reponame)
                new_file_path = os.path.join(REPO_DIR, reponame)
                backup_path = os.path.join(REPO_DIR, base_reponame + LEAPP_BACKUP_SUFFIX)

                os.rename(base_path, backup_path)
                os.rename(new_file_path, base_path)
                renamed_repofiles.append(base_reponame)
                self.log.debug('Yum repofile replaced with backup: {}'.format(base_path))

        # Disable any old repositories.
        for reponame in os.listdir(REPO_DIR):
            if LEAPP_BACKUP_SUFFIX in reponame:
                repofile_path = os.path.join(REPO_DIR, reponame)
                for line in fileinput.input(repofile_path, inplace=True):
                    if line.startswith('enabled'):
                        print("enabled = 0")
                    else:
                        print(line, end='')

        if renamed_repofiles:
            deleted_string = '\n'.join(['- {}'.format(repofile_name) for repofile_name in deleted_repofiles])
            replaced_string = '\n'.join(['- {}'.format(repofile_name) for repofile_name in renamed_repofiles])
            reporting.create_report([
                reporting.Title('CloudLinux repository config files replaced by updated versions'),
                reporting.Summary(
                    'One or more RPM repository configuration files '
                    'have been replaced with new versions provided by the upgraded packages. '
                    'Any manual modifications to these files have been overriden by this process. '
                    'Old versions of backed up files are contained in files with a naming pattern '
                    '<repository_file_name>.leapp-backup. '
                    'Deleted repository files: \n{} '
                    'Backed up repository files: \n{}'.format(deleted_string, replaced_string)
                ),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags([reporting.Tags.UPGRADE_PROCESS])
            ])
