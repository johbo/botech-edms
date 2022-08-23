from django.conf.urls import url

from .views import MySimpleView


urlpatterns = [
    url(
        regex=r'^documents/(?P<document_id>\d+)/my-simple-view/$',
        name='document_my_simple_view', view=MySimpleView.as_view()
    ),
]
