from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.tags import DownloadPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import CalledProcessError, run
from leapp.libraries.common.cllaunch import run_on_cloudlinux
from leapp import reporting


class SwitchClnChannel(Actor):
    """
    Switch CLN channel from 7 to 8 to be able to download upgrade packages
    """

    name = "switch_cln_channel"
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, DownloadPhaseTag.Before)

    switch_bin = "/usr/sbin/cln-switch-channel"

    @run_on_cloudlinux
    def process(self):
        switch_cmd = [self.switch_bin, "-t", "8", "-o", "-f"]
        yum_clean_cmd = ["yum", "clean", "all"]
        update_release_cmd = ["yum", "update", "-y", "cloudlinux-release"]
        try:
            res = run(switch_cmd)
            self.log.debug('Command "%s" result: %s', switch_cmd, res)
            res = run(yum_clean_cmd)  # required to update the repolist
            self.log.debug('Command "%s" result: %s', yum_clean_cmd, res)
            res = run(update_release_cmd)
            self.log.debug('Command "%s" result: %s', update_release_cmd, res)
        except CalledProcessError as e:
            reporting.create_report(
                [
                    reporting.Title(
                        "Failed to switch CloudLinux Network channel from 7 to 8."
                    ),
                    reporting.Summary(
                        "Command {} failed with exit code {}."
                        " The most probable cause of that is a problem with this system's"
                        " CloudLinux Network registration.".format(e.command, e.exit_code)
                    ),
                    reporting.Remediation(
                        hint="Check the state of this system's registration with \'rhn_check\'."
                        " Attempt to re-register the system with \'rhnreg_ks --force\'."
                    ),
                    reporting.Severity(reporting.Severity.HIGH),
                    reporting.Tags(
                        [reporting.Tags.OS_FACTS, reporting.Tags.AUTHENTICATION]
                    ),
                    reporting.Flags([reporting.Flags.INHIBITOR]),
                ]
            )
        except OSError as e:
            api.current_logger().error(
                "Could not call RHN command: Message: %s", str(e), exc_info=True
            )
