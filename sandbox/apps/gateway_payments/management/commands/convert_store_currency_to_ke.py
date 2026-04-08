"""
Alias for ``convert_store_currency_to_kes`` (GBP→KES amount conversion).

ISO 4217 code for Kenyan shilling is **KES** (not ``KE``). This module exists
so a typo-friendly command name still works.
"""

from apps.gateway_payments.management.commands.convert_store_currency_to_kes import (  # noqa: I001
    Command,
)

__all__ = ["Command"]
