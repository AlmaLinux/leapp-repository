from leapp.libraries.actor import scanrolloutrepositories
from leapp.libraries.common import cl_repofileutils
from leapp.libraries.common.testutils import produce_mocked
from leapp.libraries.stdlib import api

from leapp.models import (
    CustomTargetRepository,
    CustomTargetRepositoryFile,
    RepositoryData,
    RepositoryFile,
)

_REPODATA = [
    RepositoryData(repoid="repo1", name="repo1name", baseurl="repo1url/$releasever/64", enabled=True),
    RepositoryData(repoid="repo2", name="repo2name", baseurl="repo2url/$releasever/64", enabled=False),
]

_REPOFILE = RepositoryFile(file="test_rollout.repo", data=_REPODATA)


class LoggerMocked(object):
    def __init__(self):
        self.infomsg = None
        self.debugmsg = None

    def info(self, msg):
        self.infomsg = msg

    def debug(self, msg):
        self.debugmsg = msg

    def __call__(self):
        return self


def test_valid_repofile_exists(monkeypatch):
    def create_leapp_repofile_copy_mocked():
        return "/leapp_copy_path/newrepo.repo"

    monkeypatch.setattr(api, 'produce', produce_mocked())
    monkeypatch.setattr(cl_repofileutils, 'create_leapp_repofile_copy', create_leapp_repofile_copy_mocked)
    monkeypatch.setattr(api, 'current_logger', LoggerMocked())

    scanrolloutrepositories.process_repodata(_REPOFILE)

    assert api.produce.called == len(_REPODATA) + 1

    for datapoint in api.produce.model_instances:
        if isinstance(datapoint, CustomTargetRepository):
            assert "/8/64" in datapoint.baseurl
        if isinstance(datapoint, CustomTargetRepositoryFile):
            assert datapoint.file == "/leapp_copy_path/newrepo.repo"