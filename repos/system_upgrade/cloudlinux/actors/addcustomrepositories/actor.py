from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp.libraries.actor.addcustomrepositories import add_custom


class AddCustomRepositories(Actor):
    """
    Move the files inside the custom-repos folder of this leapp repository into the /etc/yum.repos.d repository.
    """

    name = 'add_custom_repositories'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    @run_on_cloudlinux
    def process(self):
        # We only want to run this actor on CloudLinux systems.
        # current_version returns a tuple (release_name, version_value).
        add_custom(self.log)
