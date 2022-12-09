import os
import re

from leapp.libraries.stdlib import run, api
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
                'Rocky Linux': 'rocky',
                'Scientific Linux': 'redhat',
                'CloudLinux': 'centos',
        }

        efi_shimname_dict = {
            'x86_64': 'shimx64.efi',
            'aarch64': 'shimaa64.efi'
        }

        def devparts(dev):
          part = next(re.finditer(r'\d+$', dev)).group(0)
          dev = dev[:-len(part)]
          return [dev, part];

        with open('/etc/system-release', 'r') as sr:
            release_line = next(line for line in sr if 'release' in line)
            distro = release_line.split(' release ', 1)[0]

        efi_bootentry_label = distro
        distro_dir = dirname.get(distro, 'default')
        shim_filename = efi_shimname_dict.get(api.current_actor().configuration.architecture, 'shimx64.efi')

        shim_path = '/boot/efi/EFI/' + distro_dir + '/' + shim_filename
        grub_cfg_path = '/boot/efi/EFI/' + distro_dir + '/grub.cfg'
        bootmgr_path = '\\EFI\\' + distro_dir + '\\' + shim_filename

        has_efibootmgr = os.path.exists('/sbin/efibootmgr')
        has_shim = os.path.exists(shim_path)
        has_grub_cfg = os.path.exists(grub_cfg_path)

        if not ff:
            raise StopActorExecutionError(
                'Could not identify system firmware',
                details={'details': 'Actor did not receive FirmwareFacts message.'}
            )

        if not has_efibootmgr:
            return

        for fact in self.consume(FirmwareFacts):
            if fact.firmware == 'efi':
                is_system_efi = True
                break

        if is_system_efi and has_shim:
            efidevlist = []
            with open('/proc/mounts', 'r') as fp:
                for line in fp:
                    if '/boot/efi' in line:
                        efidevpath = line.split(' ', 1)[0]
                        efidevpart = efidevpath.split('/')[-1]
            if os.path.exists('/proc/mdstat'):
               with open('/proc/mdstat', 'r') as mds:
                 for line in mds:
                   if line.startswith(efidevpart):
                     mddev = line.split(' ')
                     for md in mddev:
                       if '[' in md:
                         efimd = md.split('[', 1)[0]
                         efidp = efidevpath.replace(efidevpart, efimd)
                         efidevlist.append(efidp)
            if len(efidevlist) == 0:
              efidevlist.append(efidevpath)
            for devpath in efidevlist:
              efidev, efipart = devparts(devpath)
              run(['/sbin/efibootmgr', '-c', '-d', efidev, '-p', efipart, '-l', bootmgr_path, '-L', efi_bootentry_label])

            if not has_grub_cfg:
                run(['/sbin/grub2-mkconfig', '-o', grub_cfg_path])
