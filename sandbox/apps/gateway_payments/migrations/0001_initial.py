import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("order", "0021_billingaddress_code_shippingaddress_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentIntent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "gateway",
                    models.CharField(
                        choices=[("mpesa", "Lipa na M-Pesa"), ("paypal", "PayPal")],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("order_number", models.CharField(db_index=True, max_length=128)),
                ("basket_id", models.PositiveIntegerField(db_index=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(max_length=12)),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        help_text="MSISDN for STK push (normalized 254… )",
                        max_length=32,
                    ),
                ),
                (
                    "mpesa_merchant_request_id",
                    models.CharField(blank=True, max_length=128),
                ),
                (
                    "mpesa_checkout_request_id",
                    models.CharField(blank=True, max_length=128),
                ),
                ("mpesa_receipt", models.CharField(blank=True, max_length=64)),
                ("paypal_order_id", models.CharField(blank=True, max_length=128)),
                ("paypal_capture_id", models.CharField(blank=True, max_length=128)),
                ("failure_reason", models.TextField(blank=True)),
                ("callback_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="gateway_payment_intents",
                        to="order.order",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payment_intents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment intent",
                "verbose_name_plural": "Payment intents",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PaymentCallbackLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("gateway", models.CharField(max_length=20)),
                ("headers_summary", models.JSONField(blank=True, default=dict)),
                ("body_text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "intent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="callback_logs",
                        to="gateway_payments.paymentintent",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="paymentintent",
            index=models.Index(
                fields=["gateway", "status"], name="gateway_pay_gateway_63ad31_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="paymentintent",
            index=models.Index(
                fields=["order_number", "gateway"],
                name="gateway_pay_order_n_0fc320_idx",
            ),
        ),
    ]
