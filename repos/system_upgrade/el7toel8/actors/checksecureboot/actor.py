from leapp.actors import Actor
from leapp.libraries.actor import checksecureboot
from leapp.models import FirmwareFacts, InstalledRPM
from leapp.reporting import Report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag


class CheckSecureBoot(Actor):
    """
    Inhibit the upgrade to an OS of a different vendor when Secure Boot is enabled.

    The upgrade environment is booted with the kernel of the target OS, which
    is signed by the Secure Boot key of the target OS vendor. However, it is
    loaded by the bootloader (shim) of the source OS, which trusts only kernels
    signed by the vendor of the source OS. With Secure Boot enabled, the
    upgrade boot entry is refused with the "invalid signature" error after the
    reboot and the upgrade does not start.

    The target OS is determined by the installed leapp-data-<distro> package.
    """

    name = 'check_secure_boot'
    consumes = (FirmwareFacts, InstalledRPM)
    produces = (Report,)
    tags = (ChecksPhaseTag, IPUWorkflowTag)

    def process(self):
        checksecureboot.process()
