import os
import os.path

from leapp.actors import Actor
from leapp.libraries.actor.peseventsscanner import pes_events_scanner
from leapp.models import (
    InstalledRedHatSignedRPM,
    PESRpmTransactionTasks,
    RepositoriesMap,
    RepositoriesBlacklisted,
    RepositoriesSetupTasks,
    RpmTransactionTasks,
    ActiveVendorList,
)
from leapp.reporting import Report
from leapp.tags import FactsPhaseTag, IPUWorkflowTag

LEAPP_FILES_DIR = "/etc/leapp/files"
VENDORS_DIR = "/etc/leapp/files/vendors.d"


class PesEventsScanner(Actor):
    """
    Provides data about packages events from Package Evolution Service.

    After collecting data from a provided JSON file containing Package Evolution Service events, a
    message with relevant data will be produced to help DNF Upgrade transaction calculation.
    """

    name = "pes_events_scanner"
    consumes = (
        InstalledRedHatSignedRPM,
        RepositoriesBlacklisted,
        RepositoriesMap,
        RpmTransactionTasks,
        ActiveVendorList,
    )
    produces = (PESRpmTransactionTasks, RepositoriesSetupTasks, Report)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        pes_events_scanner(LEAPP_FILES_DIR, "pes-events.json")

        vendor_list = next(self.consume(ActiveVendorList), None)
        if os.path.isdir(VENDORS_DIR):
            vendor_pesfiles = list(filter(lambda vfile: ".json" in vfile, os.listdir(VENDORS_DIR)))

            for pesfile in vendor_pesfiles:
                if pesfile[:-5] in vendor_list:
                    pes_events_scanner(VENDORS_DIR, pesfile)
