import os

from leapp.libraries.stdlib import api

VAR_FOLDER = "/etc/yum/vars"


def vars_update():
    """ Iterate through and modify the variables. """
    if not os.path.isdir(VAR_FOLDER):
        api.current_logger().debug(
            "The {} directory doesn't exist. Nothing to do.".format(VAR_FOLDER)
        )
        return

    for varfile_name in os.listdir(VAR_FOLDER):
        # cp_centos_major_version contains the current OS' major version.
        if varfile_name == 'cp_centos_major_version':
            varfile_path = os.path.join(VAR_FOLDER, varfile_name)

            with open(varfile_path, 'w') as varfile:
                # Overwrite the value from outdated "7".
                varfile.write('8')
