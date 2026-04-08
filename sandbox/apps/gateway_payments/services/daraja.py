import base64
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class DarajaError(Exception):
    pass


class DarajaClient:
    """
    Safaricom Daraja M-Pesa Express (STK Push) — sandbox or production.
    Docs: https://developer.safaricom.co.ke
    """

    def __init__(self):
        self.consumer_key = getattr(settings, "DARAJA_CONSUMER_KEY", "") or ""
        self.consumer_secret = getattr(settings, "DARAJA_CONSUMER_SECRET", "") or ""
        self.shortcode = getattr(settings, "DARAJA_SHORTCODE", "") or ""
        self.passkey = getattr(settings, "DARAJA_PASSKEY", "") or ""
        self.env = (getattr(settings, "DARAJA_ENV", "sandbox") or "sandbox").lower()
        if self.env == "production":
            self.base = "https://api.safaricom.co.ke"
        else:
            self.base = "https://sandbox.safaricom.co.ke"

    def _token(self):
        if not self.consumer_key or not self.consumer_secret:
            raise DarajaError("Daraja consumer key/secret are not configured.")
        url = f"{self.base}/oauth/v1/generate?grant_type=client_credentials"
        r = requests.get(
            url,
            auth=(self.consumer_key, self.consumer_secret),
            timeout=30,
        )
        if r.status_code != 200:
            logger.warning("Daraja OAuth failed: %s %s", r.status_code, r.text)
            raise DarajaError("Could not obtain Daraja access token.")
        data = r.json()
        return data["access_token"]

    def stk_push(
        self,
        *,
        phone_msisdn: str,
        amount: int,
        account_reference: str,
        transaction_desc: str,
        callback_url: str,
    ):
        """
        Initiate Lipa na M-Pesa Online (STK Push).
        amount: whole shillings (integer) for KES.
        phone_msisdn: 2547XXXXXXX
        """
        if not self.shortcode or not self.passkey:
            raise DarajaError("Daraja shortcode/passkey are not configured.")

        token = self._token()
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        pwd_raw = f"{self.shortcode}{self.passkey}{ts}"
        password = base64.b64encode(pwd_raw.encode("utf-8")).decode("utf-8")

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": ts,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_msisdn,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_msisdn,
            "CallBackURL": callback_url,
            "AccountReference": account_reference[:12],
            "TransactionDesc": transaction_desc[:13],
        }

        url = f"{self.base}/mpesa/stkpush/v1/processrequest"
        r = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=45,
        )
        data = {}
        try:
            data = r.json()
        except ValueError:
            pass

        if r.status_code != 200:
            logger.warning("STK push HTTP %s: %s", r.status_code, r.text)
            raise DarajaError(data.get("errorMessage") or "STK push request failed.")

        if data.get("ResponseCode") != "0":
            msg = data.get("CustomerMessage") or data.get("errorMessage") or str(data)
            raise DarajaError(msg)

        return {
            "MerchantRequestID": data.get("MerchantRequestID", ""),
            "CheckoutRequestID": data.get("CheckoutRequestID", ""),
            "ResponseDescription": data.get("ResponseDescription", ""),
            "raw": data,
        }
