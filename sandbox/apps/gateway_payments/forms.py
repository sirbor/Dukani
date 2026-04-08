from django import forms
from django.utils.translation import gettext_lazy as _

from .utils import validate_ke_msisdn_for_stk


class ManualConfirmationForm(forms.Form):
    confirmation_code = forms.CharField(
        label=_("M-Pesa confirmation code"),
        max_length=64,
        min_length=4,
        help_text=_(
            "Enter the confirmation code from your M-Pesa SMS after you complete payment."
        ),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. SH86ABCD12",
                "autocomplete": "off",
            }
        ),
    )

    def clean_confirmation_code(self):
        return (self.cleaned_data.get("confirmation_code") or "").strip()


class MpesaPhoneForm(forms.Form):
    phone = forms.CharField(
        label=_("M-Pesa phone number"),
        max_length=32,
        help_text=_("Safaricom number — e.g. 07XX XXX XXX"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0712345678",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_phone(self):
        raw = self.cleaned_data.get("phone", "")
        ok, msg = validate_ke_msisdn_for_stk(raw)
        if not ok:
            raise forms.ValidationError(msg)
        return msg
