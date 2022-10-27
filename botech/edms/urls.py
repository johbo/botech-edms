from django.conf.urls import url

from .views import (
    AccountingDocumentEditView,
    PreProcessDocumentEditView,
)


urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/accounting/$',
        name='document_acct_edit_view', view=AccountingDocumentEditView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/pre-process/$',
        name='document_pre_process_view', view=PreProcessDocumentEditView.as_view()
    ),
]
