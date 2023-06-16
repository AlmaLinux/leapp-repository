import os
from leapp import config


def get_config():
    if not config._LEAPP_CONFIG:
        os.environ['LEAPP_CONFIG'] = '/etc/leapp/files/leapp.conf'
        config._CONFIG_DEFAULTS['repositories'] = {'repo_path': '/etc/leapp/repos.d'}
    return config.get_config()
