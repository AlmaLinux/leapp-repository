from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.tags import DownloadPhaseTag, IPUWorkflowTag

import subprocess


class SwitchClnChannel(Actor):
    """
    """

    name = 'switch_cln_channel'
    consumes = ()
    produces = ()
    tags = (IPUWorkflowTag, DownloadPhaseTag.Before)

    switch_bin = '/usr/sbin/cln-switch-channel'

    def process(self):
        switch_cmd = [self.switch_bin, '-t', '8', '-o', '-f']
        yum_clean_cmd = ['yum', 'clean', 'all']
        update_release_cmd = ['yum', 'update', '-y', 'cloudlinux-release']
        try:
            subprocess.call(switch_cmd)
            subprocess.call(yum_clean_cmd)  # required to update the repolist
            subprocess.call(update_release_cmd)
        except OSError as e:
            api.current_logger().error('Could not call RHN command: Message: %s', str(e), exc_info=True)
