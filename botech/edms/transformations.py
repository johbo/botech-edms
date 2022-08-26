from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.converter.layers import layer_decorations
from mayan.apps.converter.transformations import BaseTransformation
from mayan.apps.views.forms import Form

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

        # Let the mixin do the work
        return super()._execute_on(self, *args, **kwargs)


BaseTransformation.register(
    layer=layer_decorations,
    transformation=TransformationStampAccountingMetadata
)
