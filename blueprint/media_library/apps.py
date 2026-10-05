from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = "blueprint.media_library"
    label = "dbp_media_library"
    verbose_name = _("Media Library")
