from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

link_my_simple_view = Link(
    args='resolved_object.id',
    text=_('My simple view action'),
    view='botech_edms:document_my_simple_view'
)
