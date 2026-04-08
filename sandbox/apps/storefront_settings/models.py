from django.db import models
from django.utils.translation import gettext_lazy as _


class StorefrontBranding(models.Model):
    """
    Singleton (pk=1) row: public storefront name, tagline, logo, announcement bar.
    Empty fields fall back to Django settings / template defaults.
    """

    id = models.PositiveSmallIntegerField(primary_key=True, editable=False, default=1)

    shop_name = models.CharField(
        _("Store name"),
        max_length=255,
        blank=True,
        help_text=_("Shown in the header and footer. Leave blank to use Oscar settings."),
    )
    shop_tagline = models.CharField(
        _("Tagline"),
        max_length=255,
        blank=True,
        help_text=_("Used in the browser title. Leave blank to use Oscar settings."),
    )
    logo = models.ImageField(
        _("Logo"),
        upload_to="storefront/",
        blank=True,
        help_text=_("Optional. If empty, the default static logo is used."),
    )

    home_hero_eyebrow = models.CharField(
        _("Homepage hero — small line above the title"),
        max_length=160,
        blank=True,
        help_text=_('e.g. “Est. 2024”. Leave blank for the default text.'),
    )
    home_hero_title = models.CharField(
        _("Homepage hero — main headline"),
        max_length=255,
        blank=True,
        help_text=_("Usually your shop name. Leave blank to use the store name from settings."),
    )
    home_hero_lede = models.TextField(
        _("Homepage hero — supporting paragraph"),
        blank=True,
        help_text=_("One or two sentences under the headline. Leave blank for the default."),
    )

    nav_background = models.ImageField(
        _("Main navigation bar background"),
        upload_to="storefront/bg/",
        blank=True,
        help_text=_(
            "Optional. Banner behind the logo row in the header. "
            "Leave empty for the default bundled image."
        ),
    )
    book_room_background = models.ImageField(
        _('"The book room" hero tile'),
        upload_to="storefront/bg/",
        blank=True,
        help_text=_(
            "Optional. Large home hero card for books. Leave empty for the default bookshelf photo."
        ),
    )
    department_background_1 = models.ImageField(
        _("Browse by department — card 1"),
        upload_to="storefront/bg/dept/",
        blank=True,
        help_text=_("First department tile on the home page (left when four columns)."),
    )
    department_background_2 = models.ImageField(
        _("Browse by department — card 2"),
        upload_to="storefront/bg/dept/",
        blank=True,
        help_text=_("Second department tile."),
    )
    department_background_3 = models.ImageField(
        _("Browse by department — card 3"),
        upload_to="storefront/bg/dept/",
        blank=True,
        help_text=_("Third department tile."),
    )
    department_background_4 = models.ImageField(
        _("Browse by department — card 4"),
        upload_to="storefront/bg/dept/",
        blank=True,
        help_text=_("Fourth department tile."),
    )

    announcement_badge_label = models.CharField(
        _("Announcement badge label"),
        max_length=64,
        default="Live",
        help_text=_("Short label in the ticker badge (e.g. Live, News)."),
    )

    announcement_line_1 = models.CharField(_("Announcement line 1"), max_length=500, blank=True)
    announcement_icon_1 = models.CharField(
        _("Line 1 icon CSS classes"),
        max_length=128,
        default="fas fa-truck",
        help_text=_("Font Awesome classes, e.g. fas fa-truck"),
    )
    announcement_line_2 = models.CharField(_("Announcement line 2"), max_length=500, blank=True)
    announcement_icon_2 = models.CharField(
        _("Line 2 icon CSS classes"),
        max_length=128,
        default="fas fa-star",
    )
    announcement_line_3 = models.CharField(_("Announcement line 3"), max_length=500, blank=True)
    announcement_icon_3 = models.CharField(
        _("Line 3 icon CSS classes"),
        max_length=128,
        default="fas fa-th-large",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Storefront branding")
        verbose_name_plural = _("Storefront branding")

    def __str__(self):
        return _("Storefront branding")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
