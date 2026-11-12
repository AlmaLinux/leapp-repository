import pytest

from leapp import reporting
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.actor import checksecureboot
from leapp.libraries.common.testutils import create_report_mocked, CurrentActorMocked, logger_mocked
from leapp.libraries.stdlib import api
from leapp.models import FirmwareFacts, InstalledRPM, RPM

_PACKAGER = 'AlmaLinux Packaging Team <packager@almalinux.org>'
_PGPSIG = 'RSA/SHA256, Mon 01 Jan 2024 00:00:00 AM UTC, Key ID 51d6647ec21ad6ea'


def _rpm(name):
    return RPM(name=name, epoch='0', packager=_PACKAGER, version='0.6', release='15.el7',
               arch='noarch', pgpsig=_PGPSIG)


def _installed_rpms(*leapp_data_pkgs):
    names = ['bash', 'leapp', 'leapp-upgrade-el7toel8'] + list(leapp_data_pkgs)
    return InstalledRPM(items=[_rpm(name) for name in names])


def _mock_actor(monkeypatch, msgs, release_id='centos'):
    monkeypatch.setattr(api, 'current_actor', CurrentActorMocked(release_id=release_id, msgs=msgs))
    monkeypatch.setattr(api, 'current_logger', logger_mocked())
    monkeypatch.setattr(reporting, 'create_report', create_report_mocked())


@pytest.mark.parametrize('release_id, leapp_data_pkg', [
    ('centos', 'leapp-data-almalinux'),
    ('centos', 'leapp-data-rocky'),
    ('centos', 'leapp-data-oraclelinux'),
    ('ol', 'leapp-data-almalinux'),
    ('ol', 'leapp-data-centos'),
    ('rhel', 'leapp-data-almalinux'),
    ('scientific', 'leapp-data-centos'),
])
def test_inhibit_when_secure_boot_enabled_and_different_vendor(monkeypatch, release_id, leapp_data_pkg):
    msgs = [FirmwareFacts(firmware='efi', secureboot_enabled=True), _installed_rpms(leapp_data_pkg)]
    _mock_actor(monkeypatch, msgs, release_id=release_id)

    checksecureboot.process()

    assert reporting.create_report.called == 1
    report = reporting.create_report.report_fields
    assert report['title'] == 'Secure Boot is enabled when upgrading to an OS of a different vendor'
    assert reporting.Groups.INHIBITOR in report['groups']
    assert reporting.Groups.BOOT in report['groups']
    assert report['severity'] == reporting.Severity.HIGH
    assert leapp_data_pkg in report['summary']
    assert '"{}"'.format(release_id) in report['summary']


@pytest.mark.parametrize('release_id, leapp_data_pkg', [
    ('centos', 'leapp-data-centos'),
    ('ol', 'leapp-data-oraclelinux'),
])
def test_no_report_when_same_vendor(monkeypatch, release_id, leapp_data_pkg):
    msgs = [FirmwareFacts(firmware='efi', secureboot_enabled=True), _installed_rpms(leapp_data_pkg)]
    _mock_actor(monkeypatch, msgs, release_id=release_id)

    checksecureboot.process()

    assert not reporting.create_report.called


@pytest.mark.parametrize('firmware_facts', [
    FirmwareFacts(firmware='bios'),
    FirmwareFacts(firmware='bios', secureboot_enabled=None),
    FirmwareFacts(firmware='efi', secureboot_enabled=False),
    # the state cannot be determined (unsupported or inaccessible EFI variables)
    FirmwareFacts(firmware='efi', secureboot_enabled=None),
    FirmwareFacts(firmware='efi'),
])
def test_no_report_when_secure_boot_not_enabled(monkeypatch, firmware_facts):
    _mock_actor(monkeypatch, [firmware_facts, _installed_rpms('leapp-data-almalinux')])

    checksecureboot.process()

    assert not reporting.create_report.called


@pytest.mark.parametrize('leapp_data_pkgs, expected_in_summary', [
    ((), 'No leapp-data-<distro> package is installed.'),
    (('leapp-data-almalinux', 'leapp-data-centos'), 'leapp-data-almalinux, leapp-data-centos'),
])
def test_report_without_inhibitor_when_target_unknown(monkeypatch, leapp_data_pkgs, expected_in_summary):
    msgs = [FirmwareFacts(firmware='efi', secureboot_enabled=True), _installed_rpms(*leapp_data_pkgs)]
    _mock_actor(monkeypatch, msgs)

    checksecureboot.process()

    assert reporting.create_report.called == 1
    report = reporting.create_report.report_fields
    assert report['title'] == 'Secure Boot is enabled and the target OS could not be determined'
    assert reporting.Groups.INHIBITOR not in report['groups']
    assert report['severity'] == reporting.Severity.HIGH
    assert expected_in_summary in report['summary']


def test_leapp_data_packages_collected_from_all_messages(monkeypatch):
    msgs = [
        FirmwareFacts(firmware='efi', secureboot_enabled=True),
        _installed_rpms(),
        _installed_rpms('leapp-data-almalinux'),
    ]
    _mock_actor(monkeypatch, msgs)

    checksecureboot.process()

    assert reporting.create_report.called == 1
    assert reporting.Groups.INHIBITOR in reporting.create_report.report_fields['groups']


def test_missing_firmware_facts(monkeypatch):
    _mock_actor(monkeypatch, [_installed_rpms('leapp-data-almalinux')])

    with pytest.raises(StopActorExecutionError):
        checksecureboot.process()
