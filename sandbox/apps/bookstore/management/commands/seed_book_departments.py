"""
Create the Books root (if missing) and fiction / genre departments under it.

Slug and order match ``BOOK_DEPARTMENT_SPECS`` in ``category_resolution`` so the
homepage “Browse by department” grid can list them.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from oscar.apps.catalogue.category_resolution import (
    BOOK_DEPARTMENT_SPECS,
    resolve_nav_books_category,
)
from oscar.core.loading import get_model


class Command(BaseCommand):
    help = "Ensure Books category and standard genre departments exist (treebeard)."

    def handle(self, *args, **options):
        Category = get_model("catalogue", "category")

        with transaction.atomic():
            books = resolve_nav_books_category()
            if books is None:
                books = Category.add_root(
                    name="Books",
                    slug="books",
                    is_public=True,
                )
                self.stdout.write(self.style.SUCCESS("Created Books root category."))
            else:
                self.stdout.write(f"Using existing Books category (pk={books.pk}).")

            created = 0
            updated = 0
            ok = 0
            for slug, name in BOOK_DEPARTMENT_SPECS:
                child = books.get_children().filter(slug=slug).first()
                if child:
                    fields = []
                    if child.name != name:
                        child.name = name
                        fields.append("name")
                    if not child.is_public:
                        child.is_public = True
                        fields.append("is_public")
                    if fields:
                        child.save(update_fields=fields)
                        updated += 1
                        self.stdout.write(f"  ~ {name} ({slug}) — synced label")
                    else:
                        ok += 1
                    continue
                books.add_child(name=name, slug=slug, is_public=True)
                created += 1
                self.stdout.write(f"  + {name} ({slug})")

        Category.fix_tree()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created}, updated {updated}, unchanged {ok} department(s)."
            )
        )
