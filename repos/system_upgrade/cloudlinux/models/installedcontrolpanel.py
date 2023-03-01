from leapp.models import Model, fields
from leapp.topics import SystemInfoTopic


class InstalledControlPanel(Model):
    """
    Name of the web control panel present on the system.
    'Unknown' if detection failed.
    """

    topic = SystemInfoTopic
    name = fields.String()
