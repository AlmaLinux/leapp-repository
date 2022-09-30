from leapp.actors import Actor
from leapp import reporting
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

from packaging import version
import subprocess


class CheckRhnClientToolsVersion(Actor):
    """
    Check the rhn-client-tools package version
    """

    name = 'check_rhn_client_tools_version'
    consumes = ()
    produces = ()
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    minimal_version = version.parse('2.8.16')     # FIXME: actual patch is not released yet; should be 2.8.17 i guess

    def process(self):
        title, summary, remediation = None, None, None
        # ex: Version      : 2.8.16
        cmd = "yum info --installed rhn-client-tools | grep '^Version' | awk '{print $3}'"
        res = subprocess.call(cmd, shell=True, text=True)
        if not res:
            title = 'rhn-client-tools: package is not installed'
            summary = 'rhn-client-tools package is required to perform elevation.'
            remediation = 'Install rhn-client-tools "%s" version before running Leapp again.' % self.minimal_version
        elif version.parse(res) <= self.minimal_version:
            title = 'rhn-client-tools: package version is too low'
            summary = 'Current version of the rhn-client-tools package has no capability to perform elevation.'
            remediation = 'Update rhn-client-tools to "%s" version before running Leapp again.' % self.minimal_version
        if title:
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.OS_FACTS]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.Remediation(hint=remediation),
            ])
