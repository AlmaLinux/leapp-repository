import os
import errno
import shutil

from leapp.actors import Actor
from leapp.libraries.common.rpms import has_package
from leapp.models import InstalledRPM
from leapp.tags import DownloadPhaseTag, IPUWorkflowTag
from leapp.libraries.common.config import version

class ClearPackageConflicts(Actor):
    """
    Remove files manually to resolve conflicts between versions of packages to be upgraded.
    """

    name = 'clear_package_conflicts'
    consumes = (InstalledRPM,)
    produces = ()
    tags = (DownloadPhaseTag.Before, IPUWorkflowTag)

    def process(self):
        if (version.current_version()[0] != "cloudlinux"):
            return

        problem_packages = ["alt-python37-six", "alt-python37-pytz"]
        problem_packages_installed = any([has_package(InstalledRPM, pkg) for pkg in problem_packages])

        if problem_packages_installed:
            problem_dirs = [
                "/opt/alt/python37/lib/python3.7/site-packages/six-1.15.0-py3.7.egg-info",
                "/opt/alt/python37/lib/python3.7/site-packages/pytz-2017.2-py3.7.egg-info"]
            for p_dir in problem_dirs:
                try:
                    if os.path.isdir(p_dir):
                        shutil.rmtree(p_dir)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
