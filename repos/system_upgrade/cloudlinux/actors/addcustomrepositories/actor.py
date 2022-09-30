from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.common.config import version

from leapp.libraries.actor.addcustomrepositories import (
    add_custom,
)


class AddCustomRepositories(Actor):
    """
    Move the files inside the custom-repos folder of this leapp repository into the /etc/yum.repos.d repository.
    """

    name = 'add_custom_repositories'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    def process(self):
        # We only want to run this actor on CloudLinux systems.
        # current_version returns a tuple (release_name, version_value).
        if (version.current_version()[0] == "cloudlinux"):
            self.log.debug("CloudLinux OS detected, {} executing".format(self.name))
            add_custom(self.log)
