import errno
from leapp.libraries.stdlib import api


def global_value(config, default):
    """
    Find the global value for PermitRootLogin option in sshd_config.

    OpenSSH is using the first value found in configuration file, that is not
    in match block other than "all". If there is no such option, the argument
    "default" will be returned.
    """
    for opt in config.permit_root_login:
        if (opt.in_match is None or opt.in_match[0].lower() == 'all'):
            return opt.value
    return default


def semantics_changes(config):
    """
    Check if the current configuration changes semantics if upgraded from RHEL7 to RHEL8

    The case where the configuration does not contain *any* PermitRootLogin option is
    already covered in the actor and does not need to be handled here.

    This tries to capture the case, where the root login is enabled in at least one
    match block. The global default changes so the new configurations will not allow
    all password root logins, but there is at least some chance to access the system as
    root with password.

    Examples:
    * If the root login is globally set (enabled or disabled), the semantics stays the same.
    * If the root login is enabled only in match blocks, the semantics changes, but the
      machine stays accessible at least for clients matching this block.

    """
    config_global_value = global_value(config, None)
    in_match_enabled = False
    if not config.permit_root_login:
        return True

    for opt in config.permit_root_login:
        if opt.value == "yes" and opt.in_match is not None and \
                                  opt.in_match[0].lower() != 'all':
            in_match_enabled = True

    return config_global_value is None and not in_match_enabled


def add_permitrootlogin_conf():
    CONFIG = '/etc/ssh/sshd_config'
    CONFIG_BACKUP = '/etc/ssh/sshd_config.leapp_backup'
    try:
        with open(CONFIG, 'r') as fd:
            sshd_config = fd.readlines()

            permit_autoconf = [
                "# Automatically added by Leapp to preserve RHEL7 default\n",
                "# behaviour after migration.\n",
                "# Placed on top of the file to avoid being included into Match blocks.\n",
                "PermitRootLogin yes\n"
                "\n",
            ]
            permit_autoconf.extend(sshd_config)
        with open(CONFIG, 'w') as fd:
            fd.writelines(permit_autoconf)
        with open(CONFIG_BACKUP, 'w') as fd:
            fd.writelines(sshd_config)

    except IOError as err:
        if err.errno != errno.ENOENT:
            error = 'Failed to open sshd_config: {}'.format(str(err))
            api.current_logger().error(error)
        return
