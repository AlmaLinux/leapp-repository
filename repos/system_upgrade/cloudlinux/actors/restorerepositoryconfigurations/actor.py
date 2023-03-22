from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.libraries.common import dnfconfig, mounting, repofileutils
from leapp.models import (
    RepositoriesFacts,
)
from leapp.tags import ApplicationsPhaseTag, IPUWorkflowTag


class RestoreRepositoryConfigurations(Actor):
    """
    Go over the list of repositories that were present on the pre-upgrade system and compare them to the
    current list (after the main upgrade transaction).
    If any of the repositories with same repoIDs have changed their enabled state, due to changes coming
    from RPM package updates or something else, restore their enabled settings to the pre-upgrade state.
    """

    name = 'restore_repository_configurations'
    consumes = (RepositoriesFacts)
    produces = ()
    tags = (ApplicationsPhaseTag.After, IPUWorkflowTag)

    def process(self):
        current_repofiles = repofileutils.get_parsed_repofiles()
        current_repository_list = []
        for repofile in current_repofiles:
            current_repository_list.extend(repofile.data)
        current_repodict = dict((repo.repoid, repo) for repo in current_repository_list)

        current_repoids_string = ", ".join(current_repodict.keys())
        self.log.debug("Repositories currently present on the system: {}".format(current_repoids_string))

        cmd_context = mounting.NotIsolatedActions(base_dir='/')

        for repos_facts in api.consume(RepositoriesFacts):
            for repo_file in repos_facts.repositories:
                for repo_data in repo_file.data:
                    if repo_data.repoid in current_repodict:
                        if repo_data.enabled and not current_repodict[repo_data.repoid].enabled:
                            self.log.debug("Repository {} was enabled pre-upgrade, restoring".format(repo_data.repoid))
                            dnfconfig.enable_repository(cmd_context, repo_data.repoid)
                        elif not repo_data.enabled and current_repodict[repo_data.repoid].enabled:
                            self.log.debug("Repository {} was disabled pre-upgrade, restoring".format(repo_data.repoid))
                            dnfconfig.disable_repository(cmd_context, repo_data.repoid)
