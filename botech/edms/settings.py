from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import (
    DEFAULT_BOTECH_BOOKED_TAG
)


namespace = SettingNamespace(label=_('bo-tech'), name='botech')

setting_botech_booked_tag = namespace.add_setting(
    default=DEFAULT_BOTECH_BOOKED_TAG,
    global_name='BOTECH_BOOKED_TAG',
    help_text = _('Tag to flag documents as booked in accounting.'))
