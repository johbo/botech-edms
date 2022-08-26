from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.converter.layers import layer_decorations
from mayan.apps.converter.transformations import BaseTransformation
from mayan.apps.metadata.models import DocumentMetadata
from mayan.apps.views.forms import Form

from .settings import (
    setting_acct_assignment,
    setting_acct_booked_date,
    setting_acct_doc_number,
)
from .transformation_mixins import TransformationStampAccountingMetadataMixin


class TransformationStampAccountingMetadata(
        TransformationStampAccountingMetadataMixin,
        BaseTransformation):
    """
    Stamp accounting related metadata into the document.
    """

    # TODO: There is an issue if there are no arguments.
    # I assume that setting and saving the arguments is a step which also does some
    # sort of cache invalidation. Probably without arguments this is not correctly
    # triggered. Needs investigation and fix.
    arguments = ('fake_argument',)
    label = _('Stamp accounting metadata')
    name = 'stamp_accounting'

    class Form(Form):
        fake_argument = forms.IntegerField(
            widget=forms.HiddenInput,
            required=False)

    # TODO: check if it can be removed
    # Seems to have in this class the role to prepare arguments. Without arguments this
    # may not be needed at all here.
    def execute_on(self, *args, **kwargs):
        # Prepare all arguments
        super().execute_on(*args, **kwargs)
        self._prepare_arguments()

        # Let the mixin do the work
        return self.stamp_accounting_data(self.image)

    def _prepare_arguments(self):

        document = self.get_document()
        document_metadata = document.metadata

        def metadata_value(type_name):
            try:
                return document_metadata.get(
                    metadata_type__name=type_name).value
            except DocumentMetadata.DoesNotExist as e:
                # TODO: This case is exceptional, work on better handling of this
                # situation.
                return ''

        self.acct_doc_number = metadata_value(setting_acct_doc_number.value)
        self.acct_booked_stamp = 'BOOKED ' + metadata_value(
            setting_acct_booked_date.value)
        self.acct_assignment = metadata_value(setting_acct_assignment.value)


    def get_document(self):
        """
        Get the Document instance to which this transformation is applied.
        """

        file_or_version_page = self.object_layer.content_object
        document = _document_from_file_or_version_page(file_or_version_page)
        return document

# TODO: This should be provided by the page model to get the parent.
# This is internal knowledge of the documents app and should be moved
# into the mayan-edms repository.
def _document_from_file_or_version_page(file_or_version_page):
        page_parent = _page_parent(file_or_version_page)
        document = page_parent.document
        return document

def _page_parent(file_or_version_page):
    parent_attr = file_or_version_page._paged_model_parent_field
    return getattr(file_or_version_page, parent_attr)



BaseTransformation.register(
    layer=layer_decorations,
    transformation=TransformationStampAccountingMetadata
)
