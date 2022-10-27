from datetime import date

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import SingleObjectMixin

from mayan.apps.acls.models import AccessControlList
from mayan.apps.cabinets.forms import CabinetListForm
from mayan.apps.cabinets.models import Cabinet
from mayan.apps.converter.layers import layer_decorations
from mayan.apps.converter.models import (
    ObjectLayer, LayerTransformation)
from mayan.apps.converter.transformations import TransformationResize
from mayan.apps.documents.models import Document
from mayan.apps.documents.forms.document_forms import DocumentPropertiesForm
from mayan.apps.documents.forms.document_type_forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.forms.document_version_forms import (
    DocumentVersionPreviewForm)
from mayan.apps.documents.permissions import (
    permission_document_edit)
from mayan.apps.documents.settings import (
    setting_preview_height,
    setting_preview_width)
from mayan.apps.document_comments.models import Comment
from mayan.apps.metadata.api import save_metadata_list
from mayan.apps.metadata.models import DocumentMetadata, MetadataType
from mayan.apps.metadata.permissions import (
    permission_document_metadata_edit,
    permission_document_metadata_remove)
from mayan.apps.tags.forms import TagMultipleSelectionForm
from mayan.apps.tags.models import Tag
from mayan.apps.views.mixins import (
    MultipleObjectViewMixin,
    RestrictedQuerysetViewMixin,
    RedirectionViewMixin)
from mayan.apps.views.generics import (
    ConfirmView, MultiFormView, MultipleObjectFormActionView)

from .fixes import save_metadata
from .forms import CommentForm, DocumentForm, DocumentMetadataFormSet
from .settings import (
    setting_botech_booked_tag,
    setting_acct_assignment,
    setting_acct_booked_date,
    setting_acct_doc_number,
    setting_acct_entity,
    setting_acct_fiscal_year,
    setting_acct_number_range)
from .transformations import TransformationStampAccountingMetadata


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
        'preview': DocumentVersionPreviewForm,
    }
    skip_form_validation = {
        'properties',
        'preview',
    }
    prefixes = {
        'metadata': 'metadata',
        'properties': 'properties',
        'comment': 'comment',
        'preview': 'preview',
    }

    object_permission = permission_document_edit
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid.all()
    template_name = 'botech/appearance/generic_form_group.html'

    def dispatch(self, request, *args, **kwargs):
        # Note: SingleObjectMixin depends on this to render the context. Even
        # though it does define "get_object()", it is not using it.
        self.object = self.get_object()

        # TODO: Find a better place. This view shall not be usable if the
        # document number has already been set. Should be a generic check if
        # entry into this view is allowed.
        self._ensure_no_acct_doc_number()

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
            'submit_label': _('Save and mark as booked'),
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
                        'form': forms['preview'],
                        'title': _('Document preview'),
                        'object': document,
                        'hide_labels': True,
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

    def get_form_extra_kwargs__preview(self):
        transformation_instance_list = (
            TransformationResize(
                height=setting_preview_height.value,
                width=setting_preview_width.value
            ),
        )

        return {
            'instance': self.object,
            'transformation_instance_list': transformation_instance_list
        }

    def get_initial__metadata(self):
        document = self.object
        metadata_queryset = self._get_accounting_metadata()
        metadata = {}

        # TODO: The handling looks very complicated and may be due to the
        # "multi document" support in the edit metadata view. There is no
        # reason why for a single document there could ever by two values for a
        # given metadata type.
        for document_metadata in metadata_queryset:
            # Metadata value cannot be None here, fallback to an empty
            # string
            value = document_metadata.value or ''
            if document_metadata.metadata_type in metadata:
                if value not in metadata[document_metadata.metadata_type]:
                    metadata[document_metadata.metadata_type].append(value)
            else:
                metadata[document_metadata.metadata_type] = [value] if value else ''

        def value_to_initial(value):
            return ', '.join(value) if value else ''


        initial = []
        for key, value in metadata.items():
            value = value_to_initial(value)
            # TODO: Why can the form not get the document_metadata object?
            initial.append(
                {
                    'document_type': document.document_type,
                    'metadata_type': key,
                    'update': False,
                    'value': value,
                    'value_existing': value
                }
            )
        return initial

    def get_initial__comment(self):
        document = self.object
        initial = {
            'booked_date': date.today().isoformat(),
        }

        metadata_type = MetadataType.objects.get(
            name=setting_acct_booked_date.value)
        try:
            document_metadata = DocumentMetadata.objects.get(
                metadata_type=metadata_type,
                document=document)
            initial['booked_date'] = document_metadata.value
        except DocumentMetadata.DoesNotExist:
            pass

        metadata_type = MetadataType.objects.get(
            name=setting_acct_assignment.value)
        try:
            document_metadata = DocumentMetadata.objects.get(
                metadata_type=metadata_type,
                document=document)
            initial['text'] = document_metadata.value
        except DocumentMetadata.DoesNotExist:
            pass

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
        self.tag_document_as_booked()
        self.attach_stamp_accounting_metadata_transformation()


    def form_valid_metadata(self, form):
        metadata_queryset = self._get_accounting_metadata()
        document = self.object

        errors = []
        for form in form.forms:
            if form.cleaned_data['update']:
                if metadata_queryset.filter(
                        metadata_type=form.cleaned_data['metadata_type_id']).exists():
                    try:
                        # TODO: Use save_metadata directly and simplify
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
        acct_doc_number = form.cleaned_data['doc_number']
        self._set_acct_doc_number(acct_doc_number)

        acct_booked_date = form.cleaned_data['booked_date']
        self._set_acct_booked_date(acct_booked_date)

        comment_text = form.cleaned_data['text']
        self._set_assignment_comment_if_provided(comment_text)

    def _set_acct_doc_number(self, acct_doc_number):
        self._ensure_no_acct_doc_number()

        document = self.object
        metadata_type = MetadataType.objects.get(
            name=setting_acct_doc_number.value)

        document_metadata = DocumentMetadata(
            document=document,
            metadata_type=metadata_type,
            value=acct_doc_number)
        document_metadata._event_actor = self.request.user
        document_metadata.save()

    def _ensure_no_acct_doc_number(self):
        metadata_type = MetadataType.objects.get(
            name=setting_acct_doc_number.value)
        document = self.object

        document_metadata = DocumentMetadata.objects.filter(
            metadata_type=metadata_type,
            document=document)
        if document_metadata.exists():
            raise NotImplementedError('Handling for this case is not yet implemented')


    def _set_assignment_comment_if_provided(self, comment_text):
        document = self.object
        metadata_type = MetadataType.objects.get(
            name=setting_acct_assignment.value)

        try:
            document_metadata = DocumentMetadata.objects.get(
                metadata_type=metadata_type,
                document=document)
        except DocumentMetadata.DoesNotExist:
            document_metadata = DocumentMetadata(
                metadata_type=metadata_type,
                document=document)

        document_metadata.value = comment_text
        document_metadata._event_actor = self.request.user
        document_metadata.save()

    def _set_acct_booked_date(self, booked_date):
        document = self.object
        metadata_type = MetadataType.objects.get(
            name=setting_acct_booked_date.value)

        document_metadata, created = DocumentMetadata.objects.get_or_create(
            metadata_type=metadata_type,
            document=document)
        document_metadata.value = booked_date
        document_metadata._event_actor = self.request.user
        document_metadata.save()

    def tag_document_as_booked(self):
        document = self.object
        booked_tag = self._get_booked_tag()

        # TODO: This is a case which should result at least in a warning, since
        # normally this should not happen.
        #
        # Note that attaching the tag does trigger a workflow.
        if document.tags.filter(pk=booked_tag.pk).exists():
            raise NotImplementedError()

        booked_tag._event_actor = self.request.user
        booked_tag.attach_to(document)

        messages.success(
            message=_(
                'Attached booked tag to document %s'
            ) % document, request=self.request)

    def attach_stamp_accounting_metadata_transformation(self):
        # TODO: Handle the case that this transformation is already attached

        document = self.object
        active_version = document.versions.filter(active=True).first()
        first_page = active_version.version_pages.first()

        object_layer, created = ObjectLayer.objects.get_for(
            layer=layer_decorations, obj=first_page
        )

        layer_transformation = LayerTransformation(
            object_layer = object_layer,
            # TODO: Has to be found out for the given layer
            order = 1,
            name = TransformationStampAccountingMetadata.name,
            arguments = '',
        )
        layer_transformation.save()

    def _get_booked_tag(self):
        return Tag.objects.get(label=setting_botech_booked_tag.value)


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

        # TODO: Use a list of type ids or similar to filter
        metadata = metadata.filter(
            metadata_type__name__in=[
                setting_acct_entity.value,
                setting_acct_fiscal_year.value,
                setting_acct_number_range.value,
            ])

        return metadata


class PreProcessDocumentEditView(
        RestrictedQuerysetViewMixin,
        SingleObjectMixin,
        RedirectionViewMixin,
        MultiFormView):
    """
    Specialized view to support the pre processing workflow.
    """

    form_classes = {
        'cabinets': CabinetListForm,
        'metadata': DocumentMetadataFormSet,
        'preview': DocumentVersionPreviewForm,
        'properties': DocumentForm,
        'tags': TagMultipleSelectionForm,
    }
    skip_form_validation = {
        'preview',
    }
    prefixes = {
        'cabinets': 'cabinets',
        'metadata': DocumentMetadataFormSet,
        'preview': 'preview',
        'properties': 'properties',
        'tags': 'tags',
    }

    object_permission = permission_document_edit
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid.all()
    template_name = 'botech/appearance/pre-process-form-group.html'

    def dispatch(self, request, *args, **kwargs):
        # Note: SingleObjectMixin depends on this to render the context. Even
        # though it does define "get_object()", it is not using it.
        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # TODO: Implement a better solution to update only the document type so
        # that the remainder of the form works.
        if 'button-refresh-document-type' in request.POST:
            return self.post_refresh_document_type(request, *args, **kwargs)

        forms_to_validate = [form for name, form in self.forms.items()
                 if name not in self.skip_form_validation]
        if all([form.is_valid() for form in forms_to_validate]):
            return self.forms_valid(forms=self.forms)
        else:
            return self.forms_invalid(forms=self.forms)

    def post_refresh_document_type(self, request, *args, **kwargs):
        form = self.forms['properties']
        if form.is_valid():
            self.form_valid_properties(form)
        else:
            return self.forms_invalid(forms=[form])
        return HttpResponseRedirect(request.get_full_path())

    def all_forms_valid(self, forms):
        self.form_valid_properties(forms['properties'])
        self.form_valid_cabinets(forms['cabinets'])
        self.form_valid_tags(forms['tags'])
        self.form_valid_metadata(forms['metadata'])

    def form_valid_properties(self, form):
        # Note: Manually save by intention since changing the document type has
        # to call a special method on the instance.
        document = self.get_object()
        user = self.request.user

        # Note: The form.instance contains already the modified values after
        # the call to ModelForm.clean, that's why we use the instance from self.object
        new_document_type = form.cleaned_data['document_type']
        document.document_type_change(
            new_document_type, _user=user)

        form.save()

    def form_valid_cabinets(self, form):
        document = self.get_object()
        current_cabinets = set(document.cabinets.all())
        target_cabinets = set(form.cleaned_data['cabinets'])

        to_remove = current_cabinets - target_cabinets
        to_add = target_cabinets - current_cabinets

        for cabinet in to_remove:
            cabinet._event_actor = self.request.user
            cabinet.document_remove(document)

        for cabinet in to_add:
            cabinet._event_actor = self.request.user
            cabinet.document_add(document)

    def form_valid_tags(self, form):
        document = self.get_object()
        current_tags= set(document.tags.all())
        target_tags = set(form.cleaned_data['tags'])

        to_remove = current_tags - target_tags
        to_add = target_tags - current_tags

        for tag in to_remove:
            tag._event_actor = self.request.user
            tag.remove_from(document)

        for tag in to_add:
            tag._event_actor = self.request.user
            tag.attach_to(document)

    def form_valid_metadata(self, form):
        document = self.object
        errors = []
        for form in form.forms:
            if form.cleaned_data['update']:
                try:
                    save_metadata(
                        metadata_dict=form.cleaned_data, document=document,
                        create=True, _user=self.request.user
                    )
                except Exception as exception:
                    errors.append(exception)

                    if settings.DEBUG or settings.TESTING:
                        raise
            elif form.cleaned_data['remove']:
                try:
                    document_metadata = document.metadata.get(
                        metadata_type=form.cleaned_data['metadata_type_id'])
                    document_metadata._event_actor = self.request.user
                    document_metadata.delete()
                except DocumentMetadata.DoesNotExist:
                    # TODO: Double check if it's save to ignore this or if a special
                    # handling might be required here.
                    pass

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

    def get_form_extra_kwargs__properties(self):
        document = self.get_object()
        return {
            'instance': document,
        }

    def get_form_extra_kwargs__preview(self):
        transformation_instance_list = (
            TransformationResize(
                height=setting_preview_height.value,
                width=setting_preview_width.value
            ),
        )

        return {
            'instance': self.object,
            'transformation_instance_list': transformation_instance_list
        }

    def get_form_extra_kwargs__cabinets(self):
        return {
            'queryset': Cabinet.objects.all(),
        }

    def get_form_extra_kwargs__tags(self):
        return {
            'queryset': Tag.objects.all(),
        }

    def get_initial__cabinets(self):
        document = self.object
        return {
            'cabinets': document.cabinets.all(),
        }

    def get_initial__metadata(self):
        document = self.object
        user = self.request.user

        metadata_queryset = AccessControlList.objects.restrict_queryset(
            queryset=document.metadata.all(),
            permission=permission_document_metadata_edit,
            user=user
        )
        existing_metadata_types = set()
        metadata = {}

        # TODO: The handling looks very complicated and may be due to the
        # "multi document" support in the edit metadata view. There is no
        # reason why for a single document there could ever by two values for a
        # given metadata type.
        for document_metadata in metadata_queryset:
            existing_metadata_types.add(document_metadata.metadata_type)
            # Metadata value cannot be None here, fallback to an empty
            # string
            value = document_metadata.value or ''
            if document_metadata.metadata_type in metadata:
                if value not in metadata[document_metadata.metadata_type]:
                    metadata[document_metadata.metadata_type].append(value)
            else:
                metadata[document_metadata.metadata_type] = [value] if value else ''

        # TODO: Check if this can be made in a more efficient query
        all_metadata_types = set(
            dtmt.metadata_type for dtmt in document.document_type.metadata.all())
        addable_metadata_types = all_metadata_types - existing_metadata_types

        for metadata_type in addable_metadata_types:
            metadata[metadata_type] = ''

        def value_to_initial(value):
            return ', '.join(value) if value else ''

        initial = []
        for key, value in metadata.items():
            value = value_to_initial(value)
            # TODO: Why can the form not get the document_metadata object?
            initial.append(
                {
                    'document_type': document.document_type,
                    'metadata_type': key,
                    'update': False,
                    'value': value,
                    'value_existing': value
                }
            )
        return initial

    def get_initial__tags(self):
        document = self.object
        return {
            'tags': document.tags.all(),
        }

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
            'title': _('Pre process document'),
            'subtitle': document.label,
            'extra_buttons': [
                {
                    'name': 'button-refresh-document-type',
                    'label': _('Refresh document type'),
                },
            ],
            'subtemplates_list': [
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['preview'],
                        'title': _('Document preview'),
                        'object': document,
                        'hide_labels': True,
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['properties'],
                        'title': _('Document properties'),
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['cabinets'],
                        'title': _('Document cabinets'),
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['tags'],
                        'title': _('Document tags'),
                    },
                },
                {
                    'name': 'botech/appearance/generic_form_group_subtemplate.html',
                    'context': {
                        'form': forms['metadata'],
                        'form_display_mode_table': True,
                        'title': _('Document metadata'),
                    },
                },
            ]
        })
        return context


def _exception_to_message(error):
    """
    Transform a given exception to a message.
    """
    if isinstance(error, ValidationError):
        exception_message = ', '.join(error.messages)
    else:
        exception_message = force_text(s=error)
