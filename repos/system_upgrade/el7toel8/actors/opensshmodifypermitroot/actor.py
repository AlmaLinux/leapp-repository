from leapp import reporting
from leapp.actors import Actor
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api
from leapp.models import OpenSshConfig, Report
from leapp.reporting import create_report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

import errno

CONFIG = '/etc/ssh/sshd_config'

COMMON_REPORT_TAGS = [
    reporting.Tags.AUTHENTICATION,
    reporting.Tags.SECURITY,
    reporting.Tags.NETWORK,
    reporting.Tags.SERVICES
]


class OpenSshModifyPermitRoot(Actor):
    """
    OpenSSH doesn't allow root logins with password by default on RHEL8.

    Check the values of PermitRootLogin in OpenSSH server configuration file
    and see if it was set explicitly.
    If not, adding an explicit "PermitRootLogin yes" will preserve the current
    default behaviour.
    """

    name = 'openssh_modify_permit_root'
    consumes = (OpenSshConfig, )
    produces = (Report, )
    tags = (ChecksPhaseTag.Before, IPUWorkflowTag, )

    def process(self):
        # Retreive the OpenSshConfig message.
        openssh_messages = self.consume(OpenSshConfig)
        config = next(openssh_messages, None)
        if list(openssh_messages):
            api.current_logger().warning('Unexpectedly received more than one OpenSshConfig message.')
        if not config:
            raise StopActorExecutionError(
                'Could not check openssh configuration', details={'details': 'No OpenSshConfig facts found.'}
            )

        # Read and modify the config.
        # Only act if there's no explicit PermitRootLogin option set anywhere in the config.
        if not config.permit_root_login:
            try:
                with open(CONFIG, 'r') as fd:
                    sshd_config = fd.readlines()

                    # If the last line of the config doesn't have a newline, add it.
                    if sshd_config[-1][-1] != '\n':
                        sshd_config[-1].append('\n')

                    permit_autoconf = [
                        "\n",
                        "# Automatically added by Leapp to preserve RHEL7 default\n",
                        "# behaviour after migration.\n",
                        "PermitRootLogin yes\n"
                    ]
                    sshd_config.extend(permit_autoconf)
                with open(CONFIG, 'w') as fd:
                    fd.writelines(sshd_config)

            except IOError as err:
                if err.errno != errno.ENOENT:
                    error = 'Failed to open sshd_config: {}'.format(str(err))
                    api.current_logger().error(error)
                return

            # Create a report letting the user know what happened.
            resources = [
                reporting.RelatedResource('package', 'openssh-server'),
                reporting.RelatedResource('file', '/etc/ssh/sshd_config')
            ]
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
