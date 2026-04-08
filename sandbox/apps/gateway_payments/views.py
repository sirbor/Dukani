import json
import logging

from django.conf import settings as django_settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.checkout.session import CheckoutSessionMixin
from oscar.apps.checkout.utils import CheckoutSessionData

from .forms import ManualConfirmationForm, MpesaPhoneForm
from .models import PaymentCallbackLog, PaymentIntent
from .placement import place_order_for_intent
from .services import DarajaClient, DarajaError, PayPalClient, PayPalError
from .url_building import build_public_absolute_uri

logger = logging.getLogger(__name__)

CHECKOUT_PAY_PRE = [
    "check_basket_is_not_empty",
    "check_basket_is_valid",
    "check_user_email_is_captured",
    "check_shipping_data_is_captured",
]

# After freeze_basket(), `request.basket` is a new empty open basket; do not
# require lines on it (submitted basket id remains in session).
CHECKOUT_PAY_FROZEN_PRE = [
    "check_user_email_is_captured",
    "check_shipping_data_is_captured",
]


def _parse_stk_callback_payload(data: dict):
    cb = data.get("Body", {}).get("stkCallback", {})
    result_code = cb.get("ResultCode")
    mri = cb.get("MerchantRequestID") or ""
    cri = cb.get("CheckoutRequestID") or ""
    receipt = None
    if result_code == 0:
        for item in cb.get("CallbackMetadata", {}).get("Item", []):
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = str(item.get("Value", ""))
    desc = cb.get("ResultDesc") or ""
    return result_code, mri, cri, receipt, desc, cb


class MpesaStartView(OrderPlacementMixin, FormView):
    template_name = "gateway_payments/mpesa.html"
    form_class = MpesaPhoneForm
    pre_conditions = CHECKOUT_PAY_PRE
    skip_conditions = ["skip_unless_payment_is_required"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submission = self.build_submission()
        ctx["order_total"] = submission.get("order_total")
        return ctx

    def form_valid(self, form):
        basket = self.request.basket
        submission = self.build_submission()
        total = submission["order_total"]
        if not total:
            messages.error(self.request, _("Could not calculate order total."))
            return self.form_invalid(form)

        if str(total.currency).upper() != "KES":
            messages.error(
                self.request,
                _("Lipa na M-Pesa is only available when the basket total is in KES."),
            )
            return self.form_invalid(form)

        amount_int = int(total.incl_tax)
        if amount_int < 1:
            messages.error(self.request, _("Amount must be at least 1 KES."))
            return self.form_invalid(form)

        order_number = str(self.generate_order_number(basket))
        self.checkout_session.set_order_number(order_number)
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        intent = PaymentIntent.objects.create(
            gateway=PaymentIntent.Gateway.MPESA,
            status=PaymentIntent.Status.PROCESSING,
            order_number=order_number,
            basket_id=basket.id,
            user=self.request.user if self.request.user.is_authenticated else None,
            amount=total.incl_tax,
            currency=str(total.currency),
            phone_number=form.cleaned_data["phone"],
        )

        callback_url = build_public_absolute_uri(
            self.request, reverse("gateway_payments:mpesa_callback")
        )
        try:
            client = DarajaClient()
            res = client.stk_push(
                phone_msisdn=form.cleaned_data["phone"],
                amount=amount_int,
                account_reference=order_number[:12],
                transaction_desc=f"{django_settings.OSCAR_SHOP_NAME} order",
                callback_url=callback_url,
            )
        except DarajaError as exc:
            logger.info("Daraja STK failed: %s", exc)
            self.restore_frozen_basket()
            intent.status = PaymentIntent.Status.FAILED
            intent.failure_reason = str(exc)
            intent.save(update_fields=["status", "failure_reason", "updated_at"])
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        intent.mpesa_merchant_request_id = res.get("MerchantRequestID", "")
        intent.mpesa_checkout_request_id = res.get("CheckoutRequestID", "")
        intent.callback_payload = {"stk_initiate": res.get("raw", {})}
        intent.save(
            update_fields=[
                "mpesa_merchant_request_id",
                "mpesa_checkout_request_id",
                "callback_payload",
                "updated_at",
            ]
        )
        return redirect("gateway_payments:mpesa_wait", pk=intent.pk)


class MpesaWaitView(CheckoutSessionMixin, TemplateView):
    template_name = "gateway_payments/mpesa_wait.html"
    pre_conditions = CHECKOUT_PAY_FROZEN_PRE
    # No skip_conditions: frozen basket is empty so "payment required" totals are wrong here.
    skip_conditions = []

    def get(self, request, *args, **kwargs):
        self.intent = get_object_or_404(PaymentIntent, pk=kwargs["pk"])
        if self.intent.gateway != PaymentIntent.Gateway.MPESA:
            return redirect("checkout:payment-details")
        if self.checkout_session.get_order_number() != self.intent.order_number:
            messages.error(request, _("This payment does not match your checkout session."))
            return redirect("checkout:payment-details")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["intent"] = self.intent
        ctx["status_url"] = reverse(
            "gateway_payments:intent_status", kwargs={"pk": self.intent.pk}
        )
        ctx["complete_url"] = reverse(
            "gateway_payments:intent_complete", kwargs={"pk": self.intent.pk}
        )
        return ctx


class ManualPayStartView(OrderPlacementMixin, View):
    """Create a manual Paybill payment intent and send customer to instructions."""

    pre_conditions = CHECKOUT_PAY_PRE
    skip_conditions = ["skip_unless_payment_is_required"]

    def get(self, request, *args, **kwargs):
        basket = request.basket
        submission = self.build_submission()
        total = submission["order_total"]
        if not total:
            messages.error(request, _("Could not calculate order total."))
            return redirect("checkout:payment-details")
        if str(total.currency).upper() != "KES":
            messages.error(
                request,
                _("Manual Paybill payment is only available when the total is in KES."),
            )
            return redirect("checkout:payment-details")
        if total.is_tax_known:
            amount = total.incl_tax
        else:
            amount = total.excl_tax
        if amount is None or amount < 1:
            messages.error(request, _("Amount must be at least 1 KES."))
            return redirect("checkout:payment-details")

        paybill = (getattr(django_settings, "MANUAL_MPESA_PAYBILL", None) or "").strip()
        account = (getattr(django_settings, "MANUAL_MPESA_ACCOUNT", None) or "").strip()
        if not paybill or not account:
            messages.error(
                request,
                _("Manual Paybill is not configured. Please contact the shop."),
            )
            return redirect("checkout:payment-details")

        order_number = str(self.generate_order_number(basket))
        self.checkout_session.set_order_number(order_number)
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        intent = PaymentIntent.objects.create(
            gateway=PaymentIntent.Gateway.MANUAL,
            status=PaymentIntent.Status.PROCESSING,
            order_number=order_number,
            basket_id=basket.id,
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            currency=str(total.currency),
            manual_paybill=paybill,
            manual_account_number=account,
        )
        return redirect("gateway_payments:manual_confirm", pk=intent.pk)


class ManualPayConfirmView(OrderPlacementMixin, FormView):
    """Show Paybill instructions and collect M-Pesa confirmation code."""

    template_name = "gateway_payments/manual_mpesa.html"
    form_class = ManualConfirmationForm
    pre_conditions = CHECKOUT_PAY_FROZEN_PRE
    skip_conditions = []

    def dispatch(self, request, *args, **kwargs):
        self.pay_intent = get_object_or_404(PaymentIntent, pk=kwargs["pk"])
        if self.pay_intent.gateway != PaymentIntent.Gateway.MANUAL:
            return redirect("checkout:payment-details")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.checkout_session.get_order_number() != self.pay_intent.order_number:
            messages.error(
                request, _("This payment does not match your checkout session.")
            )
            return redirect("checkout:payment-details")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.checkout_session.get_order_number() != self.pay_intent.order_number:
            messages.error(
                request, _("This payment does not match your checkout session.")
            )
            return redirect("checkout:payment-details")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pay_intent"] = self.pay_intent
        return ctx

    def form_valid(self, form):
        intent = PaymentIntent.objects.get(pk=self.pay_intent.pk)
        if intent.status != PaymentIntent.Status.PROCESSING:
            if intent.status == PaymentIntent.Status.SUCCEEDED and intent.order_id:
                return place_order_for_intent(self.request, intent)
            messages.error(
                self.request, _("This payment can no longer be completed.")
            )
            return redirect("checkout:payment-details")

        intent.manual_confirmation_code = form.cleaned_data["confirmation_code"]
        intent.status = PaymentIntent.Status.SUCCEEDED
        intent.save(
            update_fields=[
                "manual_confirmation_code",
                "status",
                "updated_at",
            ]
        )
        return place_order_for_intent(self.request, intent)


class PayPalStartView(OrderPlacementMixin, View):
    pre_conditions = CHECKOUT_PAY_PRE
    skip_conditions = ["skip_unless_payment_is_required"]

    def get(self, request, *args, **kwargs):
        basket = request.basket
        submission = self.build_submission()
        total = submission["order_total"]
        if not total or total.incl_tax <= 0:
            messages.error(request, _("Could not calculate order total."))
            return redirect("checkout:payment-details")

        order_number = str(self.generate_order_number(basket))
        self.checkout_session.set_order_number(order_number)
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        intent = PaymentIntent.objects.create(
            gateway=PaymentIntent.Gateway.PAYPAL,
            status=PaymentIntent.Status.PROCESSING,
            order_number=order_number,
            basket_id=basket.id,
            user=request.user if request.user.is_authenticated else None,
            amount=total.incl_tax,
            currency=str(total.currency),
        )

        return_url = build_public_absolute_uri(
            request, reverse("gateway_payments:paypal_return")
        )
        cancel_url = build_public_absolute_uri(
            request, reverse("gateway_payments:paypal_cancel")
        )

        try:
            client = PayPalClient()
            res = client.create_order(
                amount=total.incl_tax,
                currency_code=str(total.currency),
                reference=order_number,
                return_url=return_url,
                cancel_url=cancel_url,
            )
        except PayPalError as exc:
            self.restore_frozen_basket()
            intent.status = PaymentIntent.Status.FAILED
            intent.failure_reason = str(exc)
            intent.save(update_fields=["status", "failure_reason", "updated_at"])
            messages.error(request, str(exc))
            return redirect("checkout:payment-details")

        intent.paypal_order_id = res["id"]
        intent.callback_payload = {"create": res.get("raw", {})}
        intent.save(update_fields=["paypal_order_id", "callback_payload", "updated_at"])
        return redirect(res["approve"])


class PayPalReturnView(OrderPlacementMixin, View):
    """PayPal redirects here with ?token=PAYPAL_ORDER_ID after customer approves."""

    pre_conditions = CHECKOUT_PAY_FROZEN_PRE

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        if not token:
            messages.error(request, _("Missing PayPal confirmation."))
            return redirect("checkout:payment-details")

        intent = PaymentIntent.objects.filter(
            paypal_order_id=token,
            gateway=PaymentIntent.Gateway.PAYPAL,
        ).first()
        if not intent:
            messages.error(request, _("Payment record not found."))
            return redirect("checkout:payment-details")

        if self.checkout_session.get_order_number() != intent.order_number:
            messages.error(request, _("Checkout session does not match PayPal payment."))
            return redirect("checkout:payment-details")

        if intent.status == PaymentIntent.Status.SUCCEEDED:
            return place_order_for_intent(request, intent)

        try:
            cap = PayPalClient().capture_order(token)
        except PayPalError as exc:
            logger.info("PayPal capture failed: %s", exc)
            intent.status = PaymentIntent.Status.FAILED
            intent.failure_reason = str(exc)
            intent.save(update_fields=["status", "failure_reason", "updated_at"])
            self.restore_frozen_basket()
            messages.error(request, str(exc))
            return redirect("checkout:payment-details")

        intent.status = PaymentIntent.Status.SUCCEEDED
        intent.paypal_capture_id = cap.get("capture_id", "")
        intent.callback_payload = {
            **(intent.callback_payload or {}),
            "capture": cap.get("raw", {}),
        }
        intent.save(
            update_fields=[
                "status",
                "paypal_capture_id",
                "callback_payload",
                "updated_at",
            ]
        )
        return place_order_for_intent(request, intent)


class PayPalCancelView(OrderPlacementMixin, View):
    pre_conditions = CHECKOUT_PAY_FROZEN_PRE

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        order_number = self.checkout_session.get_order_number()
        qs = PaymentIntent.objects.filter(
            gateway=PaymentIntent.Gateway.PAYPAL,
            status=PaymentIntent.Status.PROCESSING,
        )
        if token:
            qs = qs.filter(paypal_order_id=token)
        if order_number:
            qs = qs.filter(order_number=order_number)
        intent = qs.order_by("-created_at").first()
        if intent:
            intent.status = PaymentIntent.Status.CANCELLED
            intent.save(update_fields=["status", "updated_at"])
        self.restore_frozen_basket()
        messages.info(request, _("PayPal checkout was cancelled."))
        return redirect("checkout:payment-details")


class GatewayCompleteView(View):
    """Finalize Oscar order after M-Pesa success (POST from wait page)."""

    http_method_names = ["post"]

    def post(self, request, pk):
        intent = get_object_or_404(PaymentIntent, pk=pk)
        if intent.status != PaymentIntent.Status.SUCCEEDED:
            messages.error(request, _("Payment is not confirmed yet."))
            return redirect("gateway_payments:mpesa_wait", pk=intent.pk)
        return place_order_for_intent(request, intent)


def intent_status(request, pk):
    intent = get_object_or_404(PaymentIntent, pk=pk)
    cs = CheckoutSessionData(request)
    if cs.get_order_number() != intent.order_number:
        return JsonResponse({"error": "forbidden"}, status=403)
    data = {
        "status": intent.status,
        "failure_reason": intent.failure_reason,
        "order_id": intent.order_id,
        "receipt": intent.mpesa_receipt,
    }
    return JsonResponse(data)


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning("M-Pesa callback: invalid JSON")
        return HttpResponse(json.dumps({"ResultCode": 1, "ResultDesc": "Invalid JSON"}))

    PaymentCallbackLog.objects.create(
        gateway="mpesa",
        body_text=request.body.decode("utf-8", errors="replace")[:10000],
        headers_summary={"content_type": request.META.get("CONTENT_TYPE", "")},
    )

    rc, mri, cri, receipt, desc, cb = _parse_stk_callback_payload(payload)
    intent = None
    if cri:
        intent = PaymentIntent.objects.filter(
            mpesa_checkout_request_id=cri,
            gateway=PaymentIntent.Gateway.MPESA,
        ).first()
    if intent is None and mri:
        intent = PaymentIntent.objects.filter(
            mpesa_merchant_request_id=mri,
            gateway=PaymentIntent.Gateway.MPESA,
        ).first()

    if intent:
        intent.callback_payload = {
            **(intent.callback_payload or {}),
            "stk_result": cb,
        }
        if rc == 0:
            intent.status = PaymentIntent.Status.SUCCEEDED
            intent.mpesa_receipt = receipt or ""
        else:
            intent.status = PaymentIntent.Status.FAILED
            intent.failure_reason = desc or f"M-Pesa result {rc}"
        intent.save(
            update_fields=[
                "status",
                "mpesa_receipt",
                "failure_reason",
                "callback_payload",
                "updated_at",
            ]
        )

    # Ack body expected by Safaricom (ResultCode 0 = acknowledge)
    body = {"ResultCode": 0, "ResultDesc": "Accepted"}
    return HttpResponse(
        json.dumps(body),
        content_type="application/json",
        status=200,
    )
