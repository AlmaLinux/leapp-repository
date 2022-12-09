import os

from leapp.actors import Actor
from leapp.models import VendorSignatures, ActiveVendorList
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


VENDORS_DIR = "/etc/leapp/files/vendors.d/"
SIGFILE_SUFFIX = ".sigs"


class VendorRepoSignatureScanner(Actor):
    """
    Produce VendorSignatures messages for the vendor signature files inside the
    <VENDORS_DIR>.
    These messages are used to extend the list of pakcages Leapp will consider
    signed and will attempt to upgrade.

    The messages are produced only if a "from" vendor repository
    listed indide its map matched one of the repositories active on the system.
    """

    name = 'vendor_repo_signature_scanner'
    consumes = (ActiveVendorList)
    produces = (VendorSignatures)
    tags = (IPUWorkflowTag, FactsPhaseTag.Before)

    def process(self):
        if not os.path.isdir(VENDORS_DIR):
            self.log.debug(
                "The {} directory doesn't exist. Nothing to do.".format(VENDORS_DIR)
            )
            return

        for sigfile_name in os.listdir(VENDORS_DIR):
            if not sigfile_name.endswith(SIGFILE_SUFFIX):
                continue
            # Cut the suffix part to get only the name.
            vendor_name = sigfile_name[:-5]

            active_vendors = []
            for vendor_list in self.consume(ActiveVendorList):
                active_vendors.extend(vendor_list.data)

            self.log.debug(
                "Active vendor list: {}".format(active_vendors)
            )

            if vendor_name not in active_vendors:
                self.log.debug(
                    "Vendor {} not in active list, skipping".format(vendor_name)
                )
                continue

            self.log.debug(
                "Vendor {} found in active list, processing file".format(vendor_name)
            )

            full_sigfile_path = os.path.join(VENDORS_DIR, sigfile_name)
            with open(full_sigfile_path) as f:
                signatures = [line for line in f.read().splitlines() if line]

            self.produce(
                VendorSignatures(
                    vendor=vendor_name,
                    sigs=signatures,
                )
            )

        self.log.info(
            "The {} directory exists, vendor signatures loaded.".format(VENDORS_DIR)
        )
