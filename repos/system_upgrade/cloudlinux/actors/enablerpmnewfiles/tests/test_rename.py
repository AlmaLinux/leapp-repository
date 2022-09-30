import pytest

from leapp.libraries.actor.enablerpmnewfiles import build_repo_paths


def test_valid_architectures(monkeypatch):
    rpmnew_path = "cl.repo.rpmnew"
    expected_repo_paths = ("/etc/yum.repos.d/cl.repo", "/etc/yum.repos.d/cl.repo.rpmsave", "/etc/yum.repos.d/cl.repo.rpmnew")
    resulting_repo_paths = build_repo_paths(rpmnew_path)

    assert expected_repo_paths == resulting_repo_paths
