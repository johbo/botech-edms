from django.apps import apps

from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object

from .links import (
    link_acct_document_edit_view,
    link_pre_process_document_edit_view,
)


class BotechEdmsConfig(MayanAppConfig):
    app_namespace = 'botech_edms'
    app_url = 'botech'
    name = 'botech.edms'

    def ready(self):
        super().ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document')

        menu_object.bind_links(
            links=(
                link_acct_document_edit_view,
            ), sources=(Document,)
        )

        menu_object.bind_links(
            links=(
                link_pre_process_document_edit_view,
            ), sources=(Document,)
        )
