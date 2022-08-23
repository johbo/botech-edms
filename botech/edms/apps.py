from django.apps import apps

from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object

from .links import link_my_simple_view


class BotechEdmsConfig(MayanAppConfig):
    app_namespace = 'botech_edms'
    name = 'botech.edms'

    def ready(self):
        super().ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document')

        menu_object.bind_links(
            links=(
                link_my_simple_view,
            ), sources=(Document,)
        )