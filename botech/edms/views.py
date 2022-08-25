from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import SingleObjectMixin

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.documents.forms.document_forms import DocumentForm, DocumentPropertiesForm
from mayan.apps.documents.forms.document_type_forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.permissions import (
    permission_document_edit)
from mayan.apps.metadata.api import save_metadata_list
from mayan.apps.metadata.forms import DocumentMetadataFormSet
from mayan.apps.metadata.permissions import (
    permission_document_metadata_edit,
    permission_document_metadata_remove)
from mayan.apps.views.mixins import (
    MultipleObjectViewMixin,
    RestrictedQuerysetViewMixin,
    RedirectionViewMixin)
from mayan.apps.views.generics import (
    ConfirmView, MultiFormView, MultipleObjectFormActionView
)

from .forms import CommentForm


class AccountingDocumentEditView(
        RestrictedQuerysetViewMixin,
        SingleObjectMixin,
        RedirectionViewMixin,
        MultiFormView):
    """
    Specialized view to support the accounting workflow.

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
        'properties': DocumentPropertiesForm,
        'comment': CommentForm,
    }
    skip_form_validation = {
        'properties',
    }
    prefixes = {
        'metadata': 'metadata',
        'properties': 'properties',
        'comment': 'comment',
    }

    object_permission = permission_document_edit
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid.all()
    template_name = 'botech/appearance/generic_form_group.html'

    def dispatch(self, request, *args, **kwargs):
        # Note: SingleObjectMixin depends on this to render the context. Even
        # though it does define "get_object()", it is not using it.
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        document_id = self._get_document_id_from_request()

        return reverse(
            viewname='documents:document_preview', kwargs={
                'document_id': document_id,
            }
        )

    def _get_document_id_from_request(self):
        document_id = self.kwargs.get(self.pk_url_kwarg)
        return document_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = self.object
        forms = context['forms']

        context.update({
            'title': _('Process Document for Accounting'),
            'subtitle': document.label,
            'subtemplates_list': [
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['properties'],
                        'title': _('Document properties'),
                        'read_only': True,
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['metadata'],
                        'form_display_mode_table': True,
                        'title': _('Accounting metadata'),
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['comment'],
                        'title': _('Account assignment and remarks'),
                    },
                },
            ]
        })
        return context

    def get_form_kwargs(self, form_name):
        kwargs = {}
        kwargs.update({'initial': self.get_initial(form_name=form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name=form_name)})

        if (form_name not in self.skip_form_validation and
                self.request.method in ('POST', 'PUT')):
            kwargs.update(
                {
                    'data': self.request.POST,
                    'files': self.request.FILES,
                }
            )

        kwargs.update(self.get_form_extra_kwargs(form_name=form_name) or {})

        return kwargs

    def get_form_extra_kwargs__properties(self):
        document = self.get_object()
        return {
            'instance': document,
        }

    def get_initial__metadata(self):
        document = self.object
        metadata_queryset = self._get_accounting_metadata()
        metadata = {}

        for document_metadata in metadata_queryset:
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
                    'document_type': document.document_type,
                    'metadata_type': key,
                    'value': ', '.join(value)
                }
            )
        return initial


    def post(self, request, *args, **kwargs):
        forms_to_validate = [form for name, form in self.forms.items()
                 if name not in self.skip_form_validation]
        if all([form.is_valid() for form in forms_to_validate]):
            return self.forms_valid(forms=self.forms)
        else:
            return self.forms_invalid(forms=self.forms)


    def all_forms_valid(self, forms):
        """
        Update objects based on valid form data.

        This method does delegate to specialized methods per sub-form which
        does allow to change values.
        """

        self.form_valid_metadata(forms['metadata'])
        self.form_valid_comment(forms['comment'])


    def form_valid_metadata(self, form):
        metadata_queryset = self._get_accounting_metadata()
        document = self.object

        errors = []
        for form in form.forms:
            if form.cleaned_data['update']:
                if metadata_queryset.filter(
                        metadata_type=form.cleaned_data['metadata_type_id']).exists():
                    try:
                        save_metadata_list(
                            metadata_list=[form.cleaned_data], document=document,
                            _user=self.request.user
                        )
                    except Exception as exception:
                        errors.append(exception)

                        if settings.DEBUG or settings.TESTING:
                            raise

        for error in errors:
            exception_message = _exception_to_message(error)

            messages.error(
                message=_(
                    'Error editing metadata for document: '
                    '%(document)s; %(exception)s.'
                ) % {
                    'document': document,
                    'exception': exception_message
                }, request=self.request
            )
        else:
            messages.success(
                message=_(
                    'Metadata for document %s edited successfully.'
                ) % document, request=self.request
            )

    def form_valid_comment(self, form):
        text = form.cleaned_data['text']
        if not text:
            return

        # TODO: attach a comment if text is present
        raise NotImplementedError("")

    def _get_accounting_metadata(self):
        """
        Create a QuerySet with the Accounting related Metadata of this document.
        """
        document = self.object
        user = self.request.user

        metadata = AccessControlList.objects.restrict_queryset(
            queryset=document.metadata.all(),
            permission=permission_document_metadata_edit,
            user=user
        )

        # TODO: Restrict this to only the accounting related metadata instances

        return metadata


def _exception_to_message(error):
    """
    Transform a given exception to a message.
    """
    if isinstance(error, ValidationError):
        exception_message = ', '.join(error.messages)
    else:
        exception_message = force_text(s=error)
