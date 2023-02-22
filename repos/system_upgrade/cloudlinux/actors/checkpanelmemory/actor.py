from leapp.actors import Actor
from leapp.libraries.actor import checkpanelmemory
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.models import MemoryInfo, InstalledControlPanel, Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag


class CheckPanelMemory(Actor):
    """
    Check if the system has enough memory for the corresponding panel.
    """

    name = 'check_panel_memory'
    consumes = (MemoryInfo, InstalledControlPanel,)
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        checkpanelmemory.process()
