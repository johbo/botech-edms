from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

link_acct_document_edit_view = Link(
    args='resolved_object.id',
    text=_('Process for Accounting'),
    view='botech_edms:document_acct_edit_view'
)

link_pre_process_document_edit_view = Link(
    args='resolved_object.id',
    text=_('Pre process document'),
    view='botech_edms:document_pre_process_view'
)
