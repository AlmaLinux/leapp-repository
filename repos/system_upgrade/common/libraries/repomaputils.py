import json
from collections import defaultdict

from leapp.libraries.stdlib import api
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.common.fetch import load_data_asset
from leapp.models import PESIDRepositoryEntry, RepoMapEntry


def inhibit_upgrade(msg):
    rpmname = 'leapp-upgrade-el{}toel{}'.format(get_source_major_version(), get_target_major_version())
    hint = (
        'All official data files are nowadays part of the installed rpms.'
        ' This issue is usually encountered when the data files are incorrectly customized, replaced, or removed'
        ' (e.g. by custom scripts).'
        ' In case you want to recover the original file, remove it (if still exists)'
        ' and reinstall the {} rpm.'
        .format(rpmname)
    )
    raise StopActorExecutionError(msg, details={'hint': hint})

def read_repofile(repofile, directory="/etc/leapp/files"):
    # NOTE: what about catch StopActorExecution error when the file cannot be
    # obtained -> then check whether old_repomap file exists and in such a case
    # inform user they have to provde the new repomap.json file (we have the
    # warning now only which could be potentially overlooked)
    repofile_data = load_data_asset(api.current_actor(),
                                    repofile,
                                    asset_fulltext_name='Repositories mapping',
                                    asset_directory=directory,
                                    docs_url='',
                                    docs_title='')
    return repofile_data  # If the file does not contain a valid json then load_asset will do a stop actor execution


class RepoMapData(object):
    VERSION_FORMAT = '1.2.0'

    def __init__(self):
        self.repositories = []
        self.mapping = {}

    def add_repository(self, data, pesid):
        """
        Add new PESIDRepositoryEntry with given pesid from the provided dictionary.

        :param data: A dict containing the data of the added repository. The dictionary structure corresponds
                     to the repositories entries in the repository mapping JSON schema.
        :type data: Dict[str, str]
        :param pesid: PES id of the repository family that the newly added repository belongs to.
        :type pesid: str
        """
        self.repositories.append(PESIDRepositoryEntry(
            repoid=data['repoid'],
            channel=data['channel'],
            rhui=data.get('rhui', ''),
            repo_type=data['repo_type'],
            arch=data['arch'],
            major_version=data['major_version'],
            pesid=pesid
        ))

    def get_repositories(self, valid_major_versions):
        """
        Return the list of PESIDRepositoryEntry object matching the specified major versions.
        """
        return [repo for repo in self.repositories if repo.major_version in valid_major_versions]

    def get_version_repoids(self, major_version):
        """
        Return the list of repository ID strings for repositories matching the specified major version.
        """
        return [repo.repoid for repo in self.repositories if repo.major_version == major_version]

    def add_mapping(self, source_major_version, target_major_version, source_pesid, target_pesid):
        """
        Add a new mapping entry that is mapping the source pesid to the destination pesid(s),
        relevant in an IPU from the supplied source major version to the supplied target
        major version.

        :param str source_major_version: Specifies the major version of the source system
                                         for which the added mapping applies.
        :param str target_major_version: Specifies the major version of the target system
                                         for which the added mapping applies.
        :param str source_pesid: PESID of the source repository.
        :param Union[str|List[str]] target_pesid: A single target PESID or a list of target
                                                  PESIDs of the added mapping.
        """
        # NOTE: it could be more simple, but I prefer to be sure the input data
        # contains just one map per source PESID.
        key = '{}:{}'.format(source_major_version, target_major_version)
        rmap = self.mapping.get(key, defaultdict(set))
        self.mapping[key] = rmap
        if isinstance(target_pesid, list):
            rmap[source_pesid].update(target_pesid)
        else:
            rmap[source_pesid].add(target_pesid)

    def get_mappings(self, src_major_version, dst_major_version):
        """
        Return the list of RepoMapEntry objects for the specified upgrade path.

        IOW, the whole mapping for specified IPU.
        """
        key = '{}:{}'.format(src_major_version, dst_major_version)
        rmap = self.mapping.get(key, None)
        if not rmap:
            return None
        map_list = []
        for src_pesid in sorted(rmap.keys()):
            map_list.append(RepoMapEntry(source=src_pesid, target=sorted(rmap[src_pesid])))
        return map_list

    @staticmethod
    def load_from_dict(data):
        if data['version_format'] != RepoMapData.VERSION_FORMAT:
            raise ValueError(
                'The obtained repomap data has unsupported version of format.'
                ' Get {} required {}'
                .format(data['version_format'], RepoMapData.VERSION_FORMAT)
            )

        repomap = RepoMapData()

        # Load reposiories
        existing_pesids = set()
        for repo_family in data['repositories']:
            existing_pesids.add(repo_family['pesid'])
            for repo in repo_family['entries']:
                repomap.add_repository(repo, repo_family['pesid'])

        # Load mappings
        for mapping in data['mapping']:
            for entry in mapping['entries']:
                if not isinstance(entry['target'], list):
                    raise ValueError(
                        'The target field of a mapping entry is not a list: {}'
                        .format(entry)
                    )

                for pesid in [entry['source']] + entry['target']:
                    if pesid not in existing_pesids:
                        raise ValueError(
                            'The {} pesid is not related to any repository.'
                            .format(pesid)
                        )
                repomap.add_mapping(
                    source_major_version=mapping['source_major_version'],
                    target_major_version=mapping['target_major_version'],
                    source_pesid=entry['source'],
                    target_pesid=entry['target'],
                )
        return repomap
