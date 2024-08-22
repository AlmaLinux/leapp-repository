import os

from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.models import ActiveVendorList, RepositoriesFacts
from leapp.tags import IPUWorkflowTag, FirstBootPhaseTag

VENDOR_NAME = 'microsoft'
REPO_NAME = 'packages-microsoft-com-prod'
REPO_FILE_NAME = '/etc/yum.repos.d/microsoft-prod.repo'

class CleanManualRepoFile(Actor):
    """
    If there is a repo file associated with the vendor which does not belong to
    a package, rename that repo file to disable it.
    """

    name = 'clean_manual_repo_file'
    consumes = (ActiveVendorList, RepositoriesFacts)
    produces = ()
    tags = (IPUWorkflowTag, FirstBootPhaseTag)

    def process(self):
        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:

            for repos in api.consume(RepositoriesFacts):
                for repo_file in repos.repositories:
                    if repo_file.file != REPO_FILE_NAME:
                        self._process_repo_file(repo_file)

    def _process_repo_file(self, repo_file):
        for repo in repo_file.data:
            if repo.repoid == REPO_NAME and repo.enabled:
                self._disable_repo_file(repo_file.file)

    def _disable_repo_file(self, file_path):
        api.current_logger().info('Renaming {} to disable the unmanaged {} file.')
        try:
            os.rename(file_path, file_path + '.disabled')
        except OSError as e:
            api.current_logger().warn('Could not rename {} to {}: {}'.format(e.filename, e.filename2, e.strerror))
