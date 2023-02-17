from leapp import reporting
from leapp.actors import Actor
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.actor.detectcontrolpanel import (
    detect_panel,
    UNKNOWN_NAME,
    INTEGRATED_NAME,
    CPANEL_NAME,
)


class DetectControlPanel(Actor):
    """
    Check for a presence of a control panel, and inhibit the upgrade if an unsupported one is found.
    """

    name = "detect_control_panel"
    consumes = ()
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        panel = detect_panel()

        if panel == CPANEL_NAME:
            self.log.debug('cPanel detected, upgrade proceeding')
        elif panel == INTEGRATED_NAME or panel == UNKNOWN_NAME:
            self.log.debug('Integrated/no panel detected, upgrade proceeding')
        elif panel:
            summary_info = "Detected panel: {}".format(panel)
            # Block the upgrade on any systems with a panel detected.
            reporting.create_report(
                [
                    reporting.Title(
                        "The upgrade process should not be run on systems with a control panel present."
                    ),
                    reporting.Summary(
                        "Systems with a control panel present are not supported at the moment."
                        " No control panels are currently included in the Leapp database, which"
                        " makes loss of functionality after the upgrade extremely likely."
                        " {}.".format(summary_info)
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags([reporting.Tags.OS_FACTS]),
                    reporting.Flags([reporting.Flags.INHIBITOR]),
                ]
            )
