from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.common.config import version

from leapp.libraries.actor.enablerpmnewfiles import (
    rename_rpmnew,
)

class EnableRpmnewFiles(Actor):
    """
    On the upgraded target system, enable any present *.rpmnew repositories.
    Old repository files are renamed to *.rpmsave, as directed by RPM rules.
    """

    name = 'enable_rpmnew_files'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    def process(self):
        # We only want to run this actor on CloudLinux systems.
        # current_version returns a tuple (release_name, version_value).
        if (version.current_version()[0] == "cloudlinux"):
            rename_rpmnew()
