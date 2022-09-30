from leapp.actors import Actor
from leapp import reporting
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import CalledProcessError, run

import os


class CheckClLicense(Actor):
    """
    Check does the server have CL license
    """

    name = 'check_cl_license'
    consumes = ()
    produces = ()
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    system_id_path = '/etc/sysconfig/rhn/systemid'
    rhn_check_bin = '/usr/sbin/rhn_check'

    def process(self):
        res = None
        if os.path.exists(self.system_id_path):
            res = run([self.rhn_check_bin])
            self.log.debug('rhn_check result: %s', res)
        if not res or res['exit_code'] != 0 or res['stderr']:
            title = 'Server does not have active CL license'
            summary = 'Server does not have active CL license.'
            remediation = 'Activate CL license before running Leapp again.'
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.OS_FACTS]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.Remediation(hint=remediation),
            ])
