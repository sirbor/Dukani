from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BookstoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.bookstore"
    label = "bookstore"
    verbose_name = _("Dukani bookstore (catalogue helpers)")
