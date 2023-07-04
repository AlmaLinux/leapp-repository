from leapp.actors import Actor
from leapp.models import InstalledRPM, DNFWorkaround, PreRemovedRpmPackages
from leapp.libraries.stdlib import api

# NOTE: The related packages are listed both here *and* in the workaround script!
# If the list changes, it has to change in both places.
# Script location: repos\system_upgrade\cloudlinux\tools\remove-problem-packages
# This is a limitation of the current DNFWorkaround implementation.
# TODO: unify the list in one place. A separate common file, perhaps?
TO_REINSTALL = [
    "gettext-devel",
    "alt-ruby31-rubygem-rack",
    "alt-ruby31-rubygem-rackup",
]  # These packages will be marked for installation
TO_DELETE = []  # These won't be


def produce_workaround_msg(pkg_list, reinstall):
    if not pkg_list:
        return
    preremoved_pkgs = PreRemovedRpmPackages(install=reinstall)
    # Only produce a message if a package is actually about to be uninstalled
    for rpm_pkgs in api.consume(InstalledRPM):
        for pkg in rpm_pkgs.items:
            if pkg.name in pkg_list:
                preremoved_pkgs.items.append(pkg)
                api.current_logger().debug(
                    "Listing package {} to be pre-removed".format(pkg.name)
                )
    if preremoved_pkgs.items:
        api.produce(preremoved_pkgs)


def process():
    produce_workaround_msg(TO_REINSTALL, True)
    produce_workaround_msg(TO_DELETE, False)

    api.produce(
        # yum doesn't consider attempting to remove a non-existent package to be an error
        # we can safely give it the entire package list without checking if all are installed
        DNFWorkaround(
            display_name="problem package modification",
            script_path=api.get_tool_path("remove-problem-packages"),
        )
    )
