"""Build absolute URLs for payment redirects and webhooks."""

from django.conf import settings


def build_public_absolute_uri(request, path: str) -> str:
    """
    Prefer ``PUBLIC_BASE_URL`` (no trailing slash), e.g. ``https://shop.example.com``,
    so PayPal return/cancel and M-Pesa callback URLs are valid even when the browser
    ``Host`` is ``0.0.0.0``, an internal hostname, or behind a proxy that strips
    ``X-Forwarded-Host``.

    Falls back to ``request.build_absolute_uri(path)`` when unset.
    """
    base = (getattr(settings, "PUBLIC_BASE_URL", None) or "").strip().rstrip("/")
    if base:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{base}{path}"
    return request.build_absolute_uri(path)
