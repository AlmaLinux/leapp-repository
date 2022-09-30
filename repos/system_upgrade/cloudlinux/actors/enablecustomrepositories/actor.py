import os
import os.path
import shutil

from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import api
from leapp.libraries.common.config import version

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"


class EnableCustomRepositories(Actor):
    """
    On the upgraded target system, enable any present *.rpmnew repositories.
    Old repository files are renamed to *.rpmsave, as directed by RPM rules.
    """

    name = 'enable_custom_repositories'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    def rename_rpmnew(self):
        for repofile in os.listdir(REPO_ROOT_PATH):
            if repofile.endswith(".rpmnew"):
                base_filename = repofile[:-7]  # Clear ".rpmnew" from name
                new_repo_path = os.path.join(REPO_ROOT_PATH, repofile)
                base_repo_path = os.path.join(REPO_ROOT_PATH, base_filename)
                old_repo_path = os.path.join(REPO_ROOT_PATH, base_filename + ".rpmsave")

                os.rename(base_repo_path, old_repo_path)
                os.rename(new_repo_path, base_repo_path)

    def add_custom(self):
        custom_repo_dir = api.get_common_folder_path(CUSTOM_REPOS_FOLDER)

        for repofile in os.listdir(custom_repo_dir):
            full_repo_path = os.path.join(custom_repo_dir, repofile)
            shutil.copy(full_repo_path, REPO_ROOT_PATH)

    def process(self):
        if (version.current_version()[0] == "cloudlinux"):
            self.rename_rpmnew()
            self.add_custom()
