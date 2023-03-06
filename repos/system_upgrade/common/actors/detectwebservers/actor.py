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
                        "A NGINX/LiteSpeed web server is present on the system."
                        " Depending on the source of installation, "
                        " it may not upgrade to the new version correctly,"
                        " since not all installation configurations are currently supported by Leapp."
                        " Failing to upgrade the webserver may result in it malfunctioning"
                        " after the upgrade process finishes."
                        " Please review the list of packages that won't be upgraded in the report."
                        " If the web server packages are present in the list of packages that won't be upgraded,"
                        " expect the server to be non-functional on the post-upgrade system."
                        " You may still continue with the upgrade, but you'll need to"
                        " upgrade the web server manually after the process finishes."
                        " Detected webserver: {}.".format(server_name)
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags([
                        reporting.Tags.OS_FACTS,
                        reporting.Tags.SERVICES
                    ]),
                ]
            )
