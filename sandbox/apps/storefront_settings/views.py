from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .forms import StorefrontBrandingForm
from .models import StorefrontBranding


class StorefrontBrandingView(generic.FormView):
    template_name = "oscar/dashboard/storefront_branding.html"
    form_class = StorefrontBrandingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = StorefrontBranding.load()
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        if form.cleaned_data.get("clear_logo"):
            if instance.logo:
                instance.logo.delete(save=False)
            instance.logo = None
        instance.save()
        messages.success(self.request, _("Storefront appearance saved."))
        return HttpResponseRedirect(reverse("dashboard:storefront-branding"))
