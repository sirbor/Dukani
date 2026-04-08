from django import template
from django.apps import apps

register = template.Library()


def _PaymentIntent():
    return apps.get_model("gateway_payments", "PaymentIntent")


def _gateway_label(intent, PaymentIntent):
    if intent.gateway == PaymentIntent.Gateway.MPESA:
        return "Lipa na M-Pesa (STK)"
    if intent.gateway == PaymentIntent.Gateway.PAYPAL:
        return "PayPal"
    if intent.gateway == PaymentIntent.Gateway.MANUAL:
        return "M-Pesa Paybill (manual)"
    return intent.get_gateway_display()


def _row_for_intent(intent, PaymentIntent):
    paid = intent.status == PaymentIntent.Status.SUCCEEDED
    confirmation_code = ""
    detail = ""

    if intent.gateway == PaymentIntent.Gateway.MANUAL:
        confirmation_code = (intent.manual_confirmation_code or "").strip()
        detail = "Paybill {} · Acc {}".format(
            intent.manual_paybill or "—",
            intent.manual_account_number or "—",
        )
    elif intent.gateway == PaymentIntent.Gateway.MPESA:
        confirmation_code = (intent.mpesa_receipt or "").strip()
    elif intent.gateway == PaymentIntent.Gateway.PAYPAL:
        confirmation_code = (
            intent.paypal_capture_id or intent.paypal_order_id or ""
        ).strip()

    return {
        "method": _gateway_label(intent, PaymentIntent),
        "status": intent.get_status_display(),
        "paid": paid,
        "confirmation_code": confirmation_code or "—",
        "detail": detail,
        "amount": intent.amount,
        "currency": intent.currency,
    }


@register.inclusion_tag("gateway_payments/dashboard/order_gateway_panel.html")
def order_gateway_payments(order):
    """Staff dashboard: gateway payment records for this order (method, paid, confirmation)."""
    PaymentIntent = _PaymentIntent()
    if order is None or not getattr(order, "pk", None):
        return {"rows": []}
    intents = (
        PaymentIntent.objects.filter(order=order)
        .order_by("-created_at")
        .only(
            "gateway",
            "status",
            "amount",
            "currency",
            "manual_confirmation_code",
            "manual_paybill",
            "manual_account_number",
            "mpesa_receipt",
            "paypal_order_id",
            "paypal_capture_id",
        )
    )
    return {"rows": [_row_for_intent(i, PaymentIntent) for i in intents]}
