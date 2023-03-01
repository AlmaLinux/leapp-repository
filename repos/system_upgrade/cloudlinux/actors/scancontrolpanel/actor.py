from leapp.actors import Actor
from leapp.models import InstalledControlPanel
from leapp.tags import FactsPhaseTag, IPUWorkflowTag

from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.common.detectcontrolpanel import detect_panel


class ScanControlPanel(Actor):
    """
    Scan for a presence of a control panel, and produce a corresponding message.
    """

    name = 'scan_control_panel'
    consumes = ()
    produces = (InstalledControlPanel,)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        detected_panel = detect_panel()

        self.produce(
            InstalledControlPanel(
                name=detected_panel
            )
        )
