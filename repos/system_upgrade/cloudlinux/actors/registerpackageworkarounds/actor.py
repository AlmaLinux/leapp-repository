from leapp.actors import Actor
from leapp.models import InstalledRPM, DNFWorkaround, PreRemovedRpmPackages
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.common.cllaunch import run_on_cloudlinux

# NOTE: The related packages are listed both here *and* in the workaround script!
# If the list changes, it has to change in both places.
# This is a limitation of the current DNFWorkaround implementation.
# TODO: unify the list in one place. A separate common file, perhaps?
PACKAGE_LIST = ['gettext-devel']


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
        preremoved_pkgs = PreRemovedRpmPackages(install=True)
        # Only produce a message if a package is actually about to be uninstalled
        for rpm_pkgs in self.consume(InstalledRPM):
            for pkg in rpm_pkgs.items:
                if (pkg.name in PACKAGE_LIST):
                    preremoved_pkgs.items.append(pkg)
                    self.log.debug("Listing package {} to be pre-removed".format(pkg.name))

        if preremoved_pkgs.items:
            self.produce(preremoved_pkgs)

        self.produce(
            # yum doesn't consider attempting to remove a non-existent package to be an error
            # we can safely give it the entire package list without checking if all are installed
            DNFWorkaround(
                display_name='problem package modification',
                script_path=self.get_tool_path('remove-problem-packages'),
            )
        )
