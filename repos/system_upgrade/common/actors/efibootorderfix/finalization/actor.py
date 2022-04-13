import os

from leapp.libraries.stdlib import run
from leapp.actors import Actor
from leapp.models import InstalledTargetKernelVersion, KernelCmdlineArg, FirmwareFacts, MountEntry
from leapp.tags import FinalizationPhaseTag, IPUWorkflowTag
from leapp.exceptions import StopActorExecutionError

class EfiFinalizationFix(Actor):
    """
    Ensure that EFI boot order is updated, which is particularly necessary
    when upgrading to a different OS distro. Also rebuilds grub config
    if necessary.
    """

    name = 'efi_finalization_fix'
    consumes = (KernelCmdlineArg, InstalledTargetKernelVersion, FirmwareFacts, MountEntry)
    produces = ()
    tags = (FinalizationPhaseTag, IPUWorkflowTag)

    def process(self):
        is_system_efi = False
        ff = next(self.consume(FirmwareFacts), None)

        dirname = {
                'AlmaLinux': 'almalinux',
                'CentOS Linux': 'centos',
                'CentOS Stream': 'centos',
                'Oracle Linux Server': 'redhat',
                'Red Hat Enterprise Linux': 'redhat',
                'Rocky Linux': 'rocky'
        }

        with open('/etc/system-release', 'r') as sr:
                for line in sr:
                        if 'release' in line:
                                distro = line.split(' release ',1)[0]

        release = distro + " 8"
        distro_dir = dirname.get(distro, 'default')
        shim_path = '/boot/efi/EFI/' + distro_dir + '/shimx64.efi'
        grub_cfg_path =  '/boot/efi/EFI/' + distro_dir + '/grub.cfg'
        bootmgr_path = '\\EFI\\' + distro_dir + '\\shimx64.efi'

        has_efibootmgr = os.path.exists('/sbin/efibootmgr')
        has_shim = os.path.exists(shim_path)
        has_grub_cfg = os.path.exists(grub_cfg_path)

        if not ff:
            raise StopActorExecutionError(
                'Could not identify system firmware',
                details={'details': 'Actor did not receive FirmwareFacts message.'}
            )

        for fact in self.consume(FirmwareFacts):
            if fact.firmware == 'efi':
                is_system_efi = True
                break

        if is_system_efi and has_shim:
            with open('/proc/mounts', 'r') as fp:
                for line in fp:
                    if '/boot/efi' in line:
                        efidev = line.split(' ',1)[0]
            run(['/sbin/efibootmgr', '-c', '-d', efidev, '-p 1', '-l', bootmgr_path, '-L', release])

            if not has_grub_cfg:
                    run(['/sbin/grub2-mkconfig', '-o', grub_cfg_path])
