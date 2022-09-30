from leapp.actors import Actor
from leapp import reporting
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import CalledProcessError, run
from leapp.libraries.common.cllaunch import run_on_cloudlinux

import os


class CheckClLicense(Actor):
    """
    Check if the server has a CL license
    """

    name = 'check_cl_license'
    consumes = ()
    produces = ()
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    system_id_path = '/etc/sysconfig/rhn/systemid'
    rhn_check_bin = '/usr/sbin/rhn_check'

    @run_on_cloudlinux
    def process(self):
        res = None
        if os.path.exists(self.system_id_path):
            res = run([self.rhn_check_bin])
            self.log.debug('rhn_check result: %s', res)
        if not res or res['exit_code'] != 0 or res['stderr']:
            title = 'Server does not have an active CloudLinux license'
            summary = 'Server does not have an active CloudLinux license. This renders key CloudLinux packages ' \
                      'inaccessible, inhibiting the upgrade process.'
            remediation = 'Activate a CloudLinux license on this machine before running Leapp again.'
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.OS_FACTS]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.Remediation(hint=remediation),
            ])
