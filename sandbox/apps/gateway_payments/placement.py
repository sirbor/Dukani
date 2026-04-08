import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from oscar.core.loading import get_class, get_model

Applicator = get_class("offer.applicator", "Applicator")

from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.checkout.utils import CheckoutSessionData

from .models import PaymentIntent

logger = logging.getLogger(__name__)

Source = None
SourceType = None


def _models():
    global Source, SourceType
    if Source is None:
        Source = get_model("payment", "Source")
        SourceType = get_model("payment", "SourceType")
    return Source, SourceType


def attach_gateway_payment_source(placer: OrderPlacementMixin, intent: PaymentIntent):
    Source, SourceType = _models()
    if intent.gateway == PaymentIntent.Gateway.MPESA:
        name = "M-Pesa"
        ref = intent.mpesa_receipt or intent.order_number
        label = intent.phone_number[:128]
    elif intent.gateway == PaymentIntent.Gateway.PAYPAL:
        name = "PayPal"
        ref = intent.paypal_capture_id or intent.paypal_order_id or intent.order_number
        label = "PayPal"
    else:
        name = "M-Pesa Paybill"
        ref = intent.manual_confirmation_code or intent.order_number
        label = f"Paybill {intent.manual_paybill} · Acc {intent.manual_account_number}"
        label = label[:128]
    st, _ = SourceType.objects.get_or_create(name=name)
    src = Source(
        source_type=st,
        currency=intent.currency,
        amount_allocated=intent.amount,
        amount_debited=intent.amount,
        reference=str(ref)[:255],
        label=label[:128],
    )
    placer.add_payment_source(src)
    placer.add_payment_event("Paid", intent.amount, reference=str(ref)[:128])


def place_order_for_intent(request, intent: PaymentIntent):
    """
    Create the Oscar order after gateway payment succeeded. Idempotent if
    intent.order is already set.
    Note: `handle_successful_order` flushes checkout session — only call once.
    """
    if intent.order_id:
        request.session["checkout_order_id"] = intent.order_id
        return HttpResponseRedirect(_thank_you_url())

    checkout_session = CheckoutSessionData(request)
    if checkout_session.get_order_number() != intent.order_number:
        logger.warning(
            "Payment intent order_number mismatch session for intent %s", intent.pk
        )
        messages.error(
            request,
            _("Your checkout session does not match this payment. Please contact support."),
        )
        return redirect("checkout:payment-details")

    basket_id = checkout_session.get_submitted_basket_id()
    if not basket_id or basket_id != intent.basket_id:
        messages.error(
            request,
            _("Your basket does not match this payment. Try starting checkout again."),
        )
        return redirect("checkout:payment-details")

    Basket = get_model("basket", "Basket")
    try:
        basket = Basket.objects.get(pk=basket_id)
    except Basket.DoesNotExist:
        messages.error(request, _("Basket not found."))
        return redirect("checkout:payment-details")

    # Submitted basket is loaded by PK; unlike request.basket it has no strategy.
    basket.strategy = request.strategy
    Applicator().apply(basket, request.user, request)

    placer = OrderPlacementMixin()
    placer.request = request
    placer.checkout_session = checkout_session
    placer._payment_sources = None
    placer._payment_events = None

    submission = placer.build_submission(basket=basket)
    attach_gateway_payment_source(placer, intent)

    try:
        order = placer.place_order(
            order_number=intent.order_number,
            user=submission["user"],
            basket=basket,
            shipping_address=submission["shipping_address"],
            shipping_method=submission["shipping_method"],
            shipping_charge=submission["shipping_charge"],
            billing_address=submission["billing_address"],
            order_total=submission["order_total"],
            surcharges=submission.get("surcharges"),
        )
    except Exception as exc:
        logger.exception("Order placement failed for intent %s: %s", intent.pk, exc)
        messages.error(
            request,
            _("Payment was received but we could not create your order. Our team has been notified."),
        )
        return redirect("checkout:payment-details")

    intent.order = order
    intent.save(update_fields=["order", "updated_at"])
    basket.submit()

    if intent.gateway == PaymentIntent.Gateway.MANUAL:
        OrderNote = get_model("order", "OrderNote")
        msg = _(
            "M-Pesa manual — Paybill %(paybill)s, account=%(account)s, "
            "amount=%(amount)s %(currency)s, confirmation=%(code)s"
        ) % {
            "paybill": intent.manual_paybill or "-",
            "account": intent.manual_account_number or "-",
            "amount": intent.amount,
            "currency": intent.currency,
            "code": intent.manual_confirmation_code or "-",
        }
        order.notes.create(
            user=request.user if request.user.is_authenticated else None,
            message=msg,
            note_type=OrderNote.SYSTEM,
        )

    return placer.handle_successful_order(order)


def _thank_you_url():
    from django.urls import reverse

    return reverse("checkout:thank-you")
