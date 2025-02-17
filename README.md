# Auctioneer API

... an Auction Platform Interface

This FastAPI application provides a RESTful API for an auction platform, enabling users to buy and sell items.

## Features

- **User Management:** User registration, authentication, and authorization.
- **Auction Management:** Creation, retrieval, updating, and deletion of auctions, including bid management.
- **Product Management:** Creation, retrieval, updating, and deletion of products, with associations to auctions and categories.
- **Background Tasks:** Periodic tasks using APScheduler to manage auction state transitions (e.g., marking auctions as finished).
- **Email Notifications:** Yagmail integration for sending email notifications (e.g., user registration, auction results).

## Technology Stack

- **FastAPI:** High-performance web framework for building APIs.
- **SQLModel/SQLAlchemy:** Object-relational mapping (ORM) for database interaction.
- **PostgreSQL:** Relational database for data persistence.
- **Alembic:** Database migration tool for schema evolution.
- **APScheduler:** Task scheduling library for managing periodic tasks.
- **Yagmail:** Library for sending emails.

## Installation and Setup

1. **Clone the repository:**

```shell
git clone https://github.com/philippspitzley/auctioneer.git
```

2. **Move to project folder:**

```shell
cd auctioneer
```

3. **Install dependencies:**

```shell
pip install -r pyproject.toml
```

with uv is installed

```shell
uv pip install
```

4. **Create .env file:**

```shell
touch .env
```

Example .env:

```bash
DB_USER = "jon_doe"
DB_PW = ""
DB_HOST ="localhost"
DB_PORT = "5432"
DB_NAME = "auctioneer"

# openssl run 'rand -hex 32' to generate secretkey
SECRET_KEY = "8d5c0a33e1fddcb980b9488886193b3a5e80096fb6424cff42106c8627e598f3"

# email account credentials to send emails
EMAIL_USER = "yourmail@mail.com"
EMAIL_PASSWORD = "very_safe_pasword"
```

5. **Apply database migrations:**

```shell
alembic upgrade head
```

6. **Start the application:**

```shell
fastapi dev app/main.py
```

## API Documentation

The API documentation is available through Swagger UI at `https://yourhost/docs` after starting the application.
