from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.forms.document_forms import DocumentForm, DocumentPropertiesForm
from mayan.apps.documents.forms.document_type_forms import DocumentTypeFilteredSelectForm
from mayan.apps.metadata.forms import DocumentMetadataFormSet
from mayan.apps.metadata.permissions import (
    permission_document_metadata_edit,
    permission_document_metadata_remove)
from mayan.apps.views.mixins import (
    MultipleObjectViewMixin, RestrictedQuerysetViewMixin,
    RedirectionViewMixin)
from mayan.apps.views.generics import (
    ConfirmView, MultiFormView, MultipleObjectFormActionView
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


class AccountingDocumentEditView(
        MultipleObjectViewMixin,
        # TODO: Does not seem to work as expected, still requires queryset to be there
        # RestrictedQuerysetViewMixin,
        MultiFormView,
        RedirectionViewMixin):
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

    form_classes = {
        'metadata': DocumentMetadataFormSet,
        # 'properties': DocumentForm,
        # 'doc_type': DocumentTypeFilteredSelectForm,
    }
    prefixes = {
        'metadata': 'metadata',
        'properties': 'properties',
        'doc_type': 'doc_type',
    }

    # This is the parameter name used from the URL configuration
    pk_url_kwarg = 'document_id'

    object_permission = None
    source_queryset = Document.valid.all()
    # TODO: restrict to permissions
    queryset = source_queryset

    template_name = 'appearance/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context.update({
            'title': _('Process Document for Accounting'),
            'subtemplates_list': [
                {
                    'name': 'appearance/generic_form_subtemplate.html',
                    'context': {
                        'form': context['forms']['metadata'],
                        'form_display_mode_table': True,
                        'title': _('Accounting Metadata'),
                    },
                },
                # {
                #     'name': 'appearance/generic_multiform_subtemplate.html',
                #     'context': {
                #         'forms': context['forms'],
                #     },
                # },
            ]
        })
        return context

    def get_form_extra_kwargs__properties(self):
        # TODO: Fix this, fail if more than one object
        document = self.get_object_list()[0]
        return {
            'document_type': document.document_type,
        }

    def get_initial__metadata(self):
        queryset = self.object_list

        metadata = {}
        for document in queryset:
            document_metadata_queryset = AccessControlList.objects.restrict_queryset(
                queryset=document.metadata.all(),
                permission=permission_document_metadata_remove,
                user=self.request.user
            )

            for document_metadata in document_metadata_queryset:
                # Metadata value cannot be None here, fallback to an empty
                # string
                value = document_metadata.value or ''
                if document_metadata.metadata_type in metadata:
                    if value not in metadata[document_metadata.metadata_type]:
                        metadata[document_metadata.metadata_type].append(value)
                else:
                    metadata[document_metadata.metadata_type] = [value] if value else ''

        initial = []
        for key, value in metadata.items():
            initial.append(
                {
                    'document_type': queryset.first().document_type,
                    'metadata_type': key,
                    'value': ', '.join(value)
                }
            )
        return initial


    def all_forms_valid(self, forms):
        # TODO: Continue here!
        raise NotImplementedError()
