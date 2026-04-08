from django import template
from django.urls import NoReverseMatch, reverse

from oscar.apps.catalogue.category_resolution import (
    is_books_nav_slug,
    is_fashion_nav_slug,
    is_fashion_parent_hint,
    resolve_nav_books_category,
    resolve_nav_child_under_fashion,
    resolve_nav_fashion_category,
)
from oscar.core.loading import get_model

register = template.Library()
Category = get_model("catalogue", "category")


def _catalogue_fallback_url():
    try:
        return reverse("catalogue:index")
    except NoReverseMatch:
        return "#"


@register.simple_tag
def catalogue_browse_url():
    """Combined browse (`catalogue:index`); safe when URL names are unavailable."""
    return _catalogue_fallback_url()


@register.simple_tag
def category_url(slug, parent_slug=None):
    """
    Public URL for a category slug, optionally scoped to a parent slug
    (e.g. child slug ``clothes`` under parent ``fashion``).

    Books / Fashion / Clothes / Shoes use the same resolution as the homepage so
    nav icons always match the hero tiles even when slugs differ (e.g. clothing
    vs fashion).

    Categories use django-treebeard (MP_Node); there is no ``parent`` FK, so
    parent/child is resolved via ``get_children()``.
    """
    slug_norm = (slug or "").strip().lower()
    if not slug_norm:
        return _catalogue_fallback_url()

    if parent_slug is None:
        if is_books_nav_slug(slug_norm):
            cat = resolve_nav_books_category()
            return cat.get_absolute_url() if cat else _catalogue_fallback_url()
        if is_fashion_nav_slug(slug_norm):
            cat = resolve_nav_fashion_category()
            return cat.get_absolute_url() if cat else _catalogue_fallback_url()

    if is_fashion_parent_hint(parent_slug):
        child = resolve_nav_child_under_fashion(slug_norm)
        if child:
            return child.get_absolute_url()
        cat = (
            Category.objects.filter(slug=slug_norm, is_public=True)
            .order_by("depth")
            .first()
        )
        if cat:
            return cat.get_absolute_url()
        return _catalogue_fallback_url()

    parent = (
        Category.objects.filter(slug=parent_slug, is_public=True)
        .order_by("depth")
        .first()
    )
    if parent:
        category = parent.get_children().filter(slug=slug_norm, is_public=True).first()
        if category:
            return category.get_absolute_url()
    cat = (
        Category.objects.filter(slug=slug_norm, is_public=True)
        .order_by("depth")
        .first()
    )
    if cat:
        return cat.get_absolute_url()
    return _catalogue_fallback_url()


class PassThrough(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype):
        if obj is None:
            return self

        return getattr(obj.category, self.name)


class CategoryFieldPassThroughMetaClass(type):
    """
    Add accessors for category fields to whichever class is of this type.
    """

    def __new__(cls, name, bases, attrs):
        field_accessors = {}
        for field in Category._meta.get_fields():
            name = field.name
            field_accessors[name] = PassThrough(name)

        # attrs win of silly field accessors
        field_accessors.update(attrs)
        return type.__new__(cls, name, bases, field_accessors)


class CheapCategoryInfo(dict, metaclass=CategoryFieldPassThroughMetaClass):
    """
    Wrapper class for Category.

    Besides allowing inclusion of extra info, useful while rendering a template,
    this class hides any expensive properties people should not use by accident
    in templates.

    This replaces both the node as the info object returned by the ``category_tree``
    templatetag, so it mimics a tuple of 2 items (which are the same) for
    backwards compatibility.
    """

    def __init__(self, category, **info):
        super().__init__(info)
        self.category = category

    @property
    def pk(self):
        return self.category.pk

    def get_absolute_url(self):
        return self["url"]

    def __len__(self):
        "Mimic a tuple of 2 items"
        return 2

    def __iter__(self):
        "be an iterable of 2 times the same item"
        yield self
        yield self


@register.simple_tag(name="category_tree")
def get_annotated_list(depth=None, parent=None):
    """
    Gets an annotated list from a tree branch.

    Borrows heavily from treebeard's get_annotated_list
    """
    # 'depth' is the backwards-compatible name for the template tag,
    # 'max_depth' is the better variable name.
    max_depth = depth

    annotated_categories = []
    tree_slug = ""

    start_depth, prev_depth = (None, None)
    if parent:
        categories = parent.get_descendants()
        tree_slug = parent.get_full_slug()
        if max_depth is not None:
            max_depth += parent.get_depth()
    else:
        categories = Category.get_tree()

    if max_depth is not None:
        categories = categories.filter(depth__lte=max_depth)

    categories = categories.for_menu()

    info = CheapCategoryInfo(parent, url="")

    node_depth = 0
    for node in categories:
        node_depth = node.get_depth()
        if start_depth is None:
            start_depth = node_depth

        # Update previous node's info
        if prev_depth is None or node_depth > prev_depth:
            info["has_children"] = True
            if info.category is not None:
                tree_slug = info.category.get_full_slug(tree_slug)

        if prev_depth is not None and node_depth < prev_depth:
            depth_difference = prev_depth - node_depth
            info["num_to_close"] = list(range(0, depth_difference))
            tree_slugs = tree_slug.rsplit(node._slug_separator, depth_difference)
            if tree_slugs:
                tree_slug = tree_slugs[0]
            else:
                tree_slug = node.slug

        info = CheapCategoryInfo(
            node,
            url=node._get_absolute_url(tree_slug),
            num_to_close=[],
            level=node_depth - start_depth,
        )
        annotated_categories.append(info)

        prev_depth = node_depth

    if prev_depth is not None:
        # close last leaf
        info["num_to_close"] = list(range(0, prev_depth - start_depth))
        info["has_children"] = node_depth > prev_depth

    return annotated_categories
