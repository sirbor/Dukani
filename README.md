# Dukani

**Curated volumes & fine footwear** - A premium Django e-commerce
experience built on [Oscar](https://github.com/django-oscar/django-oscar).
Dukani features a luxury retail storefront, sophisticated catalogue
management, an intuitive basket system, and a multi-step checkout
pipeline.

---

## Experience the Storefront

### Homepage & Brand Experience

A premium landing page designed for high-end retail, featuring seamless
navigation and editorial merchandising.

- ![Dukani homepage](docs/screenshots/homepage.png)
- ![Client profile](docs/screenshots/clientprofile.png)

### Catalogue & Archive

Browse curated categories with editorial grids. The "archive" style
listing is optimized for books, fashion, and artisanal footwear.

- ![Catalogue grid](docs/screenshots/catalogue.png)
- ![Archive listing](docs/screenshots/archive.png)

### Product Detail

Rich, immersive product pages featuring high-resolution imagery,
detailed attributes (editions, sizes), and intelligent related-items
suggestions.

- ![Product page](docs/screenshots/bookitem.png)
- ![Product details](docs/screenshots/bookdetails.png)
- ![Related products](docs/screenshots/bookotheritems.png)

### Seamless Shopping

A modern, card-based shopping bag and a frictionless multi-step checkout
process.

- ![Shopping bag](docs/screenshots/cart.png)
- ![Shopping bag details](docs/screenshots/cart2.png)
- ![Shipping address step](docs/screenshots/shippingaddress.png)
- ![Shipping address follow-up](docs/screenshots/shippingaddress2.png)

### Order Confirmation & Accounts

Full transparency with order previews, instant confirmation, and a
dedicated customer account area for order history.

- ![Order preview](docs/screenshots/previeworder.png)
- ![Order preview details](docs/screenshots/previeworder2.png)
- ![Order confirmation](docs/screenshots/confirmorder.png)

---

## Technical Core

- **Domain-driven commerce:** Built on Oscar's robust architecture for
  catalogue, basket, and checkout.
- **Luxury UI:** Bespoke templates styled with Bootstrap 4 and SCSS for
  a high-end feel.
- **Advanced search:** Integrated with Django Haystack for fast,
  relevant product discovery.
- **Scalable backend:** Powered by Django 4.2+ and Python 3.8+.

| Layer | Technology |
| --- | --- |
| **Backend** | Django, Python |
| **Store engine** | django-oscar (customized) |
| **Frontend** | Bootstrap 4, SCSS, jQuery |
| **Search** | Haystack (Whoosh/Solr/Elasticsearch) |

## Relationship to django-oscar

Dukani is a **fork** of
[django-oscar](https://github.com/django-oscar/django-oscar). The
vendored package lives in `src/oscar/` (same module name as upstream
for drop-in compatibility). The version in
[`src/oscar/__init__.py`](src/oscar/__init__.py) records the upstream
baseline this tree started from.

**Upgrade policy:** Treat django-oscar as the upstream of record. For
security and framework support, periodically merge or rebase upstream
releases into this fork, run the full test suite (`make test` / CI),
and resolve conflicts in customized templates and apps. Document
Dukani-only patches (in commit messages or small in-repo notes) so
future upgrades stay traceable.

**Linting:** CI and `make lint` run **Black** and **Pylint** on
`src/oscar/` and `tests/`. Optional
[pre-commit](https://pre-commit.com/) runs the same **Black** settings
(including skipping `migrations/`) plus lightweight YAML and large-file
checks. Install it with `pre-commit install` after
`pip install pre-commit`. Run `make lint` before pushing if you skip
pre-commit.

## Quick Start (Sandbox)

To get the development environment running:

```bash
# Setup environment
python -m venv venv
source venv/bin/activate

# Install and build sandbox
make sandbox
```

## Project Structure

- `src/oscar/`: The core commerce engine and customized templates.
- `sandbox/`: Local development settings and assets.
- `docs/screenshots/`: Visual assets for the storefront.

---

## License

Dukani is released under the **BSD License**. See [`LICENSE`](LICENSE)
for details.
