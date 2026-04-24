<div align="center">

# Dukani

**Curated volumes & fine footwear**

A premium Django e-commerce experience built on Oscar. Dukani features a luxury retail storefront, sophisticated catalogue management, an intuitive basket system, and a multi-step checkout pipeline.

</div>

<br>

## Experience the Storefront

**Brand Experience**
The luxury retail landing page features seamless navigation and editorial merchandising.
![Homepage](docs/screenshots/homepage.png)

**Curated Catalogue**
Browse optimized grids designed for books, fashion, and artisanal footwear.
![Catalogue](docs/screenshots/book-catalogue.png)

**Shopping Bag**
A modern card based bag for managing selections before checkout.
![Shopping Bag](docs/screenshots/cart.png)

**Shipping and Logistics**
Frictionless multi step checkout pipeline starting with secure address entry.
![Shipping Address](docs/screenshots/shipping-address.png)

**Secure Payment**
Integrated payment processing with a clear cost breakdown.
![Payment](docs/screenshots/payment.png)

**Order Confirmation**
Instant verification and transparency upon successful transaction.
![Order Confirmation](docs/screenshots/confirmed-order.png)

**Client Account**
Dedicated customer area for managing profiles and tracking order status.
![Order History](docs/screenshots/order-history.png)

<br>

## Dashboard and Management

Dukani includes a sophisticated administrative interface for managing the entire commerce operation.

**Operational Overview**
Real time summary of sales, recent orders, and store health.
![Dashboard](docs/screenshots/dashboard-main.png)

**Product Inventory**
Intuitive management of the luxury product catalogue and stock levels.
![Products](docs/screenshots/dashboard-products-list.png)

**Order Fulfillment**
Streamlined pipeline for processing transactions and tracking shipments.
![Orders](docs/screenshots/dashboard-orders-list.png)

**Reporting and Analytics**
Data driven insights into store performance and customer trends.
![Reports](docs/screenshots/dashboard-reports.png)

<br>

## Technical Core

**Architecture**
Built on Oscar's domain driven architecture for catalogue, basket, and checkout.

**User Interface**
Bespoke templates styled with Bootstrap 4 and SCSS for a high end feel.

**Discovery**
Integrated with Django Haystack for fast and relevant product discovery.

**Backend Stack**
Powered by Django 5.2 and Python 3.12.

**Search Engine**
Utilizes Haystack with Whoosh for local development indexing.

<br>

## Relationship to django-oscar

Dukani is a fork of django-oscar. The vendored package lives in src/oscar/ and maintains the same module name for drop in compatibility.

**Upgrade Policy**
Treat django-oscar as the upstream of record. Periodically merge or rebase upstream releases into this fork and run the full test suite to resolve conflicts.

**Linting Standards**
Continuous integration runs Black and Pylint on the core source and tests. Pre-commit hooks are available to ensure formatting consistency before pushing.

<br>

## Quick Start

**Setup environment**
python -m venv venv
source venv/bin/activate

**Install and build sandbox**
make sandbox

<br>

## Project Structure

**Commerce Engine**
src/oscar/ contains the core commerce engine and customized templates.

**Development Sandbox**
sandbox/ contains local development settings and assets.

**Visual Assets**
docs/screenshots/ contains the imagery for the storefront and dashboard.

<br>

## License

Dukani is released under the BSD License. See LICENSE for details.
