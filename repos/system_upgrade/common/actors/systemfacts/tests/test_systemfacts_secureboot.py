import os

import pytest

from leapp.libraries.actor import systemfacts
from leapp.libraries.common.config import architecture
from leapp.libraries.common.testutils import CurrentActorMocked, logger_mocked
from leapp.libraries.stdlib import api

# 4 bytes of the EFI variable attributes
_ATTRS = b'\x06\x00\x00\x00'


def _mock_firmware(monkeypatch, is_efi, efivar_content=None, arch=architecture.ARCH_X86_64):
    def isdir_mocked(path):
        if path == '/sys/firmware/efi':
            return is_efi
        return False

    def read_efivar_mocked(path):
        assert path == systemfacts.SECURE_BOOT_EFIVAR_PATH
        if efivar_content is None:
            raise IOError('No such file or directory: {}'.format(path))
        return bytearray(efivar_content)

    monkeypatch.setattr(os.path, 'isdir', isdir_mocked)
    monkeypatch.setattr(systemfacts, '_read_efivar', read_efivar_mocked)
    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(arch=arch))
    monkeypatch.setattr(api, 'current_logger', logger_mocked())


@pytest.mark.parametrize('efivar_content, expected', [
    (_ATTRS + b'\x01', True),
    (_ATTRS + b'\x00', False),
    # the variable does not exist (no Secure Boot support or inaccessible EFI variables)
    (None, None),
    # unexpected content
    (b'', None),
    (_ATTRS, None),
])
def test_get_firmware_secure_boot_state_on_efi(monkeypatch, efivar_content, expected):
    _mock_firmware(monkeypatch, is_efi=True, efivar_content=efivar_content)

    firmware_facts = systemfacts.get_firmware()

    assert firmware_facts.firmware == 'efi'
    assert firmware_facts.secureboot_enabled is expected


def test_get_firmware_secure_boot_not_checked_on_bios(monkeypatch):
    def read_efivar_mocked(path):
        raise AssertionError('The EFI variable must not be read on BIOS systems.')

    _mock_firmware(monkeypatch, is_efi=False)
    monkeypatch.setattr(systemfacts, '_read_efivar', read_efivar_mocked)

    firmware_facts = systemfacts.get_firmware()

    assert firmware_facts.firmware == 'bios'
    assert firmware_facts.secureboot_enabled is None


def test_get_firmware_secure_boot_state_on_ppc64le(monkeypatch):
    _mock_firmware(monkeypatch, is_efi=False, arch=architecture.ARCH_PPC64LE)

    firmware_facts = systemfacts.get_firmware()

    assert firmware_facts.firmware == 'bios'
    assert firmware_facts.ppc64le_opal is False
    assert firmware_facts.secureboot_enabled is None
