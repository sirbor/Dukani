from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StorefrontSettingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.storefront_settings"
    label = "storefront_settings"
    verbose_name = _("Storefront settings")
