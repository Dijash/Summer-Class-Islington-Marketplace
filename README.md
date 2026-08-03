# 🛒 Islington MarketPlace — Modern E-Commerce Platform

A feature-rich, high-performance E-Commerce & Multi-Vendor Marketplace built with **Django 6.0**, **Python 3.12**, and modern web standards. Features interactive shopping carts, product color/size variants, customer & seller dashboards, real-time shipping/tax calculations, and full integration with the **Khalti Payment Gateway (v2 ePayment API)**.

---

## 🌟 Key Features

### 🛍️ Shopping & Product Experience
- **Interactive Product Catalog**: Grid and list views with category filtering, search, and dynamic sorting.
- **Multi-Angle Gallery & Variants**: Dynamic color swatches with instant image swapping, size selectors, and stock status.
- **Ratings & Reviews System**: Average star ratings, interactive review submit/edit form, and visual rating breakdown progress bars.
- **Wishlist**: AJAX-powered wishlist toggling with instant feedback toasts.

### 💳 Cart, Checkout & Payment Integration
- **Live Cart & Mini-Cart**: Real-time item additions, quantity modifications, and subtotal recalculation via AJAX.
- **Dynamic Checkout**: Province/District dropdown mapping (Nepal administrative divisions), address validation, and real-time shipping cost recalculation (Standard FREE vs. Express Overnight).
- **Khalti Payment Gateway (v2 API)**:
  - ePayment initiation with server-side payload generation (`pidx`).
  - Automatic lookup verification endpoint (`/khalti/verify/`).
  - Integrated local Sandbox Gateway (`/khalti/gateway/`) for offline development & testing.
- **Cash on Delivery (COD)** fallback support.

### 👤 Customer & 🏢 Seller Portals
- **Customer Dashboard**: Track active orders, view transaction history, inspect payment status (`Paid via Khalti` vs. `COD`), and track order status (`Pending`, `In Transit`, `Delivered`).
- **Seller Management**: Dedicated vendor dashboard for managing inventory, viewing store orders, and updating product availability.
- **Auth & Security**: Customized login and registration pages featuring dynamic password strength indicators, password match checks, and role separation.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | Django 6.0.7 |
| **Language** | Python 3.12 |
| **Database** | SQLite (Development) / PostgreSQL (`psycopg2-binary`) |
| **Frontend** | HTML5, CSS3 (Vanilla Design System, Glassmorphism, CSS Variables), JavaScript (ES6+ Fetch API) |
| **Iconography & Fonts** | FontAwesome 6, Google Fonts (*Plus Jakarta Sans*, *Inter*, *Playfair Display*) |
| **Payments** | Khalti ePayment Gateway API v2 |
| **Environment & Server** | `pipenv`, `python-decouple`, `gunicorn`, `whitenoise` |

---

## 📁 Project Architecture

```text
Market-Place-Final/
├── Marketplace/          # Project configuration & root URL routing
│   ├── settings.py       # App settings & Khalti API keys
│   └── urls.py           # Global URL configuration
├── core/                 # Core homepage, navigation header, hero banners & footers
├── accounts/             # Authentication, user profiles, login & signup views
├── product/              # Product catalog, variant management, reviews & gallery
├── cart/                 # Cart logic, checkout, dynamic calculation & Khalti views
│   └── templates/cart/   # Checkout UI & Khalti Gateway sandbox template
├── customer/             # Customer dashboard, order history & wishlist management
├── seller/               # Seller dashboard & product inventory management
├── static/               # Modular CSS design system & static assets
├── media/                # User uploaded product images & avatars
├── manage.py             # Django management script
├── Pipfile               # Pipenv dependency specification
└── README.md             # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- **Python 3.12+**
- **Pipenv** (`pip install pipenv`)
- **Git**

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Dijash/Summer-Class-Islington-Marketplace.git
   cd Summer-Class-Islington-Marketplace
   ```

2. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory (optional for production credentials):
   ```env
   DEBUG=True
   SECRET_KEY=your-django-secret-key
   KHALTI_SECRET_KEY=80007e115d4d421c9d240952044a76fb
   ```

4. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser (Admin Access)**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000` in your web browser.

---

## 💳 Khalti Integration Flow

1. **Initiation (`/cart/place-order/`)**:
   - Validates user shipping & payment selections.
   - Calculates the order amount in **Paisa** (`NPR * 100`).
   - Sends initiation request to Khalti v2 API (`/api/v2/epayment/initiate/`).
   - Redirects customer to Khalti's payment URL (or local sandbox fallback).

2. **Verification (`/cart/khalti/verify/`)**:
   - Intercepts callback parameters (`pidx`, `status`, `transaction_id`).
   - Sends a server-to-server lookup request (`/api/v2/epayment/lookup/`) to verify authenticity.
   - Marks order as `payment_status = 'paid'` and redirects to customer order confirmation.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.

---

## 👨‍💻 Authors & Acknowledgments

- **Developer**: Dijash
- Developed as part of the Summer E-Commerce Web Application Project at Islington College.
