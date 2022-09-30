from leapp.models import Model, fields
from leapp.topics import SystemInfoTopic


class TargetSystemType(Model):
    """
    Defines the type of the system the process will upgrade the source to.

    This distinction will likely be needed mostly when selecting which custom
    package repositories to enable during the custom repofile loading - e.g.
    stable package repos vs testing ones.
    """
    topic = SystemInfoTopic
    system_type = fields.String()
