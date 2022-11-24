from leapp.actors import Actor
from leapp.libraries.actor import scanrolloutrepositories
from leapp.models import (
    CustomTargetRepositoryFile,
    CustomTargetRepository,
    UsedRepositories
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


class ScanRolloutRepositories(Actor):
    """
    Scan for repository files associated with the Gradual Rollout System.

    Normally these repositories aren't included into the upgrade, but if one of
    the packages on the system was installed from them, we can potentially run
    into problems if ignoring these.

    Only those repositories that had packages installed from them are included.
    """

    name = 'scan_rollout_repositories'
    consumes = (UsedRepositories)
    produces = (CustomTargetRepositoryFile, CustomTargetRepository)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    def process(self):
        scanrolloutrepositories.process()
