from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.models import (
    RepositoriesFacts,
    VendorSourceRepos,
    ActiveVendorList,
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


class CheckEnabledVendorRepos(Actor):
    """
    Create a list of vendors whose repositories are present on the system and enabled.
    Only those vendors' configurations (new repositories, PES actions, etc.)
    will be included in the upgrade process.
    """

    name = "check_enabled_vendor_repos"
    consumes = (RepositoriesFacts, VendorSourceRepos)
    produces = (ActiveVendorList)
    tags = (IPUWorkflowTag, FactsPhaseTag.Before)

    def process(self):
        vendor_mapping_data = {}
        active_vendors = set()

        # Make a dict for easy mapping of repoid -> corresponding vendor name.
        for vendor_src_repodata in api.consume(VendorSourceRepos):
            for vendor_src_repo in vendor_src_repodata.source_repoids:
                vendor_mapping_data[vendor_src_repo] = vendor_src_repodata.vendor

        # Is the repo listed in the vendor map as from_repoid present on the system?
        for repos_facts in api.consume(RepositoriesFacts):
            for repo_file in repos_facts.repositories:
                for repo_data in repo_file.data:
                    self.log.debug(
                        "Looking for repository {} in vendor maps".format(repo_data.repoid)
                    )
                    if repo_data.enabled and repo_data.repoid in vendor_mapping_data:
                        # If the vendor's repository is present in the system and enabled, count the vendor as active.
                        new_vendor = vendor_mapping_data[repo_data.repoid]
                        self.log.debug(
                            "Repository {} found and enabled, enabling vendor {}".format(
                                repo_data.repoid, new_vendor
                            )
                        )
                        active_vendors.add(new_vendor)

        if active_vendors:
            self.log.debug("Active vendor list: {}".format(active_vendors))
            api.produce(ActiveVendorList(data=list(active_vendors)))
        else:
            self.log.info("No active vendors found, vendor list not generated")
