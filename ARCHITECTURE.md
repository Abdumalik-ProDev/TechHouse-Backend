# TechHouse Backend - Architecture & Design Documentation

## Executive Summary

TechHouse is a professional, production-grade e-commerce backend system built with FastAPI and Python 3.12. It demonstrates enterprise-level software engineering practices including clean architecture, SOLID principles, and comprehensive security implementation.

## System Architecture

### Layered Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              FastAPI HTTP Layer                      │
│  (API Routes, Request/Response Handling)            │
├─────────────────────────────────────────────────────┤
│          Service Layer (Business Logic)             │
│  (Validation, Authorization, Business Rules)       │
├─────────────────────────────────────────────────────┤
│        Repository Layer (Data Access)               │
│  (Database Queries, CRUD Operations)               │
├─────────────────────────────────────────────────────┤
│        SQLAlchemy ORM & Models                      │
│  (Database Abstraction, Relationships)             │
├─────────────────────────────────────────────────────┤
│             PostgreSQL Database                     │
└─────────────────────────────────────────────────────┘
```

### Directory Structure

```
app/
├── api/                      # FastAPI routers (HTTP layer)
│   ├── __init__.py
│   ├── auth.py              # Authentication endpoints
│   ├── users.py             # User management endpoints
│   ├── products.py          # Product CRUD endpoints
│   ├── shops.py             # Shop management endpoints
│   ├── carts.py             # Shopping cart endpoints
│   ├── payment.py           # Payment endpoints
│   ├── support.py           # Support ticket endpoints
│   └── deps.py              # Dependency injection utilities
│
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── auth.py              # Authentication service
│   ├── user.py              # User service
│   ├── product.py           # Product service
│   ├── shop.py              # Shop service
│   ├── cart.py              # Cart service
│   ├── payment.py           # Payment service
│   └── support.py           # Support service
│
├── repositories/             # Data access layer
│   ├── __init__.py
│   ├── user.py              # User repository
│   ├── product.py           # Product repository
│   ├── shop.py              # Shop repository
│   ├── cart.py              # Cart repository
│   └── payment.py           # Payment repository
│
├── models/                   # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py              # Base model with timestamps
│   ├── user.py              # User model
│   ├── product.py           # Product model
│   ├── shop.py              # Shop model
│   ├── membership.py        # Membership tier model
│   ├── cart.py              # Cart and CartItem models
│   ├── payment.py           # Payment model
│   └── support.py           # Support ticket model
│
├── schemas/                  # Pydantic models
│   ├── __init__.py
│   ├── auth.py              # Auth request/response schemas
│   ├── user.py              # User schemas
│   ├── product.py           # Product schemas
│   ├── shop.py              # Shop schemas
│   ├── cart.py              # Cart schemas
│   ├── payment.py           # Payment schemas
│   └── support.py           # Support ticket schemas
│
├── core/                     # Core infrastructure
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── db.py                # Database engine and session
│   ├── security.py          # JWT and password utilities
│   └── exceptions.py        # Custom exceptions (optional)
│
├── utils/                    # Utilities
│   ├── __init__.py
│   └── enums.py             # Enumerations (Status, Priority, etc)
│
├── __init__.py
└── main.py                  # FastAPI app factory
```

## Design Patterns Used

### 1. Repository Pattern
**Purpose**: Abstract database access logic from business logic

```python
# repositories/user.py
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
```

### 2. Service Layer Pattern
**Purpose**: Encapsulate business logic and coordinate between repositories

```python
# services/user.py
class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)
```

### 3. Dependency Injection
**Purpose**: Loose coupling and easy testing

```python
# api/users.py
@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    service = UserService(db)
    # ...
```

### 4. Factory Pattern
**Purpose**: Centralized application creation

```python
# main.py
def create_app() -> FastAPI:
    app = FastAPI(...)
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(auth.router, ...)
    return app
```

### 5. Singleton Pattern
**Purpose**: Single instance of database engine and session factory

```python
# core/db.py
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
```

## Data Flow Example: User Registration

```
1. HTTP Request (POST /auth/register)
   ↓
2. API Layer (auth.py:register)
   - Validates input schema
   - Calls auth service
   ↓
3. Service Layer (AuthService)
   - Checks username/email uniqueness
   - Hashes password with bcrypt
   - Creates user via repository
   - Creates associated cart
   ↓
4. Repository Layer (UserRepository)
   - Executes INSERT query
   - Returns created user
   ↓
5. Database (PostgreSQL)
   - Stores user record
   - Generates timestamps
   ↓
6. Response (UserResponse schema)
   - Returns user data (not password)
```

## Security Architecture

### Authentication Flow

```
1. User Login (POST /auth/login)
   │
   ├─ Validate credentials
   ├─ Verify password with bcrypt
   └─ If valid:
      │
      ├─ Create JWT token
      │  ├─ Set subject (user_id)
      │  ├─ Set expiration
      │  └─ Sign with SECRET_KEY
      │
      └─ Return token to client

2. Subsequent Requests
   │
   ├─ Client sends: Authorization: Bearer <token>
   │
   ├─ API extracts token
   ├─ Validates signature with SECRET_KEY
   ├─ Checks expiration
   ├─ Extracts user_id from payload
   │
   └─ If valid: Attach user to request context
```

### Security Features

1. **Password Hashing**
   - Algorithm: bcrypt
   - Rounds: 12 (configurable in security.py)
   - Salt: Automatic (bcrypt generates)

2. **JWT Tokens**
   - Algorithm: HS256
   - Payload: {sub: user_id, exp: timestamp}
   - Validation: Signature verification on each request

3. **Input Validation**
   - Pydantic models validate all inputs
   - Email validation built-in
   - Field constraints (min/max length, regex patterns)

4. **Database Security**
   - Parameterized queries (SQLAlchemy ORM)
   - Prevention of SQL injection
   - Connection pooling

5. **Authorization**
   - Role-ready structure
   - Resource ownership checks (user can only access own data)
   - Endpoint protection with `get_current_user` dependency

## Database Schema Relationships

```
User ─────┐
  └─ 1:1  └─ Cart ─── 1:N ─── CartItem ─ N:1 ── Product
  └─ 1:N  └─ Payment
  └─ 1:N  └─ SupportTicket
  └─ N:1  └─ Membership (via membership_type string)

Shop ───── 1:N ───── Product
```

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────┐
│ users                                               │
├─────────────────────────────────────────────────────┤
│ id (PK, UUID)                                       │
│ username (UNIQUE)                                   │
│ email (UNIQUE)                                      │
│ full_name                                           │
│ hashed_password                                     │
│ is_active                                           │
│ membership_type (ENUM)                              │
│ created_at, updated_at                              │
└─────────────────────────────────────────────────────┘
         │
         │ 1:1
         ├────────────────────┐
         │                    │
         │                    ▼
         │          ┌──────────────────┐
         │          │ carts            │
         │          ├──────────────────┤
         │          │ id               │
         │          │ user_id (FK)     │
         │          │ status           │
         │          │ created_at       │
         │          └──────────────────┘
         │                    │
         │                    │ 1:N
         │                    ▼
         │          ┌──────────────────┐
         │          │ cart_items       │
         │          ├──────────────────┤
         │          │ id               │
         │          │ cart_id (FK)     │
         │          │ product_id (FK)  │
         │          │ quantity         │
         │          └──────────────────┘
         │
         │ 1:N (Payments)
         │
         │ 1:N (Support Tickets)
         │
         └─────────────────────┐
                               ▼
                   ┌──────────────────┐
                   │ products         │
                   ├──────────────────┤
                   │ id (PK, UUID)    │
                   │ name             │
                   │ price            │
                   │ stock            │
                   │ category         │
                   │ sku (UNIQUE)     │
                   │ shop_id (FK)     │
                   └──────────────────┘
                         ▲
                         │ N:1
                         │
                   ┌──────────────────┐
                   │ shops            │
                   ├──────────────────┤
                   │ id (PK, UUID)    │
                   │ name (UNIQUE)    │
                   │ description      │
                   │ owner_id         │
                   │ is_active        │
                   └──────────────────┘
```

## API Endpoint Hierarchy

### Auth Routes
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Get JWT token

### User Routes
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users` - List users
- `PATCH /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete account

### Product Routes
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{product_id}` - Get product
- `GET /api/v1/products` - List products
- `PATCH /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product

### Shop Routes
- `POST /api/v1/shops` - Create shop
- `GET /api/v1/shops/{shop_id}` - Get shop
- `GET /api/v1/shops` - List shops
- `GET /api/v1/shops/user/my-shops` - Get user's shops
- `PATCH /api/v1/shops/{shop_id}` - Update shop
- `DELETE /api/v1/shops/{shop_id}` - Delete shop

### Cart Routes
- `GET /api/v1/carts/me` - Get cart
- `GET /api/v1/carts/me/summary` - Get cart summary
- `POST /api/v1/carts/me/items` - Add item
- `PATCH /api/v1/carts/me/items/{item_id}` - Update item
- `DELETE /api/v1/carts/me/items/{item_id}` - Remove item
- `DELETE /api/v1/carts/me/clear` - Clear cart

### Payment Routes
- `POST /api/v1/payments` - Create payment
- `GET /api/v1/payments/{payment_id}` - Get payment
- `GET /api/v1/payments` - List payments
- `POST /api/v1/payments/{payment_id}/process` - Process payment
- `POST /api/v1/payments/{payment_id}/refund` - Refund payment

### Support Routes
- `POST /api/v1/support/tickets` - Create ticket
- `GET /api/v1/support/tickets/{ticket_id}` - Get ticket
- `GET /api/v1/support/tickets` - List tickets
- `PATCH /api/v1/support/tickets/{ticket_id}` - Update ticket
- `POST /api/v1/support/tickets/{ticket_id}/close` - Close ticket

## Code Standards & Principles

### SOLID Principles

1. **Single Responsibility Principle**
   - Service handles business logic only
   - Repository handles database access only
   - API layer handles HTTP only

2. **Open/Closed Principle**
   - Easy to extend with new entities
   - Follow existing patterns for new features

3. **Liskov Substitution Principle**
   - Services are interchangeable with their interfaces
   - Repositories follow consistent interface

4. **Interface Segregation Principle**
   - Dependencies are specific to what's needed
   - Avoid fat service classes

5. **Dependency Inversion Principle**
   - Depend on abstractions (Session, repositories)
   - High-level modules don't depend on low-level modules

### DRY (Don't Repeat Yourself)
- Base model for common timestamps
- Shared repository methods
- Reusable schemas

### Clean Code Practices
- Meaningful variable names
- Single responsibility methods
- Type hints everywhere
- Comprehensive docstrings

## Configuration Management

### Environment Variables
```
DATABASE_URL        # PostgreSQL connection string
SECRET_KEY         # JWT signing key
DEBUG              # Debug mode flag
CORS_ORIGINS       # Allowed CORS origins
ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration
```

### Configuration Hierarchy
1. `.env` file (local development)
2. Environment variables
3. Pydantic defaults in `config.py`

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

### Custom Exceptions (Ready to implement)
```python
class TechHouseException(Exception):
    pass

class ResourceNotFound(TechHouseException):
    pass

class InvalidInput(TechHouseException):
    pass
```

## Testing Strategy

### Unit Tests
- Test repositories with mock database
- Test services with mock repositories
- Test utilities

### Integration Tests
- Test API endpoints with test database
- Test full request/response cycle

### Test Example
```python
def test_user_registration(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
```

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling
- Lazy loading relationships

### API Optimization
- Pagination on list endpoints
- Field filtering
- Query optimization

### Caching (Future Enhancement)
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_product_by_id(product_id: UUID):
    # Cached product lookup
    pass
```

## Deployment Considerations

### Development
- `DEBUG=true`
- SQLite or local PostgreSQL
- CORS allows all origins

### Staging
- `DEBUG=true` (for better error messages)
- Managed PostgreSQL
- CORS restricted to staging domains
- Comprehensive logging

### Production
- `DEBUG=false`
- Managed PostgreSQL (AWS RDS, DigitalOcean, etc)
- CORS restricted to approved domains
- SSL/TLS enabled
- Secret management (AWS Secrets Manager, HashiCorp Vault)
- Monitoring and alerting
- Database backups
- Rate limiting

## Monitoring & Logging

### Health Check
```
GET /health
Response: {"status": "healthy", "service": "TechHouse API"}
```

### Logging Levels
- `DEBUG` - Detailed information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## Conclusion

TechHouse demonstrates professional, production-ready backend development with:
- ✅ Clean, layered architecture
- ✅ SOLID principles
- ✅ Security best practices
- ✅ Comprehensive API design
- ✅ Maintainable code structure
- ✅ Docker containerization
- ✅ Professional documentation

This codebase serves as a reference implementation for BTEC Level 3 assignment requirements while maintaining real-world engineering standards.
