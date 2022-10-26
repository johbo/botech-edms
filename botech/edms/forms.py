from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.utils import get_language_choices
from mayan.apps.metadata.forms import DocumentMetadataForm as BaseDocumentMetadataForm


class CommentForm(forms.Form):

    text = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea)

    doc_number = forms.CharField(
        label=_('ACCT Document Number'),
        required=True)

    booked_date = forms.CharField(
        label=_('ACCT Booked Date'),
        required=True)


class DocumentForm(forms.ModelForm):

    class Meta:
        fields = ('document_type', 'label', 'description', 'language')
        model = Document
        widgets = {
            'document_type': forms.Select(
                attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['language'].widget = forms.Select(
            choices=get_language_choices(), attrs={
                'class': 'select2'
            }
        )


class DocumentMetadataForm(BaseDocumentMetadataForm):

    remove = forms.BooleanField(
        initial=False, label=_('Remove'), required=False
    )

DocumentMetadataFormSet = formset_factory(form=DocumentMetadataForm, extra=0)
