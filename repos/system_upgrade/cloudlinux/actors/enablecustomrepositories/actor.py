from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.common.config import version

from leapp.libraries.actor.enablecustomrepositories import (
    rename_rpmnew,
    add_custom,
)

class EnableCustomRepositories(Actor):
    """
    On the upgraded target system, enable any present *.rpmnew repositories.
    Old repository files are renamed to *.rpmsave, as directed by RPM rules.
    """

    name = 'enable_custom_repositories'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    def process(self):
        if (version.current_version()[0] == "cloudlinux"):
            rename_rpmnew()
            add_custom()
