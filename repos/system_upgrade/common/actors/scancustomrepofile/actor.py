from leapp.actors import Actor
from leapp.libraries.actor import scancustomrepofile
from leapp.models import CustomTargetRepository, CustomTargetRepositoryFile, TargetSystemType
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.stdlib import api


class ScanCustomRepofile(Actor):
    """
    Scan the custom /etc/leapp/files/leapp_upgrade_repositories.repo repo file.

    This is the official path where to put the YUM/DNF repository file with
    custom repositories for the target system. These repositories will be used
    automatically for the in-place upgrade despite the enable/disable settings.

    Additionally the CustomTargetRepositoryFile message is produced if the file
    exists to let the other actors know they should handle the file as well.

    If the file doesn't exist, nothing happens.
    """

    name = 'scan_custom_repofile'
    consumes = (TargetSystemType)
    produces = (CustomTargetRepository, CustomTargetRepositoryFile)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    def process(self):
        type_message = next(api.consume(TargetSystemType), None)
        if not type_message:
            api.current_logger().info(('The current configuration does not provide a target system type, assuming stable'))
            target_type = "stable"
        else:
            target_type = type_message.system_type

        scancustomrepofile.process(target_type)
