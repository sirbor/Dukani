"""
Resolve catalogue categories for nav / homepage when slugs differ per dataset.

Books URLs and the storefront catalogue are aligned to the same resolved “books”
tree. Fashion helpers remain for legacy links and dashboard-only categories.
"""

from oscar.core.loading import get_model

Category = get_model("catalogue", "category")


def category_by_slug_candidates(slugs, names):
    for s in slugs:
        cat = Category.objects.filter(slug=s, is_public=True).order_by("depth").first()
        if cat:
            return cat
    for name in names:
        cat = (
            Category.objects.filter(name__iexact=name, is_public=True)
            .order_by("depth")
            .first()
        )
        if cat:
            return cat
    return None


def resolve_nav_books_category():
    return category_by_slug_candidates(
        ("books", "book"),
        ("Books", "Book"),
    )


def resolve_nav_fashion_category():
    books = resolve_nav_books_category()
    fashion = category_by_slug_candidates(
        ("fashion", "clothing", "apparel", "wardrobe", "style"),
        ("Fashion", "Clothing", "Apparel", "Wardrobe", "Ready-to-wear"),
    )
    if fashion and books and fashion.pk == books.pk:
        fashion = None
    if fashion is None:
        roots = Category.objects.filter(depth=1, is_public=True).order_by("path")
        if books:
            roots = roots.exclude(pk=books.pk)
        fashion = roots.first()
    return fashion


def find_child_under_parent(parent, slug_candidates, name_candidates):
    """First matching public child of ``parent`` by slug then display name."""
    if not parent:
        return None
    children = parent.get_children().filter(is_public=True)
    for s in slug_candidates:
        c = children.filter(slug=s).first()
        if c:
            return c
    for name in name_candidates:
        c = children.filter(name__iexact=name).first()
        if c:
            return c
    return None


_NAV_CHILD_SPECS = {
    "clothes": (
        ("clothes", "clothing", "ready-to-wear", "rtw"),
        ("Clothes", "Clothing", "Ready-to-wear"),
    ),
    "shoes": (
        ("shoes", "shoe", "footwear", "fine-footwear"),
        ("Shoes", "Shoe", "Footwear"),
    ),
}


def resolve_nav_child_under_fashion(nav_child_slug: str):
    """
    Resolve Clothes / Shoes (or similar) under the same fashion root as the homepage.
    ``nav_child_slug`` should be 'clothes' or 'shoes' (lowercase).
    """
    parent = resolve_nav_fashion_category()
    key = (nav_child_slug or "").strip().lower()
    spec = _NAV_CHILD_SPECS.get(key)
    if parent and spec:
        return find_child_under_parent(parent, spec[0], spec[1])
    if parent and key:
        return find_child_under_parent(parent, (key,), ())
    return None


def is_fashion_parent_hint(parent_slug: str) -> bool:
    if not parent_slug:
        return False
    return str(parent_slug).strip().lower() in (
        "fashion",
        "clothing",
        "apparel",
        "wardrobe",
        "style",
    )


def is_fashion_nav_slug(slug: str) -> bool:
    return str(slug or "").strip().lower() in (
        "fashion",
        "clothing",
        "apparel",
        "wardrobe",
        "style",
    )


def is_books_nav_slug(slug: str) -> bool:
    return str(slug or "").strip().lower() in ("books", "book")


# Canonical fiction / genre departments under the Books root (slug, display name).
BOOK_DEPARTMENT_SPECS = (
    ("literary-fiction", "Literary Fiction"),
    ("contemporary-romance", "Contemporary Romance"),
    ("thriller-suspense", "Thriller & Suspense"),
    ("fantasy", "Fantasy"),
    ("science-fiction", "Science Fiction"),
    ("historical-fiction", "Historical Fiction"),
    ("mystery-crime", "Mystery & Crime"),
    ("young-adult-ya", "Young Adult (YA)"),
    ("horror", "Horror"),
    ("magical-realism", "Magical Realism"),
)

BOOK_DEPARTMENT_SLUG_TO_DISPLAY = dict(BOOK_DEPARTMENT_SPECS)


def book_department_display_name(category):
    """
    Canonical shelf label for dashboard / storefront when ``category`` is one of
    the ten genre departments (matched by slug). Other categories use ``.name``.
    """
    if category is None:
        return ""
    slug = (getattr(category, "slug", None) or "").strip()
    if slug in BOOK_DEPARTMENT_SLUG_TO_DISPLAY:
        return BOOK_DEPARTMENT_SLUG_TO_DISPLAY[slug]
    return category.name


def resolve_book_department_categories():
    """
    Ordered list of public department categories that are direct children of the
    resolved Books root, matching :data:`BOOK_DEPARTMENT_SPECS` when present.
    """
    books = resolve_nav_books_category()
    if not books:
        return []
    by_slug = {
        c.slug: c for c in books.get_children().filter(is_public=True).order_by("path")
    }
    out = []
    for slug, name in BOOK_DEPARTMENT_SPECS:
        cat = by_slug.get(slug)
        if cat is None:
            cat = (
                books.get_children()
                .filter(is_public=True, name__iexact=name)
                .order_by("path")
                .first()
            )
        if cat:
            out.append(cat)
    return out


def resolve_storefront_browse_categories():
    """
    Category queryset for the main catalogue index (``/catalogue/``): the Books nav
    tree only (bookstore). Returns ``None`` when books do not resolve so browse
    stays unrestricted (e.g. tests or empty DB).
    """
    books = resolve_nav_books_category()
    if not books:
        return None
    return books.get_descendants_and_self()


def category_is_in_storefront_books_tree(category) -> bool:
    """True if ``category`` is the resolved books root or one of its descendants."""
    if category is None:
        return False
    books = resolve_nav_books_category()
    if not books:
        return True
    books_pks = set(books.get_descendants_and_self().values_list("pk", flat=True))
    return category.pk in books_pks
