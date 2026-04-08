from django.urls import path

from . import views

app_name = "gateway_payments"

urlpatterns = [
    path(
        "manual/start/",
        views.ManualPayStartView.as_view(),
        name="manual_pay_start",
    ),
    path(
        "manual/<int:pk>/",
        views.ManualPayConfirmView.as_view(),
        name="manual_confirm",
    ),
    path("mpesa/", views.MpesaStartView.as_view(), name="mpesa_start"),
    path("mpesa/<int:pk>/wait/", views.MpesaWaitView.as_view(), name="mpesa_wait"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("intent/<int:pk>/status/", views.intent_status, name="intent_status"),
    path("intent/<int:pk>/complete/", views.GatewayCompleteView.as_view(), name="intent_complete"),
    path("paypal/start/", views.PayPalStartView.as_view(), name="paypal_start"),
    path("paypal/return/", views.PayPalReturnView.as_view(), name="paypal_return"),
    path("paypal/cancel/", views.PayPalCancelView.as_view(), name="paypal_cancel"),
]
