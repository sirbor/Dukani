from django.contrib import admin

from .models import StorefrontBranding


@admin.register(StorefrontBranding)
class StorefrontBrandingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not StorefrontBranding.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
