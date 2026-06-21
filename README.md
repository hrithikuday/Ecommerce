# Xeon - Premium E-Commerce Platform

Xeon is a state-of-the-art, high-performance E-Commerce platform built with **Django** and **Django REST Framework (DRF)**. It features a premium, responsive glassmorphic HTML user interface as well as a robust, fully-documented REST API backend.

## Tech Stack

- **Core Framework**: Django 4.2+
- **REST APIs**: Django REST Framework (DRF)
- **Database**: 
  - PostgreSQL (Production / Render)
  - SQLite (Local Development)
- **Styling & Assets**: Vanilla CSS (Premium Dark Mode & Glassmorphic components)
- **Static Assets Serving**: WhiteNoise (Compressed & Manifest-cached serving)
- **Production Server**: Gunicorn

---

## Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Git** installed on your local machine.

### 2. Installation & Setup
Clone the repository and install dependencies inside a Python virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Database Migrations
Run the initial migrations to set up the database schema:

```bash
python manage.py migrate
```

### 4. Seed Database Data
A script has been provided to seed the database with sample products, categories, admin users, and media links. Run it using:

```bash
python seed_data.py
```

### 5. Running the Application
Start the Django development server:

```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## API Documentation

All API endpoints are under the `/api/` prefix.

### Authentication
#### 1. Token Login
Generates a REST token for programmatic API authentication.
* **Endpoint**: `/api/auth/login/`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "token": "4a5c8e3...",
    "user": {
      "id": 1,
      "username": "your_username",
      "email": "user@example.com",
      "role": "BUYER",
      "phone": null,
      "address": null
    }
  }
  ```

---

### Categories API
Manages product categories.
* **Endpoint**: `/api/categories/`
* **Authentication**: `None` (Public Read), admin/seller (Write)
* **Methods**:
  - `GET /api/categories/` - List all categories.
  - `GET /api/categories/<slug>/` - Retrieve a category by slug.
  - `POST /api/categories/` - Create a new category.
  - `PUT /api/categories/<slug>/` - Update a category.
  - `DELETE /api/categories/<slug>/` - Delete a category.
* **Category Fields**:
  - `id` (int, read-only)
  - `name` (string, required)
  - `slug` (string, read-only auto-generated)
  - `description` (string, optional)
  - `image_url` (string, optional)
  - `product_count` (int, read-only)

---

### Products API
Manages items in the product catalog.
* **Endpoint**: `/api/products/`
* **Authentication**: `None` (Public Read), admin/seller (Write)
* **Methods**:
  - `GET /api/products/` - List all active products.
    - *Query Parameters*: `category=<slug>` (filter by category), `search=<text>` (search in name or description).
  - `GET /api/products/<slug>/` - Retrieve product details.
  - `POST /api/products/` - Add a new product.
  - `PUT /api/products/<slug>/` - Edit a product.
  - `DELETE /api/products/<slug>/` - Delete a product.
* **Product Fields**:
  - `id` (int, read-only)
  - `category` (int, category ID reference)
  - `category_name` (string, read-only)
  - `name` (string, required)
  - `slug` (string, read-only auto-generated)
  - `description` (string, optional)
  - `price` (decimal, required)
  - `currency` (string, defaults to "USD")
  - `stock` (int, defaults to 0)
  - `image_url` (string, optional)
  - `is_active` (boolean, defaults to True)

---

### Shopping Cart API
Manages the user's shopping cart.
* **Endpoint**: `/api/cart/`
* **Authentication**: Required (`Token` or `Session` Auth)
* **Methods**:
  - `GET /api/cart/` - View current cart status (items, quantities, and total price).
  - `POST /api/cart/add/` - Add an item to the cart.
    * *Payload*:
      ```json
      {
        "product_id": 1,
        "quantity": 2
      }
      ```
  - `POST /api/cart/update/` - Update item quantity.
    * *Payload*:
      ```json
      {
        "item_id": 4,
        "quantity": 3
      }
      ```
  - `POST /api/cart/clear/` - Clear all items from the cart.
* **Response Payload (Cart Schema)**:
  ```json
  {
    "id": 1,
    "user": 2,
    "items": [
      {
        "id": 4,
        "product": { ...product_data... },
        "quantity": 3,
        "total_price": "89.97"
      }
    ],
    "total_price": "89.97",
    "item_count": 3
  }
  ```

---

### Orders API
Allows buyers to place and view orders.
* **Endpoint**: `/api/orders/`
* **Authentication**: Required (`Token` or `Session` Auth)
* **Methods**:
  - `GET /api/orders/` - Retrieve order history for the authenticated user.
  - `GET /api/orders/<id>/` - Retrieve details of a specific order.
  - `POST /api/orders/` - Create a new order from current cart items.
    * *Payload*:
      ```json
      {
        "shipping_address": "123 Main St, New York, NY",
        "billing_address": "123 Main St, New York, NY"
      }
      ```
* **Order Fields**:
  - `id` (int, read-only)
  - `total_amount` (decimal, read-only generated from cart)
  - `status` (string, e.g., "PAID", "PENDING")
  - `shipping_address` (string, required)
  - `billing_address` (string, optional)
  - `items` (array, read-only lists of products ordered)
  - `payment` (object, payment reference & transaction details)

---

### Media URLs API
Manages dynamic custom external media and marketing links.
* **Endpoint**: `/api/media-urls/`
* **Authentication**: Required (`Token` or `Session` Auth)
* **Methods**:
  - `GET /api/media-urls/` - List links. (Sellers view all links; Buyers view only their created links).
  - `POST /api/media-urls/` - Create a new link.
    * *Payload*:
      ```json
      {
        "title": "Xeon Ad Campaign",
        "url": "https://youtube.com/example",
        "url_type": "VIDEO"
      }
      ```
  - `PUT /api/media-urls/<id>/` - Update a link.
  - `DELETE /api/media-urls/<id>/` - Delete a link.

---

## Hosting on Render

The repository is pre-configured with **Render Blueprint** files:
- **`render.yaml`**: Multi-service configuration creating a free PostgreSQL DB and a Python Web Service.
- **`build.sh`**: Automatic build script which installs python dependencies, runs `collectstatic`, and runs database migrations on startup.
- **`.gitattributes`**: Configured to force LF line-endings on `build.sh` when pushing to Git, preventing bash scripting errors on Render's Linux server.

To host:
1. Connect your GitHub repository to Render.
2. Select **New Blueprint** and link the repository.
3. Render will deploy the infrastructure and output the live link automatically.
