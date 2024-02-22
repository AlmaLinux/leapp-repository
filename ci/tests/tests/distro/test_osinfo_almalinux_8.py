import pytest


@pytest.mark.usefixtures("get_os_release")
class TestOSRelease:
    """Test values of NAME, ID and VERSION_ID"""

    def test_os_rel_name(self, get_os_release):
        assert get_os_release.contains('NAME="AlmaLinux"')

    def test_os_rel_id(self, get_os_release):
        assert get_os_release.contains('ID="almalinux"')

    def test_os_rel_version_id(self, get_os_release):
        assert get_os_release.contains('VERSION_ID="8.*"')


@pytest.mark.usefixtures("get_redhat_release")
class TestRHRelease:
    """Test contents of the /etc/redhat-release"""

    def test_redhat_release(self, get_redhat_release):
        assert get_redhat_release.contains("AlmaLinux release 8.*")


@pytest.mark.usefixtures("get_pkg_info")
class TestPkgInfo:
    """Test vendor and version of packages"""

    def test_pkg_vendor(self, get_pkg_info):
        assert get_pkg_info[1] == "AlmaLinux"

    def test_pkg_version(self, get_pkg_info):
        if get_pkg_info[0] == "kernel":
            assert get_pkg_info[2] == "4.18.0"
        elif get_pkg_info[0] == "glibc":
            assert get_pkg_info[2] == "2.28"
        elif get_pkg_info[0] == "systemd":
            assert get_pkg_info[2] == "239"
        elif get_pkg_info[0] == "coreutils":
            assert get_pkg_info[2] == "8.30"
        else:
            assert get_pkg_info[2] == "4.14.3"
