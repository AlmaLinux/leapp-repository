import os
import os.path

from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag


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
        root_path = "/etc/yum.repos.d"
        for repofile in os.listdir(root_path):
            if repofile.endswith(".rpmnew"):
                base_filename = repofile[:-7]  # Clear ".rpmnew" from name
                new_repo_path = os.path.join(root_path, repofile)
                base_repo_path = os.path.join(root_path, base_filename)
                old_repo_path = os.path.join(root_path, base_filename + ".rpmsave")

                os.rename(base_repo_path, old_repo_path)
                os.rename(new_repo_path, base_repo_path)
