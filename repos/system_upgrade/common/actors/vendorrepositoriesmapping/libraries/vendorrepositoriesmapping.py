import os

from leapp.libraries.common.config.version import get_target_major_version, get_source_major_version
from leapp.libraries.common.repomaputils import RepoMapData, read_repofile, inhibit_upgrade
from leapp.libraries.stdlib import api
from leapp.models import VendorSourceRepos, RepositoriesMapping
from leapp.models.fields import ModelViolationError


VENDORS_DIR = "/etc/leapp/files/vendors.d"
"""The folder containing the vendor repository mapping files."""


def read_repomap_file(repomap_file, read_repofile_func, vendor_name):
    json_data = read_repofile_func(repomap_file, VENDORS_DIR)
    try:
        repomap_data = RepoMapData.load_from_dict(json_data)

        # What repositories associated with the vendor are expected to be present
        # on a system with the current major version?
        # We need to know that to know what to look for in currently enabled
        # system repositories.
        api.produce(VendorSourceRepos(
            vendor=vendor_name,
            source_repoids=repomap_data.get_version_repoids(get_source_major_version())
        ))

        mapping = repomap_data.get_mappings(get_source_major_version(), get_target_major_version())
        valid_major_versions = [get_source_major_version(), get_target_major_version()]

        # This RepositoriesMapping message is different from the one produced by the
        # builtin actor because of the vendor field.
        # It can be used later to distinguish the messages provided from vendors and the one
        # from the OS upgrade data.
        api.produce(RepositoriesMapping(
            mapping=mapping,
            repositories=repomap_data.get_repositories(valid_major_versions),
            vendor=vendor_name
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


def scan_vendor_repomaps(read_repofile_func=read_repofile):
    """
    Scan the repository mapping file and produce RepositoriesMapping msg.

    See the description of the actor for more details.
    """

    map_json_suffix = "_map.json"
    if os.path.isdir(VENDORS_DIR):
        vendor_mapfiles = list(filter(lambda vfile: map_json_suffix in vfile, os.listdir(VENDORS_DIR)))

        for mapfile in vendor_mapfiles:
            read_repomap_file(mapfile, read_repofile_func, mapfile[:-len(map_json_suffix)])
    else:
        api.current_logger().debug(
            "The {} directory doesn't exist. Nothing to do.".format(VENDORS_DIR)
        )
    # vendor_repomap_collection = scan_vendor_repomaps(VENDOR_REPOMAP_DIR)
    # if vendor_repomap_collection:
    #     self.produce(vendor_repomap_collection)
    #     for repomap in vendor_repomap_collection.maps:
    #         self.produce(repomap)
