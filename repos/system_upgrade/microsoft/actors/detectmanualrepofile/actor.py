from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.models import RpmTransactionTasks, InstalledRPM, ActiveVendorList
from leapp.tags import IPUWorkflowTag, FactsPhaseTag
from leapp.libraries.common.rpms import has_package

VENDOR_NAME = 'microsoft'
REPO_PKG_NAME = 'packages-microsoft-prod'

class DetectManualRepoFile(Actor):
    """
    If the vendor is active, but the repo file used for this process isn't the
    one owned by a package in the repo itself, install that package at the
    appropriate time.
    """

    name = 'detect_manual_repo_file'
    consumes = (ActiveVendorList, InstalledRPM)
    produces = (RpmTransactionTasks,)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):

        active_vendors = []
        for vendor_list in api.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        if VENDOR_NAME in active_vendors:
            api.current_logger().info('Vendor {} is active. Looking for information...'.format(VENDOR_NAME))

            if has_package(InstalledRPM, REPO_PKG_NAME):
                api.current_logger().info(
                    'Package {} is installed: vendor will upgrade this to point DNF to the correct repo.'.format(
                        REPO_PKG_NAME
                    )
                )
            else:
                api.current_logger().info(
                    'Package {} is not installed: requesting installation.'.format(REPO_PKG_NAME)
                )
                api.produce(RpmTransactionTasks(to_install=[REPO_PKG_NAME,]))
