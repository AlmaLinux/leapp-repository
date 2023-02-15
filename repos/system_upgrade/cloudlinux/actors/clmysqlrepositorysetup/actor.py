from leapp.actors import Actor
from leapp.libraries.actor import clmysqlrepositorysetup
from leapp.models import (
    CustomTargetRepository,
    CustomTargetRepositoryFile
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux


class ClMysqlRepositorySetup(Actor):
    """
    No documentation has been provided for the cl_mysql_repository_setup actor.
    """

    name = 'cl_mysql_repository_setup'
    consumes = ()
    produces = (CustomTargetRepository, CustomTargetRepositoryFile, Report)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        clmysqlrepositorysetup.process()
