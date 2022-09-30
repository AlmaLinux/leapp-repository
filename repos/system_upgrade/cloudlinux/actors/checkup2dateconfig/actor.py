from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp import reporting

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

    def process(self):
        """
        For some reason we get new .rpmnew file instead of modified `original`
        Here is an actor which tries to save old `serverURL` parameter to new config and move new instead of old one
        """
        replace, old_lines, new_lines = None, None, None
        if os.path.exists(self.new):
            self.log.warning('"%s" config found, trying to replace old one', self.new)
            with open(self.original) as o, open(self.new) as n:
                old_lines = o.readlines()
                new_lines = n.readlines()
                for l in old_lines:
                    if 'serverURL=' in l and l not in new_lines:
                        replace = l
                        break
            if replace:
                for line in new_lines:
                    if 'serverURL=' in line:
                        line = replace
                        self.log.warning('"serverURL" parameter will be saved as "%s"', line.strip())
                        break
            with open(self.original, 'w') as f:
                f.writelines(new_lines)
                f.flush()
                self.log.info('"%s" config is overwritten by contents of the "%s"', self.original, self.new)
            os.unlink(self.new)
            self.log.info('"%s" config deleted', self.new)
