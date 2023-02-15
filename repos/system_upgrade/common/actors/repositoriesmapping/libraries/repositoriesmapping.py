import os
from collections import defaultdict

from leapp.libraries.common.config.version import get_target_major_version, get_source_major_version
from leapp.libraries.common.repomaputils import RepoMapData, read_repofile, inhibit_upgrade
from leapp.libraries.stdlib import api
from leapp.models import RepositoriesMapping
from leapp.models.fields import ModelViolationError

OLD_REPOMAP_FILE = 'repomap.csv'
"""The name of the old, deprecated repository mapping file (no longer used)."""

REPOMAP_FILE = 'repomap.json'
"""The name of the new repository mapping file."""


def scan_repositories(read_repofile_func=read_repofile):
    """
    Scan the repository mapping file and produce RepositoriesMapping msg.

    See the description of the actor for more details.
    """
    # TODO: add filter based on the current arch
    # TODO: deprecate the product type and introduce the "channels" ?.. more or less
    # NOTE: product type is changed, now it's channel: eus,e4s,aus,tus,ga,beta

    if os.path.exists(os.path.join('/etc/leapp/files', OLD_REPOMAP_FILE)):
        # NOTE: what about creating the report (instead of warning)
        api.current_logger().warning(
            'The old repomap file /etc/leapp/files/repomap.csv is present.'
            ' The file has been replaced by the repomap.json file and it is'
            ' not used anymore.'
        )

    json_data = read_repofile_func(REPOMAP_FILE)
    try:
        repomap_data = RepoMapData.load_from_dict(json_data)
        mapping = repomap_data.get_mappings(get_source_major_version(), get_target_major_version())

        valid_major_versions = [get_source_major_version(), get_target_major_version()]
        api.produce(RepositoriesMapping(
            mapping=mapping,
            repositories=repomap_data.get_repositories(valid_major_versions)
        ))
    except ModelViolationError as err:
        err_message = (
            'The repository mapping file is invalid: '
            'the JSON does not match required schema (wrong field type/value): {}'
            .format(err)
        )
        inhibit_upgrade(err_message)
    except KeyError as err:
        inhibit_upgrade(
            'The repository mapping file is invalid: the JSON is missing a required field: {}'.format(err))
    except ValueError as err:
        # The error should contain enough information, so we do not need to clarify it further
        inhibit_upgrade('The repository mapping file is invalid: {}'.format(err))
