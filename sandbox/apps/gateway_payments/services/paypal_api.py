import logging
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class PayPalError(Exception):
    pass


class PayPalClient:
    """
    PayPal REST API v2 (Orders create + capture).
    """

    def __init__(self):
        mode = (getattr(settings, "PAYPAL_MODE", "sandbox") or "sandbox").lower()
        self.base = (
            "https://api-m.paypal.com"
            if mode == "live"
            else "https://api-m.sandbox.paypal.com"
        )
        self.client_id = getattr(settings, "PAYPAL_CLIENT_ID", "") or ""
        self.secret = getattr(settings, "PAYPAL_CLIENT_SECRET", "") or ""

    def _token(self):
        if not self.client_id or not self.secret:
            raise PayPalError("PayPal client id/secret are not configured.")
        r = requests.post(
            f"{self.base}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.secret),
            timeout=30,
        )
        if r.status_code != 200:
            logger.warning("PayPal OAuth failed: %s %s", r.status_code, r.text)
            raise PayPalError("Could not obtain PayPal access token.")
        return r.json()["access_token"]

    def create_order(
        self,
        *,
        amount: Decimal,
        currency_code: str,
        reference: str,
        return_url: str,
        cancel_url: str,
    ):
        token = self._token()
        amt = f"{amount.quantize(Decimal('0.01')):.2f}"
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference[:127],
                    "amount": {
                        "currency_code": currency_code,
                        "value": amt,
                    },
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "user_action": "PAY_NOW",
            },
        }
        r = requests.post(
            f"{self.base}/v2/checkout/orders",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=45,
        )
        data = r.json() if r.content else {}
        if r.status_code not in (200, 201):
            logger.warning("PayPal create order failed: %s %s", r.status_code, r.text)
            detail = data.get("message") or r.text
            raise PayPalError(detail)

        approve = None
        for link in data.get("links", []):
            if link.get("rel") == "approve":
                approve = link.get("href")
                break
        if not approve:
            raise PayPalError("PayPal did not return an approval URL.")

        return {
            "id": data.get("id"),
            "approve": approve,
            "raw": data,
        }

    def capture_order(self, paypal_order_id: str):
        token = self._token()
        r = requests.post(
            f"{self.base}/v2/checkout/orders/{paypal_order_id}/capture",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        data = r.json() if r.content else {}
        if r.status_code not in (200, 201):
            logger.warning(
                "PayPal capture failed: %s %s", r.status_code, r.text[:500]
            )
            raise PayPalError(data.get("message") or "PayPal capture failed.")

        if data.get("status") != "COMPLETED":
            raise PayPalError(
                data.get("details", [{}])[0].get("description")
                or f"Unexpected PayPal status: {data.get('status')}"
            )

        capture_id = None
        try:
            caps = (
                data.get("purchase_units", [{}])[0]
                .get("payments", {})
                .get("captures", [])
            )
            if caps:
                capture_id = caps[0].get("id")
        except (IndexError, TypeError):
            pass

        return {"capture_id": capture_id or "", "raw": data}
