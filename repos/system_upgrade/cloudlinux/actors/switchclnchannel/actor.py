from leapp.actors import Actor
from leapp.libraries.stdlib import api
from leapp.tags import DownloadPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import CalledProcessError, run


class SwitchClnChannel(Actor):
    """
    Switch CLN channel from 7 to 8 to be able to download upgrade packages
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
            res = run(switch_cmd)
            self.log.debug('Command "%s" result: %s', switch_cmd, res)
            res = run(yum_clean_cmd)  # required to update the repolist
            self.log.debug('Command "%s" result: %s', yum_clean_cmd, res)
            res = run(update_release_cmd)
            self.log.debug('Command "%s" result: %s', update_release_cmd, res)
        except OSError as e:
            api.current_logger().error('Could not call RHN command: Message: %s', str(e), exc_info=True)
