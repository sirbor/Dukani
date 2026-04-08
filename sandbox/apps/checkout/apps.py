from django.urls import path
from django.utils.translation import gettext_lazy as _

from oscar.apps.checkout.apps import CheckoutConfig as OscarCheckoutConfig


class CheckoutConfig(OscarCheckoutConfig):
    name = "apps.checkout"
    label = "checkout"
    verbose_name = _("Checkout")

    def ready(self):
        super().ready()
        from .views import PaymentMethodView, PaymentDetailsView

        self.payment_method_view = PaymentMethodView
        self.payment_details_view = PaymentDetailsView


    def get_urls(self):
        return super().get_urls()
