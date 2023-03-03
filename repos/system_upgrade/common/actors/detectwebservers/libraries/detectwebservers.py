import os

LITESPEED_CONFIG_FILE = '/usr/local/lsws/conf/httpd_config.xml'
LITESPEED_OPEN_CONFIG_FILE = '/usr/local/lsws/conf/httpd_config.conf'
NGINX_BINARY = '/usr/sbin/nginx'


def detect_webservers():
    """
    Wrapper function for detection.
    """
    return (detect_litespeed() or detect_nginx())


# Detect LiteSpeed
def detect_litespeed():
    """
    LiteSpeed can be enterprise or open source, and each of them
    stores config in different formats
    """
    return detect_enterprise_litespeed() or detect_open_litespeed()


def detect_enterprise_litespeed():
    """
    Detects LSWS Enterprise presence
    """
    return os.path.isfile(LITESPEED_CONFIG_FILE)


def detect_open_litespeed():
    """
    Detects OpenLiteSpeed presence
    """
    return os.path.isfile(LITESPEED_OPEN_CONFIG_FILE)


def detect_nginx():
    """
    Detects NGINX presence
    """
    return os.path.isfile(NGINX_BINARY)
