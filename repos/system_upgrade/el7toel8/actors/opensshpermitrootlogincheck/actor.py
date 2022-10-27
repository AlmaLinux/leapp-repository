from leapp import reporting
from leapp.actors import Actor
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.actor.opensshpermitrootlogincheck import semantics_changes, add_permitrootlogin_conf
from leapp.libraries.stdlib import api
from leapp.models import OpenSshConfig, Report
from leapp.reporting import create_report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

COMMON_REPORT_TAGS = [
    reporting.Tags.AUTHENTICATION,
    reporting.Tags.SECURITY,
    reporting.Tags.NETWORK,
    reporting.Tags.SERVICES
]


class OpenSshPermitRootLoginCheck(Actor):
    """
    OpenSSH no longer allows root logins with password.

    Check the values of PermitRootLogin in OpenSSH server configuration file
    and warn about potential issues after update.
    """
    name = 'openssh_permit_root_login'
    consumes = (OpenSshConfig, )
    produces = (Report, )
    tags = (ChecksPhaseTag, IPUWorkflowTag, )

    def process(self):
        openssh_messages = self.consume(OpenSshConfig)
        config = next(openssh_messages, None)
        if list(openssh_messages):
            api.current_logger().warning('Unexpectedly received more than one OpenSshConfig message.')
        if not config:
            raise StopActorExecutionError(
                'Could not check openssh configuration', details={'details': 'No OpenSshConfig facts found.'}
            )

        resources = [
            reporting.RelatedResource('package', 'openssh-server'),
            reporting.RelatedResource('file', '/etc/ssh/sshd_config')
        ]
        if not config.permit_root_login:
            add_permitrootlogin_conf()
            create_report([
                reporting.Title('SSH configuration automatically modified to permit root login'),
                reporting.Summary(
                    'Your OpenSSH configuration file does not explicitly state '
                    'the option PermitRootLogin in sshd_config file. '
                    'Its default is "yes" in RHEL7, but will change in '
                    'RHEL8 to "prohibit-password", which may affect your ability '
                    'to log onto this machine after the upgrade. '
                    'To prevent this from occuring, the PermitRootLogin option '
                    'has been explicity set to "yes" to preserve the default behaivour '
                    'after migration.'
                ),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags(COMMON_REPORT_TAGS),
                reporting.Remediation(
                    hint='If you would prefer to configure the root login policy yourself, '
                         'consider setting the PermitRootLogin option '
                         'in sshd_config explicitly.'
                )
            ] + resources)

        # Check if there is at least one PermitRootLogin other than "no"
        # in match blocks (other than Match All).
        # This usually means some more complicated setup depending on the
        # default value being globally "yes" and being overwritten by this
        # match block
        elif semantics_changes(config):
            create_report([
                reporting.Title('OpenSSH configured to allow root login'),
                reporting.Summary(
                    'OpenSSH is configured to deny root logins in match '
                    'blocks, but not explicitly enabled in global or '
                    '"Match all" context. This update changes the '
                    'default to disable root logins using paswords '
                    'so your server might become inaccessible.'
                ),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags(COMMON_REPORT_TAGS),
                reporting.Remediation(
                    hint='Consider using different user for administrative '
                         'logins or make sure your configration file '
                         'contains the line "PermitRootLogin yes" '
                         'in global context if desired.'
                ),
                reporting.Flags([reporting.Flags.INHIBITOR])
            ] + resources)
