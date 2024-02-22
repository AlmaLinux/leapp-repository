import pytest


@pytest.mark.usefixtures("get_os_release")
class TestOSRelease:
    """Test values of NAME, ID and VERSION_ID"""

    def test_os_rel_name(self, get_os_release):
        assert get_os_release.contains('NAME="AlmaLinux"')

    def test_os_rel_id(self, get_os_release):
        assert get_os_release.contains('ID="almalinux"')

    def test_os_rel_version_id(self, get_os_release):
        assert get_os_release.contains('VERSION_ID="9.*"')


@pytest.mark.usefixtures("get_redhat_release")
class TestRHRelease:
    """Test contents of the /etc/redhat-release"""

    def test_redhat_release(self, get_redhat_release):
        assert get_redhat_release.contains("AlmaLinux release 9.*")


@pytest.mark.usefixtures("get_kernel_info")
class TestKernelInfo:
    """Test version and vendor of running kernel"""

    def test_kernel_version(self, get_kernel_info):
        assert get_kernel_info[0] == "5.14.0"

    def test_kernel_vendor(self, get_kernel_info):
        assert get_kernel_info[1] == "AlmaLinux"


@pytest.mark.usefixtures("get_pkg_info")
class TestPkgInfo:
    """Test vendor and version of packages"""

    def test_pkg_vendor(self, get_pkg_info):
        assert get_pkg_info[1] == "AlmaLinux"

    def test_pkg_version(self, get_pkg_info):
        if get_pkg_info[0] == "glibc":
            assert get_pkg_info[2] == "2.34"
        elif get_pkg_info[0] == "systemd":
            assert get_pkg_info[2] == "252"
        elif get_pkg_info[0] == "coreutils":
            assert get_pkg_info[2] == "8.32"
        else:
            assert get_pkg_info[2] == "4.16.1.3"
