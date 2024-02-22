import pytest


class TestDockerServices:
    """Test docker and containerd services running and enabled"""

    def test_docker_is_running(self, host):
        assert host.service("docker.service").is_running

    def test_containerd_is_running(self, host):
        assert host.service("containerd.service").is_running

    def test_docker_is_enabled(self, host):
        assert host.service("docker.service").is_enabled

    def test_containerd_is_enabled(self, host):
        assert host.service("containerd.service").is_enabled


class TestDockerWorking:
    """Test docker working with the hello world container"""

    def test_docker_is_working(self, host):
        with host.sudo():
            cmd = host.run("sudo docker run --rm hello-world")
        assert cmd.succeeded
