from django.utils.translation import ugettext_lazy as _

from mayan.apps.document_states.classes import WorkflowAction


# TODO: This adds an extry into the available actions when defining
# a workflow.

class MySimpleDocumentAction(WorkflowAction):
    label = _('My simple document action')

    def execute(self, context):
        raise NotImplementedError('TODO: implement me!')

