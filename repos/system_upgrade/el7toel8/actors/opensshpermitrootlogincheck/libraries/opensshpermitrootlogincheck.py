import errno
from leapp.libraries.stdlib import api


def semantics_changes(config):
    globally_enabled = False
    in_match_disabled = False
    for opt in config.permit_root_login:
        if opt.value != "yes" and opt.in_match is not None \
                and opt.in_match[0].lower() != 'all':
            in_match_disabled = True

        if opt.value == "yes" and (opt.in_match is None or
                                   opt.in_match[0].lower() == 'all'):
            globally_enabled = True

    return not globally_enabled and in_match_disabled


def add_permitrootlogin_conf():
    CONFIG = '/etc/ssh/sshd_config'
    try:
        with open(CONFIG, 'r') as fd:
            sshd_config = fd.readlines()

            # If the last line of the config doesn't have a newline, add it.
            if sshd_config[-1][-1] != '\n':
                sshd_config[-1].append('\n')

            permit_autoconf = [
                "\n",
                "# Automatically added by Leapp to preserve RHEL7 default\n",
                "# behaviour after migration.\n",
                "PermitRootLogin yes\n"
            ]
            sshd_config.extend(permit_autoconf)
        with open(CONFIG, 'w') as fd:
            fd.writelines(sshd_config)

    except IOError as err:
        if err.errno != errno.ENOENT:
            error = 'Failed to open sshd_config: {}'.format(str(err))
            api.current_logger().error(error)
        return
