# 🛒 E-commerce API

A production-ready RESTful API for an e-commerce platform, built with **FastAPI**, **PostgreSQL**, and **Docker**. Supports role-based access control, product catalog management, cart/checkout, and real payment processing via **Stripe**.

🔗 **Live Demo:** [https://your-render-url.onrender.com/docs](https://your-render-url.onrender.com/docs)

---

## 🚀 Features

- **JWT Authentication** with **Role-Based Access Control** (admin/user)
- **Category & Product Management** — admin-only create/edit, soft delete to preserve order history
- **Product Images on Cloudinary** — automatic resizing, old image cleanup on replace
- **Search & Filter** — by category, keyword, and price range, with pagination
- **Shopping Cart** — add/update/remove items, automatic stock validation
- **Transaction-Safe Checkout** — cart converts to an order atomically; any failure rolls back cleanly, no partial stock deductions
- **Stripe Payment Integration** — Payment Intents created per order, server-side verification before marking an order paid
- **Order History** — price is snapshotted at purchase time, independent of later price changes
- **Dockerized** — fully containerized, deployed with a managed PostgreSQL instance

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt |
| Image Storage | Cloudinary |
| Payments | Stripe (Payment Intents API) |
| Containerization | Docker |
| Deployment | Render (Web Service + managed PostgreSQL) |

---

## 📂 Project Structure

```
app/
├── main.py              # App entry point
├── database.py          # PostgreSQL connection setup
├── models.py            # SQLAlchemy models (User, Category, Product, Cart, Order...)
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # Password hashing + JWT logic
├── dependencies.py      # get_current_user / get_current_admin
├── cloudinary_config.py # Cloudinary SDK setup
├── stripe_config.py     # Stripe SDK setup
└── routers/
    ├── users.py          # Register/Login/Me
    ├── categories.py     # Category CRUD (admin-only writes)
    ├── products.py       # Product CRUD, image upload, search/filter
    ├── cart.py            # Cart management
    └── orders.py          # Checkout, payment, order history
```

---

## 🔑 Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/users/register` | Create a new account (default role: user) |
| POST | `/users/login` | Login, receive JWT token |
| GET | `/users/me` | Get current user's profile |
| GET | `/categories/` | List categories (public) |
| POST | `/categories/` | Create category (admin only) |
| GET | `/products/?category_id=&search=&min_price=&max_price=` | Browse/filter products |
| POST | `/products/` | Create product (admin only) |
| POST | `/products/{id}/image` | Upload product thumbnail to Cloudinary (admin only) |
| GET | `/cart/` | View cart with calculated total |
| POST | `/cart/` | Add item to cart |
| POST | `/orders/` | Checkout — converts cart to an order |
| POST | `/orders/{id}/pay` | Create a Stripe Payment Intent for an order |
| POST | `/orders/{id}/confirm-payment` | Verify payment with Stripe, mark order as paid |
| GET | `/orders/` | View order history |

Full interactive documentation available at `/docs` (Swagger UI).

---

## ⚙️ Running Locally

### With Docker (recommended)

```bash
docker build -t ecommerce-api .
docker run -d -p 8000:8000 --env-file .env --name ecommerce-container ecommerce-api
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to explore the API.

---

## 🔒 Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ecommerce_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

STRIPE_SECRET_KEY=sk_test_your-key
```

---

## 🏗️ Design Notes

- **Admins are never self-assigned** — every new account defaults to the `user` role; the first admin is promoted directly in the database.
- **Checkout validates before it mutates** — stock and product-availability checks run fully before any database write, and the whole operation runs inside a try/rollback block so a mid-checkout failure can't leave stock partially deducted.
- **Order prices are immutable** — `price_at_purchase` is stored per order item at checkout time, so historical orders stay accurate even if product prices change later.
- **Payments are server-verified** — an order is only marked `paid` after the backend confirms the Payment Intent's status directly with Stripe, never from a client-supplied flag.

---

## 👤 Author

Built as part of a backend development portfolio project series focused on FastAPI, relational database design, third-party service integration, and containerized deployment.