from leapp.actors import Actor
from leapp.tags import FinalizationPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux


class ResetRhnVersionOverride(Actor):
    """
    Reset the versionOverride value in the RHN up2date config to empty.
    """

    name = 'reset_rhn_version_override'
    consumes = ()
    produces = ()
    tags = (FinalizationPhaseTag, IPUWorkflowTag)

    @run_on_cloudlinux
    def process(self):
        up2date_config = '/etc/sysconfig/rhn/up2date'
        with open(up2date_config, 'r') as f:
            config_data = f.readlines()
            for line in config_data:
                if line.startswith('versionOverride='):
                    line = 'versionOverride='
        with open(up2date_config, 'w') as f:
            f.writelines(config_data)
