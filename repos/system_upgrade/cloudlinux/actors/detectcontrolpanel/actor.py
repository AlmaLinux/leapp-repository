from leapp.actors import Actor
from leapp import reporting
from leapp.reporting import Report
from leapp.models import InstalledControlPanel
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
from leapp.exceptions import StopActorExecutionError

from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.detectcontrolpanel import (
    UNKNOWN_NAME,
    INTEGRATED_NAME,
    CPANEL_NAME,
)


class DetectControlPanel(Actor):
    """
    Inhibit the upgrade if an unsupported control panel is found.
    """

    name = "detect_control_panel"
    consumes = (InstalledControlPanel)
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        panel = next(self.consume(InstalledControlPanel), None)
        if panel is None:
            raise StopActorExecutionError(message=("Missing information about the installed web panel."))

        if panel == CPANEL_NAME:
            self.log.debug('cPanel detected, upgrade proceeding')
        elif panel == INTEGRATED_NAME or panel == UNKNOWN_NAME:
            self.log.debug('Integrated/no panel detected, upgrade proceeding')
        elif panel:
            # Block the upgrade on any systems with a non-supported panel detected.
            reporting.create_report(
                [
                    reporting.Title(
                        "The upgrade process should not be run on systems with a control panel present."
                    ),
                    reporting.Summary(
                        "Systems with a control panel present are not supported at the moment."
                        " No control panels are currently included in the Leapp database, which"
                        " makes loss of functionality after the upgrade extremely likely."
                        " Detected panel: {}.".format(panel)
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags([reporting.Tags.OS_FACTS]),
                    reporting.Flags([reporting.Flags.INHIBITOR]),
                ]
            )
