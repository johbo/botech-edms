from django import forms
from django.utils.translation import ugettext_lazy as _


class CommentForm(forms.Form):

    text = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea)
