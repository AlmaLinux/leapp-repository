import os

# This file contains the data on the currently active MySQL installation type and version.
CL7_MYSQL_TYPE_FILE = "/usr/share/lve/dbgovernor/mysql.type.installed"

# This dict matches the MySQL type strings with DNF module and stream IDs.
MODULE_STREAMS = {
    "mysql55": "mysql:cl-MySQL55",
    "mysql56": "mysql:cl-MySQL56",
    "mysql57": "mysql:cl-MySQL57",
    "mysql80": "mysql:cl-MySQL80",
    "mariadb55": "mariadb:cl-MariaDB55",
    "mariadb100": "mariadb:cl-MariaDB100",
    "mariadb101": "mariadb:cl-MariaDB101",
    "mariadb102": "mariadb:cl-MariaDB102",
    "mariadb103": "mariadb:cl-MariaDB103",
    "mariadb104": "mariadb:cl-MariaDB104",
    "mariadb105": "mariadb:cl-MariaDB105",
    "mariadb106": "mariadb:cl-MariaDB106",
    "percona56": "percona:cl-Percona56",
    "auto": "mysql:8.0"
}


def get_pkg_prefix(clmysql_type):
    """
    Get a Yum package prefix string from cl-mysql type.
    """
    if "mysql" in clmysql_type:
        return "cl-MySQL"
    elif "mariadb" in clmysql_type:
        return "cl-MariaDB"
    elif "percona" in clmysql_type:
        return "cl-Percona"
    else:
        return None


def get_clmysql_type():
    if os.path.isfile(CL7_MYSQL_TYPE_FILE):
        with open(CL7_MYSQL_TYPE_FILE, "r") as mysql_f:
            return mysql_f.read()
    return None
