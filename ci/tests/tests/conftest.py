import pytest
import re


@pytest.fixture(scope="module")
def get_os_release(host):
    """Get content of the /etc/os-release"""
    os_release = host.file("/etc/os-release")
    return os_release


@pytest.fixture(scope="module")
def get_redhat_release(host):
    """Get content of the /etc/redhat-release"""
    redhat_release = host.file("/etc/redhat-release")
    return redhat_release


@pytest.fixture(scope="module")
def get_kernel_info(host):
    """Get kernel version and vendor information"""
    kernel_ver_pattern = re.compile(
        f".*(^[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?).*"
    )
    kernel_ver_output = host.check_output("uname -r")
    kernel_version = kernel_ver_pattern.match(kernel_ver_output).group(1)

    with host.sudo():
        kernel_vendor = host.check_output(
            "grep -Ei '(.*kernel signing key|.*CA Server|.*Build)' /proc/keys | sed -E"
            " 's/ +/:/g' | cut -d ':' -f 9 | uniq"
        )
    kernel_info = (kernel_version, kernel_vendor)
    return kernel_info


@pytest.fixture(scope="module", params=["glibc", "systemd", "coreutils", "rpm"])
def get_pkg_info(host, request):
    """Get vendor and version of installed packages"""
    pkg_name = request.param
    pkg_vendor = host.check_output(
        f"rpm -qa --queryformat \"%{{VENDOR}}\n\" {request.param} | sed '$p;d' "
    )
    pkg_version = host.check_output(
        f'rpm -qa --queryformat "%{{VERSION}}\n" {request.param} | sort -n | sed'
        " '$p;d'"
    )
    pkg_info = (pkg_name, pkg_vendor, pkg_version)
    # print(pkg_name)
    # print(pkg_vendor)
    # print(pkg_version)
    return pkg_info
