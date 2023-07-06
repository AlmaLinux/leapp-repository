import os

from leapp.libraries.actor import scanrolloutrepositories

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def build_repo_paths(reponame):
    before_path = os.path.join(CUR_DIR, f'files/before/{reponame}')
    after_path = os.path.join(CUR_DIR, f'files/after/{reponame}')
    return (before_path, after_path)


cl_rollout_repo = build_repo_paths("cloudlinux-rollout.repo")
i360_rollout_repo = build_repo_paths("imunify-rollout.repo")
i360_new_rollout_repo = build_repo_paths("imunify-new-rollout.repo")


def test_rollout_repos():
    tests = [cl_rollout_repo, i360_rollout_repo, i360_new_rollout_repo]
    for config, expected_config in tests:
        with open(config, "r") as config_file, open(expected_config, "r") as expected_file:
            config_lines = config_file.readlines()
            expected_lines = expected_file.readlines()

            config_lines = scanrolloutrepositories.replace_releasever()
            assert config_lines == expected_lines
