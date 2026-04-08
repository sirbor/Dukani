import re
from typing import Tuple

from django.utils.translation import gettext_lazy as _


def normalize_ke_msisdn(raw: str) -> str:
    """Return 2547XXXXXXXX for M-Pesa STK."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    if digits.startswith("0") and len(digits) == 10:
        return "254" + digits[1:]
    if digits.startswith("7") and len(digits) == 9:
        return "254" + digits
    if digits.startswith("254"):
        return digits
    return digits


def validate_ke_msisdn_for_stk(raw: str) -> Tuple[bool, str]:
    msisdn = normalize_ke_msisdn(raw)
    if not msisdn.startswith("254") or len(msisdn) != 12:
        return False, str(_("Enter a valid Kenyan number (e.g. 07XX XXX XXX)."))
    return True, msisdn
