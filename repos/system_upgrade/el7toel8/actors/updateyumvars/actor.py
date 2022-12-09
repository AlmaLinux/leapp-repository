from leapp.actors import Actor
from leapp.libraries.actor import updateyumvars
from leapp.tags import ThirdPartyApplicationsPhaseTag, IPUWorkflowTag


class UpdateYumVars(Actor):
    """
    Update the files corresponding to the current major
    OS version in the /etc/yum/vars folder.
    """

    name = 'update_yum_vars'
    consumes = ()
    produces = ()
    tags = (ThirdPartyApplicationsPhaseTag, IPUWorkflowTag)

    def process(self):
        updateyumvars.vars_update()
