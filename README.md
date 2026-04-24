<div align="center">

# Dukani

**Curated volumes & fine footwear**

A premium Django e-commerce experience built on Oscar. Dukani features a luxury retail storefront, sophisticated catalogue management, an intuitive basket system, and a multi-step checkout pipeline.

</div>

<br>

## Experience the Storefront

**Brand Experience**
The luxury retail landing page serves as the digital flagship store, designed to evoke the premium feel of high-end boutique shopping. It features seamless navigation through curated collections and editorial merchandising that highlights featured volumes and footwear. The layout is fully responsive, ensuring a consistent brand experience across desktop and mobile devices.
![Homepage](docs/screenshots/homepage.png)

**Curated Catalogue**
The catalogue employs an editorial grid system optimized for visual discovery. Products are organized into sophisticated categories with support for complex attributes, including editions for books and sizing for footwear. Users can filter and sort through the archive to find specific items or browse curated selections defined by store curators.
![Catalogue](docs/screenshots/book-catalogue.png)

**Shopping Bag**
A modern, card-based interface allows customers to manage their selections with ease. The system supports real-time updates for quantities and automatically applies active offers or vouchers. Customers can review their total costs, including estimated taxes and shipping, before proceeding to the checkout pipeline.
![Shopping Bag](docs/screenshots/cart.png)

**Shipping and Logistics**
The checkout process is divided into logical, frictionless steps to maximize conversion. It begins with secure address entry and validation, supporting multiple saved addresses for returning clients. The system dynamically calculates shipping options based on the delivery destination and the physical properties of the items in the bag.
![Shipping Address](docs/screenshots/shipping-address.png)

**Secure Payment**
Integrated payment processing ensures a safe and transparent transaction experience. Customers are presented with a clear breakdown of their order costs, including subtotal, shipping, and tax. The platform is designed to integrate with various payment gateways while maintaining high security standards for client data.
![Payment](docs/screenshots/payment.png)

**Order Confirmation**
Upon successful transaction, customers receive instant verification on-screen and via email. The confirmation page provides a comprehensive summary of the purchase, including an order number for tracking and a final receipt. This transparency builds trust and ensures the customer is informed at every stage of the post-purchase process.
![Order Confirmation](docs/screenshots/confirmed-order.png)

**Client Account**
The dedicated customer area provides a central hub for managing the shopping relationship. Clients can track current order status, view their complete purchase history, and manage their address book and personal profiles. This section is designed to facilitate easy re-ordering and provide a personalized experience for returning shoppers.
![Order History](docs/screenshots/order-history.png)

<br>

## Dashboard and Management

Dukani includes a sophisticated administrative interface for managing the entire commerce operation.

**Operational Overview**
The administrative dashboard provides a high-level command center for store managers. It features real-time analytics on sales performance, recent order volume, and overall store health. This central hub allows for quick identification of trends and immediate response to operational needs.
![Dashboard](docs/screenshots/dashboard-main.png)

**Product Inventory**
Management of the product catalogue is handled through an intuitive interface that supports complex product structures. Administrators can define product classes, attributes, and variants, as well as manage multiple stock records and pricing strategies. The system is built to handle the unique requirements of both literary editions and artisanal footwear.
![Products](docs/screenshots/dashboard-products-list.png)

**Order Fulfillment**
The order management pipeline is designed for efficiency and accuracy. Staff can track orders through various stages of fulfillment, from payment authorization to packing and shipping. The interface provides all necessary details for processing transactions and maintaining clear communication with the customer throughout the delivery lifecycle.
![Orders](docs/screenshots/dashboard-orders-list.png)

**Reporting and Analytics**
Data-driven insights are available through comprehensive reporting tools. Managers can analyze customer trends, product performance, and financial data to inform business decisions. The system provides the visibility needed to optimize the catalogue and marketing strategies for long-term growth.
![Reports](docs/screenshots/dashboard-reports.png)

<br>

## Technical Core

**Architecture**
Built on Oscar's domain-driven architecture for catalogue, basket, and checkout. This modular design allows for deep customization of core commerce logic while maintaining a stable foundation.

**User Interface**
Bespoke templates styled with Bootstrap 4 and SCSS provide a high-end visual feel. The front-end architecture is designed for performance and accessibility across all modern browser environments.

**Discovery**
Integrated with Django Haystack for fast and relevant product discovery. The search system supports advanced filtering and indexing, ensuring that customers can find exactly what they are looking for with minimal effort.

**Backend Stack**
The platform is powered by Django 5.2 and Python 3.12, utilizing the latest features of the framework for security and performance. This modern stack provides a scalable and maintainable codebase for future growth.

**Search Engine**
The implementation utilizes Haystack with Whoosh for local development indexing, providing a powerful search experience without the need for complex external dependencies during the setup phase.

<br>

## Relationship to django-oscar

Dukani is a fork of django-oscar. The vendored package lives in src/oscar/ and maintains the same module name for drop-in compatibility.

**Upgrade Policy**
Treat django-oscar as the upstream of record. Periodically merge or rebase upstream releases into this fork and run the full test suite to resolve conflicts. This ensures that the platform benefits from the latest security updates and core feature improvements.

**Linting Standards**
Continuous integration runs Black and Pylint on the core source and tests to maintain high code quality. Pre-commit hooks are available to ensure formatting consistency and catch common issues before code is pushed to the repository.

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
The src/oscar/ directory contains the core commerce engine and customized templates that define the unique Dukani experience.

**Development Sandbox**
The sandbox/ directory contains local development settings, assets, and fixtures used to populate the store for testing and demonstration.

**Visual Assets**
The docs/screenshots/ directory contains the high-resolution imagery used to document the storefront and administrative dashboard features.

<br>

## License

Dukani is released under the BSD license by Tangent Communications PLC. See LICENSE for details.
