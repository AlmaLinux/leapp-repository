from leapp import reporting
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api
from leapp.models import FirmwareFacts, InstalledRPM

_LEAPP_DATA_PREFIX = 'leapp-data-'

# Maps the ID of the source OS to the leapp-data package of the target OS
# provided by the same vendor, i.e. the target OS whose kernel is signed by
# a key trusted by the bootloader (shim) of the source OS.
_SAME_VENDOR_LEAPP_DATA = {
    'centos': 'leapp-data-centos',
    'ol': 'leapp-data-oraclelinux',
}

_SUMMARY = (
    'Secure Boot is enabled on this system. The upgrade environment is booted with the kernel'
    ' of the target OS, which is signed by the Secure Boot key of the target OS vendor. The bootloader'
    ' (shim) of the currently installed OS does not trust this key, so the system would not be able'
    ' to boot into the upgrade environment after the reboot (the "invalid signature" error) and'
    ' the upgrade would not start.'
)

_HINT = (
    'Disable Secure Boot before the upgrade. Check the documentation of your hardware, or of the'
    ' hypervisor in case of virtual machines, for information how to disable Secure Boot.'
    ' Secure Boot can be enabled again after the upgrade is finished, as the upgraded system'
    ' uses the bootloader of the target OS.'
)


def _get_installed_leapp_data_packages():
    names = set()
    for installed_rpms in api.consume(InstalledRPM):
        names.update(rpm.name for rpm in installed_rpms.items if rpm.name.startswith(_LEAPP_DATA_PREFIX))
    return sorted(names)


def _report_secure_boot_enabled(source_id, leapp_data_pkg):
    target = leapp_data_pkg[len(_LEAPP_DATA_PREFIX):]
    reporting.create_report([
        reporting.Title('Secure Boot is enabled when upgrading to an OS of a different vendor'),
        reporting.Summary(
            '{} The system is going to be upgraded from "{}" to "{}" (based on the installed {} package).'
            .format(_SUMMARY, source_id, target, leapp_data_pkg)
        ),
        reporting.Severity(reporting.Severity.HIGH),
        reporting.Groups([reporting.Groups.INHIBITOR, reporting.Groups.BOOT]),
        reporting.Remediation(hint=_HINT),
    ])


def _report_unknown_target(leapp_data_pkgs):
    if leapp_data_pkgs:
        detected = 'Multiple leapp-data packages are installed: {}.'.format(', '.join(leapp_data_pkgs))
    else:
        detected = 'No leapp-data-<distro> package is installed.'
    reporting.create_report([
        reporting.Title('Secure Boot is enabled and the target OS could not be determined'),
        reporting.Summary(
            '{} This applies when the target OS is provided by a different vendor than the installed OS.'
            ' Leapp could not determine the target OS. {}'.format(_SUMMARY, detected)
        ),
        reporting.Severity(reporting.Severity.HIGH),
        reporting.Groups([reporting.Groups.BOOT]),
        reporting.Remediation(
            hint='If the target OS is provided by a different vendor than the installed OS: {}'.format(_HINT)
        ),
    ])


def process():
    firmware_facts = next(api.consume(FirmwareFacts), None)
    if not firmware_facts:
        raise StopActorExecutionError(
            'Could not identify system firmware',
            details={'details': 'Actor did not receive FirmwareFacts message.'}
        )

    if firmware_facts.firmware != 'efi' or not firmware_facts.secureboot_enabled:
        # Nothing to do on BIOS systems, when Secure Boot is disabled, or when
        # its state cannot be determined (unsupported or inaccessible EFI variables).
        return

    source_id = api.current_actor().configuration.os_release.release_id
    leapp_data_pkgs = _get_installed_leapp_data_packages()

    if len(leapp_data_pkgs) != 1:
        _report_unknown_target(leapp_data_pkgs)
        return

    leapp_data_pkg = leapp_data_pkgs[0]
    if _SAME_VENDOR_LEAPP_DATA.get(source_id) == leapp_data_pkg:
        api.current_logger().debug(
            'Secure Boot is enabled, but the target OS is provided by the vendor of the source OS'
            ' ({} with {}).'.format(source_id, leapp_data_pkg)
        )
        return

    _report_secure_boot_enabled(source_id, leapp_data_pkg)
