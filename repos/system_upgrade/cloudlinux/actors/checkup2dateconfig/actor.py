from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp import reporting
from leapp.libraries.common.cllaunch import run_on_cloudlinux

import os


class CheckUp2dateConfig(Actor):
    """
    Move up2date.rpmnew config to the old one's place
    """

    name = 'check_up2date_config'
    consumes = ()
    produces = ()
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    original = '/etc/sysconfig/rhn/up2date'
    new = original + '.rpmnew'

    @run_on_cloudlinux
    def process(self):
        """
        For some reason we get new .rpmnew file instead of the modified `original`
        This actor tries to save the old `serverURL` parameter to new config and move new instead of old one
        """
        replace, old_lines, new_lines = None, None, None
        if os.path.exists(self.new):
            self.log.warning('"%s" config found, trying to replace the old one', self.new)
            with open(self.original) as o, open(self.new) as n:
                old_lines = o.readlines()
                new_lines = n.readlines()
                for l in old_lines:
                    if l.startswith('serverURL=') and l not in new_lines:
                        replace = l
                        break
                if replace:
                    for i, line in enumerate(new_lines):
                        if line.startswith('serverURL='):
                            new_lines[i] = replace
                            self.log.warning('"serverURL" parameter will be saved as "%s"', line.strip())
                            break
            with open(self.original, 'w') as f:
                f.writelines(new_lines)
                self.log.info('"%s" config is overwritten by the contents of "%s"', self.original, self.new)
            os.unlink(self.new)
            self.log.info('"%s" config deleted', self.new)
