from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import gettext as _

from .models import StorefrontBranding

# Defaults match the previous hard-coded English strings in layout.html.
_ANNOUNCEMENT_DEFAULTS = (
    ("fas fa-truck", "Complimentary express delivery on curated volumes"),
    ("fas fa-star", "New titles added every week"),
    ("fas fa-th-large", "Browse the full book catalogue online"),
)


def _image_or_static(filefield, default_static_path: str) -> str:
    if filefield and getattr(filefield, "name", ""):
        return filefield.url
    return static(default_static_path)


def storefront_branding(request):
    b = StorefrontBranding.load()

    shop_name = (b.shop_name or "").strip() or settings.OSCAR_SHOP_NAME
    shop_tagline = (b.shop_tagline or "").strip() or settings.OSCAR_SHOP_TAGLINE
    store_type = b.store_type
    store_type_display = b.get_store_type_display()

    storefront_logo_url = b.logo.name and b.logo.url or ""

    storefront_home_hero_eyebrow = (b.home_hero_eyebrow or "").strip() or _("Est. 2024")
    storefront_home_hero_title = (b.home_hero_title or "").strip() or shop_name
    storefront_home_hero_lede = (b.home_hero_lede or "").strip() or _(
        "Fiction, non-fiction, and children's books chosen with care. Browse our shelves "
        "for your next read — delivered across Kenya."
    )

    storefront_nav_background_url = _image_or_static(b.nav_background, "dukani/img/background.jpg")
    storefront_book_room_background_url = _image_or_static(
        b.book_room_background, "dukani/img/bookshelf.jpg"
    )
    storefront_department_background_urls = [
        _image_or_static(b.department_background_1, "dukani/departments/dept-1.jpg"),
        _image_or_static(b.department_background_2, "dukani/departments/dept-2.jpg"),
        _image_or_static(b.department_background_3, "dukani/departments/dept-3.jpg"),
        _image_or_static(b.department_background_4, "dukani/departments/dept-4.jpg"),
    ]

    badge = (b.announcement_badge_label or "Live").strip() or "Live"

    items = []
    for i in range(3):
        default_icon, default_text = _ANNOUNCEMENT_DEFAULTS[i]
        line = getattr(b, f"announcement_line_{i + 1}") or ""
        line = line.strip() or default_text
        icon = getattr(b, f"announcement_icon_{i + 1}") or ""
        icon = (icon.strip() or default_icon).strip()
        items.append({"icon": icon, "text": line})

    return {
        "shop_name": shop_name,
        "shop_tagline": shop_tagline,
        "store_type": store_type,
        "store_type_display": store_type_display,
        "storefront_logo_url": storefront_logo_url,
        "storefront_home_hero_eyebrow": storefront_home_hero_eyebrow,
        "storefront_home_hero_title": storefront_home_hero_title,
        "storefront_home_hero_lede": storefront_home_hero_lede,
        "storefront_nav_background_url": storefront_nav_background_url,
        "storefront_book_room_background_url": storefront_book_room_background_url,
        "storefront_department_background_urls": storefront_department_background_urls,
        "announcement_badge_label": badge,
        "announcement_items": items,
    }
