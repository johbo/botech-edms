from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.generics import (
    ConfirmView, MultiFormView
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


class AccountingDocumentEditView(MultiFormView):
    """Specialized view to support the accounting workflow.

    This view shows the relevant aspects of a document which are required when
    adding the document to the accounting system:

    * Preview

      Displayed, so that all relevant information is at hands when working with
      the document.

    * Document Type

      Displayed so that it can be verified quickly.

    * Specific Metadata attributes

      The "acct_" prefixed metadata attributes are shown, so that they can be
      inspected, updated and also added as needed.

      Case for inspection: The legal entity must be correct, rarely changed.

      Case for updating: The fiscal year and also the number range are
      pre-filled, but are sometimes set with a different value.

      Case for adding: The document number is set in the accounting system and
      the value is propagated back once the records have been posted.

    * Comments

      It is a frequent case that some aspects of an invoice or financial
      document need specific handling. In these cases a comment can be added,
      so that this information can be captured together with the document.


    Further changes are made when the form is submitted via the "Flag as booked" button:

    * Tagging the document with the tag "Booked". This tag also will
      potentially trigger workflow state changes, so that the document will
      disappear from special inbox cabinets or similar.

    """

    # TODO: implement view
    pass
