# TechHouse Backend API

A production-grade e-commerce backend for technology products built with FastAPI and PostgreSQL.

## Overview

TechHouse is a modular monolith backend system designed to demonstrate professional software engineering practices including clean architecture, secure coding, and realistic e-commerce workflows.

**Tech Stack:**
- FastAPI 0.104+
- Python 3.12
- PostgreSQL (Docker)
- SQLAlchemy 2.0
- JWT Authentication
- Pydantic v2

## Features

- **User Management**: Registration, authentication, profile management, membership tiers
- **Product Catalog**: CRUD operations for products with categories and inventory
- **Multi-Vendor Shops**: Shop creation and management
- **Shopping Cart**: Item management with real-time stock validation
- **Payments**: Prototype payment system (no real card processing)
- **Support Tickets**: Customer support ticket management system
- **Role-Ready Architecture**: Foundation for role-based access control

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12 (for local development)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Abdumalik-ProDev/TechHouse-Backend
cd TechHouse-Backend
```

2. Start the services:
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

### Initial Setup

On first run, the database will be created automatically. Access the Swagger documentation at:
```
http://localhost:8000/redock
```

## Project Structure

```
app/
├── api/              # FastAPI route handlers (no business logic)
├── core/             # Configuration, database, security utilities
├── models/           # SQLAlchemy ORM models
├── repositories/     # Database access layer
├── schemas/          # Pydantic request/response schemas
├── services/         # Business logic layer
├── utils/            # Enumerations and utilities
└── main.py           # Application entry point
```

## Architecture Principles

- **Separation of Concerns**: API layer contains only route handling, services contain business logic
- **Dependency Injection**: Services receive dependencies through constructors
- **Repository Pattern**: All database access goes through dedicated repositories
- **Type Safety**: Full type hints throughout codebase
- **Clean Code**: SOLID principles, DRY, minimal magic numbers

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login

### Users
- `GET /api/v1/users/{user_id}` - Get user profile
- `PUT /api/v1/users/{user_id}` - Update profile
- `DELETE /api/v1/users/{user_id}` - Delete account

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{product_id}` - Get product details
- `POST /api/v1/products` - Create product
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product

### Shops
- `GET /api/v1/shops` - List shops
- `POST /api/v1/shops` - Create shop
- `GET /api/v1/shops/{shop_id}` - Get shop details

### Cart
- `GET /api/v1/carts/me` - Get user's cart
- `POST /api/v1/carts/items` - Add item to cart
- `DELETE /api/v1/carts/items/{item_id}` - Remove item

### Payments
- `POST /api/v1/payments` - Create payment record
- `GET /api/v1/payments/{payment_id}` - Get payment details

### Support
- `POST /api/v1/support/tickets` - Create support ticket
- `GET /api/v1/support/tickets/{ticket_id}` - Get ticket details

## Development

### Running Locally

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Start PostgreSQL via Docker:
```bash
docker compose up db -d
```

4. Run the app:
```bash
uvicorn app.main:app --reload
```

## Security

- Passwords hashed with bcrypt (12 rounds)
- JWT-based authentication with configurable expiration
- Environment variables for sensitive configuration
- No hardcoded credentials
- CORS configured for development

## Database

PostgreSQL is containerized and managed via Docker Compose. Connection pooling is configured for production readiness.

## Testing

Run tests with:
```bash
pytest
```

## Deployment

For production:
1. Update `.env` with production secrets
2. Set `DEBUG=false` in configuration
3. Use strong `SECRET_KEY` value
4. Configure proper database backups
5. Set up monitoring and logging

## Contributing

Code must be:
- Type-hinted throughout
- Well-documented (clear docstrings)
- Tested before commit
- Reviewed before merge

## License

Academic assignment - TechHouse Backend © 2026
