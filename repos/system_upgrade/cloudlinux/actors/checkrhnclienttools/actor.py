from leapp.actors import Actor
from leapp import reporting
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux

from leapp.libraries.actor.version import (
    Version, VersionParsingError,
)

import subprocess


class CheckRhnClientToolsVersion(Actor):
    """
    Check the rhn-client-tools package version
    """

    name = 'check_rhn_client_tools_version'
    consumes = ()
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    minimal_version = Version('2.0.2')
    minimal_release_int = 43
    minimal_release = '%s.el7.cloudlinux' % minimal_release_int

    @run_on_cloudlinux
    def process(self):
        title, summary, remediation = None, None, None
        # ex:
        #   Version      : 2.0.2
        #   Release      : 43.el7.cloudlinux
        # res is: b'2.0.2\n43.el7.cloudlinux\n'
        cmd = "yum info installed rhn-client-tools | grep '^Version' -A 1 | awk '{print $3}'"
        res = subprocess.check_output(cmd, shell=True)
        rhn_version, rhn_release = res.decode().split()
        self.log.info('Current rhn-client-tools version: "%s"', rhn_version)
        try:
            current_version = Version(rhn_version)
        except VersionParsingError:
            title = 'rhn-client-tools: package is not installed'
            summary = 'rhn-client-tools package is required to perform elevation.'
            remediation = 'Install rhn-client-tools "%s" version before running Leapp again.' % self.minimal_version
        else:
            if current_version < self.minimal_version or int(rhn_release.split('.')[0]) < self.minimal_release_int:
                title = 'rhn-client-tools: package version is too low'
                summary = 'Current version of the rhn-client-tools package has no capability to perform elevation.'
                remediation = 'Update rhn-client-tools to "%s %s" version before running Leapp again.' % (self.minimal_version, self.minimal_release)
        if title:
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.OS_FACTS]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
                reporting.Remediation(hint=remediation),
            ])
