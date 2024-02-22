import pytest


@pytest.mark.usefixtures("get_os_release")
class TestOSRelease:
    """Test values of NAME, ID and VERSION_ID"""

    def test_os_rel_name(self, get_os_release):
        assert get_os_release.contains('NAME="Oracle Linux Server"')

    def test_os_rel_id(self, get_os_release):
        assert get_os_release.contains('ID="ol"')

    def test_os_rel_version_id(self, get_os_release):
        assert get_os_release.contains('VERSION_ID="8.*"')


@pytest.mark.usefixtures("get_redhat_release")
class TestRHRelease:
    """Test contents of the /etc/redhat-release"""

    def test_redhat_release(self, get_redhat_release):
        assert get_redhat_release.contains("Red Hat Enterprise Linux release 8.*")
