from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.generics import (
    ConfirmView
)

class MySimpleView(ConfirmView):
    action_cancel_redirect = post_action_redirect = reverse_lazy(
        'documents:document_list_deleted'
    )
    extra_context = {
        'title': _('MySimpleView Title')
    }

    def view_action(self):

        # TODO

        messages.success(
            message=_('My simple view did run'),
            request=self.request
        )
