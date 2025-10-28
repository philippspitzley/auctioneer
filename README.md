# 🏛️ Auctioneer API

> *A personal learning project to build a REST API from scratch using FastAPI*

## 📖 About

This FastAPI application provides a **RESTful API** for an auction platform where users can register, create auctions, list products, place bids, and receive notifications about their auction activities.

### 💡 The Motivation

Throughout my learning journey, I've accumulated knowledge about REST APIs, databases, authentication, and various Python frameworks. This is where I **put it all together** - making architectural decisions, solving integration challenges, and discovering what I *really* understand versus what I only *thought* I understood.

### 🎯 The Challenge

Building an auction platform from scratch seemed like the perfect challenge: it requires **user management**, complex business logic with **time-sensitive operations**, database relationships, **background tasks** for auction state management, and **email notifications**.

---

## ✨ Features

- 👤 **User Management:** User registration, authentication, and authorization.
- 🔨 **Auction Management:** Creation, retrieval, updating, and deletion of auctions, including bid management.
- 📦 **Product Management:** Creation, retrieval, updating, and deletion of products, with associations to auctions and categories.
- ⚙️ **Background Tasks:** Periodic tasks using APScheduler to manage auction state transitions (e.g., marking auctions as finished).
- 📧 **Email Notifications:** Yagmail integration for sending email notifications (e.g., user registration, auction results).

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance web framework for building APIs |
| **SQLModel/SQLAlchemy** | Object-relational mapping (ORM) for database interaction |
| **PostgreSQL** | Relational database for data persistence |
| **Alembic** | Database migration tool for schema evolution |
| **APScheduler** | Task scheduling library for managing periodic tasks |
| **Yagmail** | Library for sending emails |

---

## 🚀 Installation and Setup

### 1️⃣ Clone the repository

```shell
git clone https://github.com/philippspitzley/auctioneer.git
```

### 2️⃣ Move to project folder

```shell
cd auctioneer
```

### 3️⃣ Install dependencies

Using pip:
```shell
pip install -r pyproject.toml
```


using uv (if installed)
```shell
uv pip install
```

### 4️⃣ Create .env file

```shell
touch .env
```

Example .env configuration:

```bash
# Database Configuration
DB_USER = "jon_doe"
DB_PW = ""
DB_HOST ="localhost"
DB_PORT = "5432"
DB_NAME = "auctioneer"

# Security
# Generate with: openssl rand -hex 32
SECRET_KEY = "8d5c0a33e1fddcb980b9488886193b3a5e80096fb6424cff42106c8627e598f3"

# Email Configuration
EMAIL_USER = "yourmail@mail.com"
EMAIL_PASSWORD = "very_safe_pasword"
```

### 5️⃣ Apply database migrations

```shell
alembic upgrade head
```

### 6️⃣ Start the application

```shell
fastapi dev app/main.py
```

## 📚 API Documentation

The API documentation is automatically generated and available through **Swagger UI** at:
`https://yourhost/docs`

💡 **Tip:** Access this URL after starting the application to explore all available endpoints interactively.
