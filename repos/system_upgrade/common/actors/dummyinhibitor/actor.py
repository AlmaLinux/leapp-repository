from leapp.actors import Actor
from leapp import reporting
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

import os


class DummyInhibitor(Actor):
    """
    Raise an inhibitor report to halt the upgrade process when the test marker is present.
    """

    name = 'dummy_inhibitor'
    consumes = ()
    produces = (Report,)
    tags = (IPUWorkflowTag, ChecksPhaseTag)

    def process(self):
        if os.path.exists("/etc/leapp-simulate-inhibitor"):
            reporting.create_report([
                reporting.Title('Upgrade blocked by /etc/leapp-simulate-inhibitor'),
                reporting.Summary(
                    '/etc/leapp-simulate-inhibitor file is present, upgrade blocked by dummy_inhibitor actor.'
                ),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.SANITY]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
            ])
