from leapp.libraries import stdlib
from leapp.models import InstalledRPM


def get_installed_rpms():
    rpm_cmd = [
        '/bin/rpm',
        '-qa',
        '--queryformat',
        r'%{NAME}|%{VERSION}|%{RELEASE}|%|EPOCH?{%{EPOCH}}:{0}||%|PACKAGER?{%{PACKAGER}}:{(none)}||%|'
        r'ARCH?{%{ARCH}}:{}||%|DSAHEADER?{%{DSAHEADER:pgpsig}}:{%|RSAHEADER?{%{RSAHEADER:pgpsig}}:{(none)}|}|\n'
    ]
    try:
        return stdlib.run(rpm_cmd, split=True)['stdout']
    except stdlib.CalledProcessError as err:
        error = 'Execution of {CMD} returned {RC}. Unable to find installed packages.'.format(CMD=err.command,
                                                                                              RC=err.exit_code)
        stdlib.api.current_logger().error(error)
        return []


def create_lookup(model, field, keys, context=stdlib.api):
    """
    Create a lookup list from one of the model fields.
    Returns a list of keys instead of a set, as you might want to
    access this data at some point later in some form of structured
    manner. See package_data_for

    :param model: model class
    :param field: model field, its value will be taken for lookup data
    :param key: property of the field's data that will be used to build a resulting set
    :param context: context of the execution
    """
    data = getattr(next((m for m in context.consume(model)), model()), field)
    try:
        return [tuple(getattr(obj, key) for key in keys) for obj in data] if data else list()
    except TypeError:
        # data is not iterable, not lookup can be built
        stdlib.api.current_logger().error(
                "{model}.{field}.{keys} is not iterable, can't build lookup".format(
                    model=model, field=field, keys=keys))
        return list()


def has_package(model, package_name, arch=None, version=None, release=None, context=stdlib.api):
    """
    Expects a model InstalledRedHatSignedRPM or InstalledUnsignedRPM.
    Can be useful in cases like a quick item presence check, ex. check in actor that
    a certain package is installed. Returns BOOL
    :param model: model class
    :param package_name: package to be checked
    :param arch: filter by architecture. None means all arches.
    :param version: filter by version. None means all versions.
    :param release: filter by release. None means all releases.
    """
    if not (isinstance(model, type) and issubclass(model, InstalledRPM)):
        return False
    keys = ['name']
    if arch:
        keys.append('arch')
    if version:
        keys.append('version')
    if release:
        keys.append('release')

    attributes = [package_name]
    attributes += [attr for attr in (arch, version, release) if attr is not None]
    rpm_lookup = create_lookup(model, field='items', keys=keys, context=context)
    return tuple(attributes) in rpm_lookup


def package_data_for(model, package_name, context=stdlib.api):
    """
    Expects a model InstalledRedHatSignedRPM or InstalledUnsignedRPM.
    Useful for where we want to know a thing is installed
    THEN do something based on the data.
    Returns list( name, arch, version, release ) for given RPM.
    :param model: model class
    :param package_name: package to be checked
    :param arch: filter by architecture. None means all arches.
    :param version: filter by version. None means all versions.
    :param release: filter by release. None means all releases.
    """
    if not (isinstance(model, type) and issubclass(model, InstalledRPM)):
        return list()

    lookup_keys = ['name', 'arch', 'version', 'release']
    for (rpmName,rpmArch,rpmVersion,rpmRelease) in create_lookup(model, field='items', keys=lookup_keys, context=context):
        if package_name == rpmName:
            return {'name': rpmName,'arch': rpmArch, 'version': rpmVersion, 'release': rpmRelease}


def _read_rpm_modifications(config):
    """
    Ask RPM database whether the configuration file was modified.

    :param config: a config file to check
    """
    try:
        return stdlib.run(['rpm', '-Vf', config], split=True, checked=False)['stdout']
    except OSError as err:
        error = 'Failed to check the modification status of the file {}: {}'.format(config, str(err))
        stdlib.api.current_logger().error(error)
        return []


def _parse_config_modification(data, config):
    """
    Handle the output of rpm verify command to figure out if configuration file was modified.

    :param data: output of the rpm verify
    :param config: a config file to check
    """

    # First assume it is not modified -- empty data says it is not modified
    modified = False
    for line in data:
        parts = line.split(' ')
        # The last part of the line is the actual file we care for
        if parts[-1] == config:
            # First part contains information, if the size and digest differ
            if '5' in parts[0] or 'S' in parts[0]:
                modified = True
        # Ignore any other files lurking here

    return modified


def check_file_modification(config):
    """
    Check if the given configuration file tracked by RPM was modified

    This is useful when figuring out if the file will be replaced by the rpm on the upgrade
    or we need to take care of the upgrade manually.

    :param config: The configuration file to check
    """
    output = _read_rpm_modifications(config)
    return _parse_config_modification(output, config)
