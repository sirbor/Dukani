"""
Assign each book in the Books tree to exactly one genre department.

Distributes titles evenly across the 10 departments (round-robin: ~20 each for
198 books). Only parent / standalone products get categories; children inherit
from the parent.
"""

import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from oscar.apps.catalogue.category_resolution import (
    resolve_book_department_categories,
    resolve_nav_books_category,
)
from oscar.core.loading import get_model


class Command(BaseCommand):
    help = (
        "Split books evenly across the 10 department categories (round-robin). "
        "Use --shuffle to randomize which title lands in which department while "
        "keeping counts balanced."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--shuffle",
            action="store_true",
            help="Shuffle books before assigning so departments get a mixed set (counts stay even).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print counts only; do not change ProductCategory rows.",
        )

    def handle(self, *args, **options):
        Product = get_model("catalogue", "product")
        ProductCategory = get_model("catalogue", "ProductCategory")

        books = resolve_nav_books_category()
        if books is None:
            raise CommandError("No Books category found. Run seed_book_departments first.")

        departments = resolve_book_department_categories()
        if len(departments) < 10:
            raise CommandError(
                "Expected 10 department categories under Books; found %s. "
                "Run seed_book_departments." % len(departments)
            )

        book_tree_ids = list(
            books.get_descendants_and_self().values_list("pk", flat=True)
        )
        book_tree_id_set = set(book_tree_ids)

        product_ids = (
            ProductCategory.objects.filter(category_id__in=book_tree_id_set)
            .values_list("product_id", flat=True)
            .distinct()
        )
        candidates = Product.objects.filter(pk__in=product_ids, is_public=True)

        class_candidates = Product.objects.filter(
            is_public=True, product_class__slug__in=("book", "books")
        )

        canonical_pks = set()
        for p in candidates.only("pk", "structure", "parent_id").iterator():
            if p.structure == Product.CHILD and p.parent_id:
                canonical_pks.add(p.parent_id)
            else:
                canonical_pks.add(p.pk)

        for p in class_candidates.only("pk", "structure", "parent_id").iterator():
            if p.structure == Product.CHILD and p.parent_id:
                canonical_pks.add(p.parent_id)
            else:
                canonical_pks.add(p.pk)

        products = list(
            Product.objects.filter(pk__in=canonical_pks, is_public=True).order_by("pk")
        )
        n = len(products)
        if options["shuffle"]:
            random.shuffle(products)

        k = len(departments)
        self.stdout.write(
            "Books tree: %d categories | Departments: %d | Books to assign: %d "
            "(~%d–%d per department)"
            % (
                len(book_tree_ids),
                k,
                n,
                n // k,
                (n + k - 1) // k,
            )
        )

        if options["dry_run"]:
            return

        with transaction.atomic():
            for idx, product in enumerate(products):
                dept = departments[idx % k]
                ProductCategory.objects.filter(
                    product=product, category_id__in=book_tree_id_set
                ).delete()
                for child in product.children.all():
                    ProductCategory.objects.filter(
                        product=child, category_id__in=book_tree_id_set
                    ).delete()

                ProductCategory.objects.get_or_create(
                    product=product, category_id=dept.pk
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Assigned %d book(s) across %d departments (even round-robin)."
                % (n, k)
            )
        )
