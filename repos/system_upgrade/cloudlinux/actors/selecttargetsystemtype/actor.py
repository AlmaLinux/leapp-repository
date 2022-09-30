from leapp.actors import Actor
from leapp.dialogs import Dialog
from leapp.dialogs.components import ChoiceComponent
from leapp.models import TargetSystemType
from leapp.tags import IPUWorkflowTag, FactsPhaseTag


class SelectTargetSystemType(Actor):
    """
    Check the target system type the user has chosen, and produce the
    corresponding data.

    This data will affect the list of repositories being used during the upgrade -
    normally only the stable package versions would be installed.
    """

    name = 'select_target_system_type'
    consumes = ()
    produces = (TargetSystemType,)
    tags = (IPUWorkflowTag, FactsPhaseTag.Before)

    dialogs = (
        Dialog(
            scope='select_target_system_type',
            reason='Selection',
            components=(
                ChoiceComponent(
                    key='select',
                    label='Select the type of the target system to upgrade to. '
                          'If not chosen, the system will upgrade to stable by default.',
                    description='This choice determines which package repositories will be used '
                                'during the upgrade - either the stable or the testing branch.',
                    reason='Without this selector, the system will always upgrade to the stable '
                                'branch.',
                    choices=['stable', 'beta'],
                    default='stable'
                ),
            )
        ),
    )

    def process(self):
        target_system_type = self.get_answers(self.dialogs[0]).get('select')
        if not target_system_type:
            target_system_type = 'stable'

        self.log.info("Target system type selected by user: {}".format(target_system_type))
        self.produce(TargetSystemType(system_type=target_system_type))
