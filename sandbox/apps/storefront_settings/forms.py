from django import forms
from django.utils.translation import gettext_lazy as _

from .models import StorefrontBranding


class StorefrontBrandingForm(forms.ModelForm):
    clear_logo = forms.BooleanField(
        label=_("Remove logo"),
        required=False,
        help_text=_("Revert to the default static site logo."),
    )

    field_order = [
        "shop_name",
        "store_type",
        "shop_tagline",
        "logo",
        "clear_logo",
        "home_hero_eyebrow",
        "home_hero_title",
        "home_hero_lede",
        "announcement_badge_label",
        "announcement_line_1",
        "announcement_icon_1",
        "announcement_line_2",
        "announcement_icon_2",
        "announcement_line_3",
        "announcement_icon_3",
        "nav_background",
        "book_room_background",
        "department_background_1",
        "department_background_2",
        "department_background_3",
        "department_background_4",
    ]

    class Meta:
        model = StorefrontBranding
        fields = [
            "shop_name",
            "store_type",
            "shop_tagline",
            "logo",
            "home_hero_eyebrow",
            "home_hero_title",
            "home_hero_lede",
            "announcement_badge_label",
            "announcement_line_1",
            "announcement_icon_1",
            "announcement_line_2",
            "announcement_icon_2",
            "announcement_line_3",
            "announcement_icon_3",
            "nav_background",
            "book_room_background",
            "department_background_1",
            "department_background_2",
            "department_background_3",
            "department_background_4",
        ]
