from django.urls import path
from django.utils.translation import gettext_lazy as _

from oscar.apps.checkout.apps import CheckoutConfig as OscarCheckoutConfig


class CheckoutConfig(OscarCheckoutConfig):
    name = "apps.checkout"
    label = "checkout"
    verbose_name = _("Checkout")

    def ready(self):
        super().ready()
        from .views import OrderReviewView

        self.order_review_view = OrderReviewView

    def get_urls(self):
        urls = super().get_urls()
        review_route = path(
            "order-review/",
            self.order_review_view.as_view(),
            name="order-review",
        )
        out = []
        inserted = False
        for u in urls:
            if not inserted and getattr(u, "name", None) == "payment-method":
                out.append(review_route)
                inserted = True
            out.append(u)
        if not inserted:
            out.insert(0, review_route)
        return self.post_process_urls(out)
