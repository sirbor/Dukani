from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentIntent(models.Model):
    """
    Tracks an in-flight or completed payment for Oscar checkout (M-Pesa / PayPal).
    Linked to the Oscar order once placement succeeds.
    """

    class Gateway(models.TextChoices):
        MPESA = "mpesa", _("Lipa na M-Pesa")
        PAYPAL = "paypal", _("PayPal")
        MANUAL = "manual", _("M-Pesa Paybill (manual)")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    gateway = models.CharField(max_length=20, choices=Gateway.choices, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    order_number = models.CharField(max_length=128, db_index=True)
    basket_id = models.PositiveIntegerField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_intents",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=12)

    phone_number = models.CharField(
        max_length=32,
        blank=True,
        help_text=_("MSISDN for STK push (normalized 254… )"),
    )
    mpesa_merchant_request_id = models.CharField(max_length=128, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=128, blank=True)
    mpesa_receipt = models.CharField(max_length=64, blank=True)

    paypal_order_id = models.CharField(max_length=128, blank=True)
    paypal_capture_id = models.CharField(max_length=128, blank=True)

    manual_paybill = models.CharField(
        max_length=32,
        blank=True,
        help_text=_("Snapshot: business paybill shown to customer."),
    )
    manual_account_number = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Snapshot: paybill account number."),
    )
    manual_confirmation_code = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text=_("M-Pesa confirmation / transaction code entered by customer."),
    )

    failure_reason = models.TextField(blank=True)
    callback_payload = models.JSONField(default=dict, blank=True)

    order = models.ForeignKey(
        "order.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gateway_payment_intents",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["gateway", "status"]),
            models.Index(fields=["order_number", "gateway"]),
        ]
        verbose_name = _("Payment intent")
        verbose_name_plural = _("Payment intents")

    def __str__(self):
        return f"{self.gateway} {self.order_number} ({self.status})"


class PaymentCallbackLog(models.Model):
    """Optional audit trail for raw gateway callbacks (debug / disputes)."""

    intent = models.ForeignKey(
        PaymentIntent,
        on_delete=models.CASCADE,
        related_name="callback_logs",
        null=True,
        blank=True,
    )
    gateway = models.CharField(max_length=20)
    headers_summary = models.JSONField(default=dict, blank=True)
    body_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
