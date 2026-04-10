from django.urls import path

from oscar.apps.dashboard import apps
from oscar.core.loading import get_class


class DashboardConfig(apps.DashboardConfig):
    name = "tests._site.apps.dashboard"

    def configure_permissions(self):
        super().configure_permissions()
        DashboardPermission = get_class("dashboard.permissions", "DashboardPermission")
        self.permissions_map["storefront-branding"] = (DashboardPermission.staff,)

    def get_urls(self):
        from apps.storefront_settings.views import StorefrontBrandingView

        urls = [
            path(
                "storefront-branding/",
                StorefrontBrandingView.as_view(),
                name="storefront-branding",
            ),
        ]
        self.post_process_urls(urls)
        return urls + super().get_urls()
