from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from . import literals


namespace = SettingNamespace(label=_('bo-tech'), name='botech')

setting_botech_booked_tag = namespace.add_setting(
    default=literals.DEFAULT_BOTECH_BOOKED_TAG,
    global_name='BOTECH_BOOKED_TAG',
    help_text = _('Tag to flag documents as booked in accounting.'))

setting_acct_doc_number = namespace.add_setting(
    default=literals.DEFAULT_ACCT_DOC_NUMBER,
    global_name='BOTECH_ACCT_DOC_NUMBER',
    help_text = _('Name of MetadataType to store the document number into.'))

setting_acct_booked_date = namespace.add_setting(
    default=literals.DEFAULT_ACCT_BOOKED_DATE,
    global_name='BOTECH_ACCT_BOOKED_DATE',
    help_text = _('Name of MetadataType to store the booked date.'))

setting_acct_assignment = namespace.add_setting(
    default=literals.DEFAULT_ACCT_ASSIGNMENT,
    global_name='BOTECH_ACCT_ASSIGNMENT',
    help_text = _('Name of MetadataType to store the assignment comment into.'))
