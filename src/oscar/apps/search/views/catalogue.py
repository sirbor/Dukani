# pylint: disable=E1101
from urllib.parse import quote

from django.contrib import messages
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect
from django.db import DatabaseError
from django.utils.translation import gettext_lazy as _

from oscar.apps.catalogue.category_resolution import category_is_in_storefront_books_tree
from oscar.core.loading import get_class, get_model

BrowseCategoryForm = get_class("search.forms", "BrowseCategoryForm")
DepartmentBrowseCategoryForm = get_class(
    "search.forms", "DepartmentBrowseCategoryForm"
)
CategoryForm = get_class("search.forms", "CategoryForm")
BaseSearchView = get_class("search.views.base", "BaseSearchView")
Category = get_model("catalogue", "Category")
ConditionalOffer = get_model("offer", "ConditionalOffer")


class CatalogueView(BaseSearchView):
    """
    Browse all products in the catalogue
    """

    form_class = DepartmentBrowseCategoryForm
    context_object_name = "products"
    template_name = "oscar/catalogue/browse.html"
    enforce_paths = True

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            # Redirect to page one.
            messages.error(request, _("The given page number was invalid."))
            return redirect("catalogue:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            from oscar.apps.catalogue.category_resolution import (
                resolve_storefront_browse_categories,
            )

            categories = resolve_storefront_browse_categories()
        except (DatabaseError, TypeError, ValueError):
            categories = None
        if categories is not None:
            kwargs["categories"] = categories
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["summary"] = _("Books")
        ctx["offers"] = ConditionalOffer.active.filter(offer_type=ConditionalOffer.SITE)
        return ctx


class ProductCategoryView(BaseSearchView):
    """
    Browse products in a given category
    """

    form_class = CategoryForm
    enforce_paths = True
    context_object_name = "products"
    template_name = "oscar/catalogue/category.html"

    def get(self, request, *args, **kwargs):
        # pylint: disable=W0201
        self.category = self.get_category()

        # Allow staff members so they can test layout etc.
        if not self.is_viewable(self.category, request):
            raise Http404()

        potential_redirect = self.redirect_if_necessary(request.path, self.category)
        if potential_redirect is not None:
            return potential_redirect

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.error(request, _("The given page number was invalid."))
            return redirect(self.category.get_absolute_url())

    def is_viewable(self, category, request):
        if not category.is_public and not request.user.is_staff:
            return False
        if request.user.is_staff:
            return True
        return category_is_in_storefront_books_tree(category)

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            # Categories are fetched by primary key to allow slug changes.
            # If the slug has changed, issue a redirect.
            expected_path = category.get_absolute_url()
            if expected_path != quote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_category(self):
        return get_object_or_404(Category, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["summary"] = self.category.name
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["categories"] = self.category.get_descendants_and_self()
        return kwargs
