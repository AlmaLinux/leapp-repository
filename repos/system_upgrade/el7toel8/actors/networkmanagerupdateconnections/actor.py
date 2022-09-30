from leapp.actors import Actor
from leapp.libraries.stdlib import CalledProcessError, run
from leapp.models import NetworkManagerConfig
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp import reporting


class NetworkManagerUpdateConnections(Actor):
    """
    Update NetworkManager connections.

    When using dhcp=dhclient on Red Hat Enterprise Linux 7, a non-hexadecimal client-id (a string)
    is sent on the wire as is (i.e. the first character is the 'type' as per RFC 2132 section
    9.14). On Red Hat Enterprise Linux 8, a zero byte is prepended to string-only client-ids. To
    preserve behavior on upgrade, we convert client-ids to the hexadecimal form.
    """

    name = 'network_manager_update_connections'
    consumes = (NetworkManagerConfig,)
    produces = ()
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    def process(self):
        for nm_config in self.consume(NetworkManagerConfig):
            if nm_config.dhcp not in ('', 'dhclient'):
                self.log.info('DHCP client is "{}", nothing to do'.format(nm_config.dhcp))
                return

            try:
                r = run(['/usr/bin/python3', 'tools/nm-update-client-ids.py'])
                if r['exit_code'] == 79:
                    title = 'NetworkManager connection update failed - PyGObject bindings for NetworkManager not found.'
                    summary = 'When using dhcp=dhclient on Red Hat Enterprise Linux 7, a non-hexadecimal ' \
                        'client-id (a string) is sent on the wire as is. On Red Hat Enterprise Linux 8, a zero ' \
                        'byte is prepended to string-only client-ids. If you wish to preserve the RHEL 7 behaviour, ' \
                        'you may want to convert your client-ids to hexadecimal form manually.'
                    reporting.create_report([
                        reporting.Title(title),
                        reporting.Summary(summary),
                        reporting.Severity(reporting.Severity.MEDIUM),
                        reporting.Tags([reporting.Tags.NETWORK])
                    ])
                    continue

                self.log.info('Updated client-ids: {}'.format(r['stdout']))
            except (OSError, CalledProcessError) as e:
                self.log.warning('Error calling nm-update-client-ids script: {}'.format(e))

            break
