from django.conf.urls import url

from .views import AccountingDocumentEditView


urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/accounting/$',
        name='document_acct_edit_view', view=AccountingDocumentEditView.as_view()
    ),
]
