import os
import os.path

from leapp.actors import Actor
from leapp.libraries.actor.pes_event_parsing import get_pes_events
from leapp.libraries.actor.pes_events_scanner import process
from leapp.models import (
    EnabledModules,
    InstalledRedHatSignedRPM,
    PESRpmTransactionTasks,
    RepositoriesBlacklisted,
    RepositoriesFacts,
    RepositoriesMapping,
    RepositoriesSetupTasks,
    RHUIInfo,
    RpmTransactionTasks,
    ActiveVendorList
)
from leapp.reporting import Report
from leapp.tags import FactsPhaseTag, IPUWorkflowTag

LEAPP_FILES_DIR = "/etc/leapp/files"
PES_FILE_NAME = 'pes-events.json'
VENDORS_DIR = "/etc/leapp/files/vendors.d"


class PesEventsScanner(Actor):
    """
    Provides data about package events from Package Evolution Service.

    After collecting data from a provided JSON file containing Package Evolution Service events, a
    message with relevant data will be produced to help DNF Upgrade transaction calculation.
    """

    name = 'pes_events_scanner'
    consumes = (
        EnabledModules,
        InstalledRedHatSignedRPM,
        RepositoriesBlacklisted,
        RepositoriesFacts,
        RepositoriesMapping,
        RHUIInfo,
        RpmTransactionTasks,
        ActiveVendorList,
    )
    produces = (PESRpmTransactionTasks, RepositoriesSetupTasks, Report)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        events = get_pes_events(LEAPP_FILES_DIR, PES_FILE_NAME)

        active_vendors = []
        for vendor_list in self.consume(ActiveVendorList):
            active_vendors.extend(vendor_list.data)

        pes_json_suffix = "_pes.json"
        if os.path.isdir(VENDORS_DIR):
            vendor_pesfiles = list(filter(lambda vfile: pes_json_suffix in vfile, os.listdir(VENDORS_DIR)))

            for pesfile in vendor_pesfiles:
                if pesfile[:-len(pes_json_suffix)] in active_vendors:
                    events.extend(get_pes_events(VENDORS_DIR, PES_FILE_NAME))

        process(events)
