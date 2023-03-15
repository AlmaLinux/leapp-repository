import os
import os.path

from leapp.libraries.stdlib import api


NOPANEL_NAME = 'No panel'
CPANEL_NAME = 'cPanel'
DIRECTADMIN_NAME = 'DirectAdmin'
PLESK_NAME = 'Plesk'
ISPMANAGER_NAME = 'ISPManager'
INTERWORX_NAME = 'InterWorx'
UNKNOWN_NAME = 'Unknown (legacy)'
INTEGRATED_NAME = 'Integrated'

CLSYSCONFIG = '/etc/sysconfig/cloudlinux'


def lvectl_custompanel_script():
    """
    Retrives custom panel script for lvectl from CL config file
    :return: Script path or None if script filename wasn't found in config
    """
    config_param_name = 'CUSTOM_GETPACKAGE_SCRIPT'
    try:
        # Try to determine the custom script name
        if os.path.exists(CLSYSCONFIG):
            with open(CLSYSCONFIG, 'r') as f:
                file_lines = f.readlines()
            for line in file_lines:
                line = line.strip()
                if line.startswith(config_param_name):
                    line_parts = line.split('=')
                    if len(line_parts) == 2 and line_parts[0].strip() == config_param_name:
                        script_name = line_parts[1].strip()
                        if os.path.exists(script_name):
                            return script_name
    except (OSError, IOError, IndexError):
        # Ignore errors - what's important is that the script wasn't found
        pass
    return None


def detect_panel():
    """
    This function will try to detect control panels supported by CloudLinux
    :return: Detected control panel name or None
    """
    panel_name = NOPANEL_NAME
    if os.path.isfile('/opt/cpvendor/etc/integration.ini'):
        panel_name = INTEGRATED_NAME
    elif os.path.isfile('/usr/local/cpanel/cpanel'):
        panel_name = CPANEL_NAME
    elif os.path.isfile('/usr/local/directadmin/directadmin') or\
            os.path.isfile('/usr/local/directadmin/custombuild/build'):
        panel_name = DIRECTADMIN_NAME
    elif os.path.isfile('/usr/local/psa/version'):
        panel_name = PLESK_NAME
    # ispmanager must have:
    # v5: /usr/local/mgr5/ directory,
    # v4: /usr/local/ispmgr/bin/ispmgr file
    elif os.path.isfile('/usr/local/ispmgr/bin/ispmgr') or os.path.isdir('/usr/local/mgr5'):
        panel_name = ISPMANAGER_NAME
    elif os.path.isdir('/usr/local/interworx'):
        panel_name = INTERWORX_NAME
    # Check if the CL config has a legacy custom script for a control panel
    elif lvectl_custompanel_script():
        panel_name = UNKNOWN_NAME
    return panel_name
