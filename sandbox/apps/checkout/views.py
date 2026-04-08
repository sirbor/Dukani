from django.urls import reverse_lazy
from django.views.generic import TemplateView

from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.apps.checkout.views import (
    IndexView,
    PaymentDetailsView,
    PaymentMethodView,
    ShippingAddressView,
    ThankYouView,
    UserAddressDeleteView,
    UserAddressUpdateView,
)
from oscar.apps.checkout.views import ShippingMethodView as OscarShippingMethodView


class ShippingMethodView(OscarShippingMethodView):
    """After choosing shipping, require order review before payment."""

    success_url = reverse_lazy("checkout:order-review")


class OrderReviewView(CheckoutSessionMixin, TemplateView):
    """
    Pre-payment summary (lines, shipping, totals). External gateways place
    the Oscar order after payment, so Oscar's /preview/ step is never shown;
    this page restores an explicit review step in the checkout journey.
    """

    template_name = "oscar/checkout/order_review.html"
    pre_conditions = PaymentDetailsView.pre_conditions


__all__ = [
    "IndexView",
    "OrderReviewView",
    "PaymentDetailsView",
    "PaymentMethodView",
    "ShippingAddressView",
    "ShippingMethodView",
    "ThankYouView",
    "UserAddressDeleteView",
    "UserAddressUpdateView",
]
