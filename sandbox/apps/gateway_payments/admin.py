from django.contrib import admin

from .models import PaymentCallbackLog, PaymentIntent


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gateway",
        "status",
        "order_number",
        "manual_confirmation_code",
        "amount",
        "currency",
        "created_at",
        "order",
    )
    list_filter = ("gateway", "status", "currency")
    search_fields = (
        "order_number",
        "mpesa_receipt",
        "paypal_order_id",
        "phone_number",
        "manual_confirmation_code",
        "manual_account_number",
    )
    readonly_fields = ("created_at", "updated_at", "callback_payload")
    raw_id_fields = ("user", "order")


@admin.register(PaymentCallbackLog)
class PaymentCallbackLogAdmin(admin.ModelAdmin):
    list_display = ("id", "gateway", "created_at")
    list_filter = ("gateway",)
