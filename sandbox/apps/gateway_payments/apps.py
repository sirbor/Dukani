from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GatewayPaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gateway_payments"
    label = "gateway_payments"
    verbose_name = _("Gateway payments (M-Pesa & PayPal)")
