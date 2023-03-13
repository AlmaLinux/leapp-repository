from leapp.actors import Actor
from leapp import reporting
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux


class CheckRhnVersionOverride(Actor):
    """
    Check if the up2date versionOverride option has not been set.
    """

    name = 'check_rhn_version_override'
    consumes = ()
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        up2date_config = '/etc/sysconfig/rhn/up2date'
        with open(up2date_config, 'r') as f:
            config_data = f.readlines()
            for line in config_data:
                if line.startswith('versionOverride=') and line != 'versionOverride=':
                    title = 'RHN up2date: versionOverride not empty'
                    summary = ('The RHN config file up2date has a set value of the versionOverride option.'
                               ' This value will get overwritten by the upgrade process, and non-supported values'
                               ' carry a risk of causing issues during the upgrade.')
                    remediation = ('Remove the versionOverride value from the up2date config file'
                                   ' before running Leapp again.')
                    reporting.create_report([
                        reporting.Title(title),
                        reporting.Summary(summary),
                        reporting.Severity(reporting.Severity.HIGH),
                        reporting.Tags([reporting.Tags.OS_FACTS]),
                        reporting.Flags([reporting.Flags.INHIBITOR]),
                        reporting.Remediation(hint=remediation),
                        reporting.RelatedResource('file', '/etc/sysconfig/rhn/up2date')
                    ])
