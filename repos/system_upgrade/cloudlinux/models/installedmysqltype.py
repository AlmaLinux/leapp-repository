from leapp.models import Model, fields
from leapp.topics import SystemInfoTopic


class InstalledMySqlType(Model):
    """
    Contains data about the MySQL/MariaDB/Percona installation on the source system.
    """

    topic = SystemInfoTopic
    type = fields.String()
    version = fields.Nullable(fields.String(default=None))  # used for cl-mysql
