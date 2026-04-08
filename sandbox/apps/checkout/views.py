from django.urls import reverse_lazy

from oscar.apps.checkout.views import (
    IndexView,
    PaymentDetailsView as OscarPaymentDetailsView,
    PaymentMethodView as OscarPaymentMethodView,
    ShippingAddressView,
    ThankYouView,
    UserAddressDeleteView,
    UserAddressUpdateView,
)
from oscar.apps.checkout.views import ShippingMethodView as OscarShippingMethodView


class ShippingMethodView(OscarShippingMethodView):
    """After choosing shipping, go to payment method."""

    success_url = reverse_lazy("checkout:payment-method")


class PaymentMethodView(OscarPaymentMethodView):
    """After choosing payment method, go to payment-details."""

    success_url = reverse_lazy("checkout:payment-details")


class PaymentDetailsView(OscarPaymentDetailsView):
    """
    Pre-payment summary (lines, shipping, totals).
    """

    template_name_preview = "oscar/checkout/sandbox_order_review.html"


__all__ = [
    "IndexView",
    "PaymentDetailsView",
    "PaymentMethodView",
    "ShippingAddressView",
    "ShippingMethodView",
    "ThankYouView",
    "UserAddressDeleteView",
    "UserAddressUpdateView",
]
