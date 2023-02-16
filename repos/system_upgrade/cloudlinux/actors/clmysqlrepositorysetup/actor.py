from leapp.actors import Actor
from leapp.reporting import Report
from leapp.libraries.actor import clmysqlrepositorysetup
from leapp.models import (
    CustomTargetRepository,
    CustomTargetRepositoryFile,
    Report
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux


class ClMysqlRepositorySetup(Actor):
    """
    Gather data on what MySQL/MariaDB variant is installed on the system, if any.
    Then prepare the custom repository data and the corresponding file
    to be sent to the target environment creator.
    """

    name = 'cl_mysql_repository_setup'
    consumes = ()
    produces = (CustomTargetRepository, CustomTargetRepositoryFile, Report)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        clmysqlrepositorysetup.process()
