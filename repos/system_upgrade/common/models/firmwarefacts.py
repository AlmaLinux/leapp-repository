from leapp.models import fields, Model
from leapp.topics import SystemFactsTopic


class FirmwareFacts(Model):
    topic = SystemFactsTopic

    firmware = fields.StringEnum(['bios', 'efi'])
    """ System firmware interface (BIOS or EFI) """
    ppc64le_opal = fields.Nullable(fields.Boolean())
    """ Check OPAL presence to identify ppc64le bare metal systems """
    secureboot_enabled = fields.Nullable(fields.Boolean())
    """
    Whether Secure Boot is enabled.

    The value is None when the state cannot be determined, e.g. on BIOS
    systems, on systems without the Secure Boot support, or when the EFI
    variables are not accessible.
    """
