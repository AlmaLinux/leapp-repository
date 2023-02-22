from leapp.actors import Actor
from leapp.libraries.actor import registerpackageworkarounds
from leapp.models import InstalledRPM, DNFWorkaround, PreRemovedRpmPackages
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux


class RegisterPackageWorkarounds(Actor):
    """
    Registers a yum workaround that adjusts the problematic packages that would
    break the main upgrade transaction otherwise.
    """

    name = 'register_package_workarounds'
    consumes = (InstalledRPM,)
    produces = (DNFWorkaround, PreRemovedRpmPackages)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    @run_on_cloudlinux
    def process(self):
        registerpackageworkarounds.process()
