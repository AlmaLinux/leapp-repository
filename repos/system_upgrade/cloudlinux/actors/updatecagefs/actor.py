import os

from leapp.actors import Actor
from leapp.libraries.stdlib import run, CalledProcessError
from leapp.reporting import Report, create_report
from leapp import reporting
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.common.config import version


class UpdateCagefs(Actor):
    """
    Force update of cagefs.

    cagefs should reflect massive changes in system made in previous phases
    """

    name = 'update_cagefs'
    consumes = ()
    produces = ()
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    def process(self):
        if (version.current_version()[0] != "cloudlinux"):
            return
        if os.path.exists('/usr/sbin/cagefsctl'):
            try:
                run(['/usr/sbin/cagefsctl', '--force-update'], checked=True)
                self.log.info('cagefs update was successful')
            except CalledProcessError as e:
                # cagefsctl prints errors in stdout
                self.log.error(e.stdout)
                self.log.error('Command "cagefsctl --force-update" finished with exit code {}, '
                    'the filesystem inside cagefs may be out-of-date.\n'
                    'Check cagefsctl output above and in /var/log/cagefs-update.log, '
                    'rerun "cagefsctl --force-update" after fixing the issues.'.format(e.exit_code)
                )
