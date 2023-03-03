from leapp.actors import Actor
from leapp import reporting
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

from leapp.libraries.actor.detectwebservers import (
    detect_litespeed,
    detect_nginx
)


class DetectWebServers(Actor):
    """
    Check for a presence of a web server, and produce a warning if one is installed.
    """

    name = 'detect_web_servers'
    consumes = ()
    produces = (Report)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    def process(self):
        litespeed_installed = detect_litespeed()
        nginx_installed = detect_nginx()

        if litespeed_installed or nginx_installed:
            server_name = "NGINX" if nginx_installed else "LiteSpeed"
            reporting.create_report(
                [
                    reporting.Title(
                        "An installed web server might not be upgraded properly."
                    ),
                    reporting.Summary(
                        "A web server is present on the system."
                        " Depending on the source of installation, "
                        " it may not upgrade to the new version correctly,"
                        " since not all varoants are currently supported by Leapp."
                        " Please check the list of packages that won't be upgraded in the report."
                        " Alternatively, upgrade the webserver manually after the process finishes."
                        " Detected webserver: {}.".format(server_name)
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags([
                        reporting.Tags.OS_FACTS,
                        reporting.Tags.SERVICES
                    ]),
                ]
            )
