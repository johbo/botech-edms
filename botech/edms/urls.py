from django.conf.urls import url

from .views import AccountingDocumentEditView, MySimpleView


urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/my-simple-view/$',
        name='document_my_simple_view', view=MySimpleView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/accounting/$',
        name='document_acct_edit_view', view=AccountingDocumentEditView.as_view()
    ),
]
