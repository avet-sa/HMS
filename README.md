# Hotel Management System (HMS) – Production-Grade Implementation

A comprehensive, full-featured hotel management system built with **Python FastAPI**, **SQLAlchemy**, and **Vanilla JavaScript**. This system demonstrates enterprise-level architecture, RBAC, payment processing, reporting, and operational automation.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Architecture](#project-architecture)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Core Features](#core-features)
9. [Security & RBAC](#security--rbac)
10. [Deployment](#deployment)
11. [Testing](#testing)
12. [Key Business Logic](#key-business-logic)
13. [Future Enhancements](#future-enhancements)

---

## Project Overview

**HMS** is a web-based hotel management system designed to automate and streamline all operational aspects of a hotel, including:

- **Room Inventory Management** – Track room types, pricing, maintenance status, and availability
- **Guest Management** – Register guests, capture contact & identification information, loyalty tracking
- **Booking Lifecycle** – Create, confirm, check-in, check-out, and cancel bookings with automatic billing
- **Payment Processing** – Track pending/paid/refunded payments with overpayment protection and auto-invoice generation
- **Cancellation & Refund Policies** – Define flexible, partial, and non-refundable policies with automated enforcement
- **No-Show Penalties** – Automatic penalty application for guests who fail to check in
- **Dynamic Pricing Rules** – Seasonal rates, weekend premiums, early bird discounts, long stay discounts, loyalty rewards with priority-based stacking
- **Centralized Configuration** – Pydantic-based settings management with environment variable validation
- **Reporting & Analytics** – Occupancy, revenue, and booking trend reports with cross-database support (PostgreSQL/SQLite)
- **Role-Based Access Control (RBAC)** – REGULAR users, MANAGER staff, and ADMIN roles with endpoint-level authorization
- **Rate Limiting** – API request throttling via slowapi to prevent abuse
- **Automated Invoicing** – Auto-generate invoices when payments are processed with PDF export capability
- **Audit Logging** – Comprehensive tracking of all critical operations (bookings, payments, auth) for compliance and debugging
- **Pagination & Filtering** – All list endpoints support pagination, filtering, sorting, and search
- **Docker Support** – Production-grade multi-stage Dockerfile and Docker Compose configuration
- **Graceful Shutdown** – Signal handlers and health check endpoints for production deployments

---

## Technology Stack

### **Backend**
- **Framework:** FastAPI 0.104+ (async-ready, modern Python web framework)
- **Database ORM:** SQLAlchemy 2.x
- **Database Migrations:** Alembic
- **Authentication:** JWT (python-jose), bcrypt password hashing
- **Validation:** Pydantic v2
- **Rate Limiting:** slowapi
- **CORS:** Starlette middleware
- **HTTP Client:** requests

### **Frontend**
- **HTML5** – Semantic markup
- **CSS3** – Dark/light theme toggle with localStorage persistence, responsive table-based layouts
- **Vanilla JavaScript (ES6+)** – Modularized architecture (7 separate modules: config, utils, theme, api, auth, ui, reports, app)
- **UI Components** – Table-based data display with badges, action buttons, and sortable columns
- **Forms** – Tab-based UI for rooms, guests, bookings, payments, invoices, and reports
- **Auto-load Data** – Automatically refreshes data when switching tabs
- **Admin Panel** – User management with 3-tier permission system (REGULAR, MANAGER, ADMIN) and activation controls

### **Database (Development & Test)**
- **SQLite** (in-memory for tests)
- **PostgreSQL** (production via Docker)

### **Infrastructure**
- **Docker** – Multi-stage build, non-root user, logging
- **Docker Compose** – Local dev and production configurations
- **Alembic** – Version-controlled schema migrations

### **Testing & CI/CD**
- **pytest** – Unit and integration tests
- **Starlette TestClient** – API testing
- **GitHub Actions** – CI workflow (test on push/PR)

---

## Project Architecture

### **Folder Structure**

```
HMS1/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app, router registration, CORS, rate limiting
│   │   ├── api/
│   │   │   ├── auth.py               # /auth/token, /auth/register
│   │   │   ├── users.py              # /users/me
│   │   │   ├── rooms.py              # /rooms/ CRUD
│   │   │   ├── room_types.py         # /room-types/ CRUD with auth
│   │   │   ├── guests.py             # /guests/ CRUD
│   │   │   ├── bookings.py           # /bookings/ + lifecycle endpoints
│   │   │   ├── payments.py           # /payments/ GET, /payments/create, /payments/{id}/process, refund
│   │   │   ├── invoices.py           # /invoices/ endpoints (list, generate, PDF download)
│   │   │   ├── pricing_rules.py      # /pricing-rules/ CRUD, /calculate-price
│   │   │   ├── audit_logs.py         # /audit-logs/ endpoints with filtering
│   │   │   └── reports.py            # /reports/occupancy, revenue, trends
│   │   ├── core/
│   │   │   ├── config.py             # Centralized configuration with pydantic-settings (40+ settings)
│   │   │   ├── permissions.py        # PermissionLevel enum (REGULAR, MANAGER, ADMIN)
│   │   │   └── security.py           # JWT token generation & validation
│   │   ├── dependencies/
│   │   │   └── security.py           # require_role dependency for RBAC
│   │   ├── db/
│   │   │   ├── models.py             # SQLAlchemy ORM models (User, Guest, Room, Booking, etc.)
│   │   │   ├── base.py               # DeclarativeBase export
│   │   │   └── session.py            # Database session factory
│   │   ├── schemas/
│   │   │   ├── user.py               # UserCreate, UserResponse Pydantic models
│   │   │   ├── room.py               # RoomCreate, RoomResponse
│   │   │   ├── room_type.py          # RoomTypeCreate, RoomTypeResponse
│   │   │   ├── guest.py              # GuestCreate, GuestResponse
│   │   │   ├── booking.py            # BookingCreate, BookingResponse
│   │   │   ├── payment.py            # PaymentCreate, PaymentResponse
│   │   │   ├── invoice.py            # InvoiceResponse
│   │   │   ├── pricing_rule.py       # PricingRuleCreate, PriceCalculationRequest/Response
│   │   │   ├── audit_log.py          # AuditLogResponse
│   │   │   └── report.py             # ReportResponse models
│   │   ├── services/
│   │   │   ├── user_service.py       # User CRUD & authentication
│   │   │   ├── room_service.py       # Room CRUD & availability logic
│   │   │   ├── guest_service.py      # Guest CRUD
│   │   │   ├── booking_service.py    # Booking lifecycle, no-show penalties
│   │   │   ├── payment_service.py    # Payment creation, processing, refunds, auto-invoice
│   │   │   ├── invoice_service.py    # Invoice generation and PDF export (reportlab)
│   │   │   ├── pricing_rule_service.py # Dynamic pricing engine with rule stacking
│   │   │   ├── report_service.py     # Occupancy, revenue, trends reports (SQLite/Postgres compatible)
│   │   │   └── refund_policy.py      # Cancellation & refund calculation
│   │   └── utils/
│   │       ├── availability.py       # Room availability checking logic
│   │       ├── audit.py              # Audit logging utility
│   │       └── pagination.py         # Pagination utilities
│   └── alembic/
│       ├── env.py                    # Alembic environment config
│       ├── script.py.mako            # Migration template
│       └── versions/
│           ├── 001_initial.py        # Base schema
│           ├── 003_add_booking_created_by.py
│           ├── 004_booking_lifecycle.py
│           ├── 005_payments_invoices.py
│           ├── 006_cancellation_policies.py
│           ├── 881741c5e475_add_audit_logs_table.py
│           └── b954b2b2b7e0_add_pricing_rules.py
├── frontend/
│   ├── index.html                    # Main dashboard (auth, rooms, guests, bookings, payments, invoices, reports)
│   ├── admin.html                    # Admin panel (user management with permission controls)
│   ├── styles.css                    # Dark/light theme, responsive table layouts, badge components
│   ├── admin.css                     # Admin panel specific styles
│   └── js/
│       ├── config.js                 # API base URL configuration
│       ├── utils.js                  # Utility functions (showMessage, formatters)
│       ├── theme.js                  # Dark/light theme toggle logic
│       ├── api.js                    # API client with Bearer token auth (apiFetch)
│       ├── auth.js                   # Authentication & user context
│       ├── ui.js                     # CRUD UI rendering (table rows, badges)
│       ├── reports.js                # Report generation and chart rendering
│       ├── app.js                    # Main application initialization
│       └── admin.js                  # Admin user management (permission cycling, activation)
├── tests/
│   ├── conftest.py                   # Pytest fixtures (client, admin_headers, regular_headers, db)
│   ├── test_auth_users.py            # Authentication & user endpoints
│   ├── test_rooms.py                 # Room CRUD & availability
│   ├── test_room_types.py            # Room type CRUD
│   ├── test_guests.py                # Guest CRUD
│   ├── test_bookings.py              # Booking lifecycle
│   ├── test_payments_integration.py  # Payment creation, processing, overpayment protection
│   ├── test_payment_service.py       # PaymentService unit tests
│   ├── test_cancellation_refund.py   # Refund policy logic
│   ├── test_no_show_penalties.py     # No-show penalty application
│   ├── test_invoice_service.py       # Invoice generation
│   ├── test_invoices.py              # Invoice API endpoints
│   ├── test_pricing_rules.py         # Dynamic pricing rules & calculations (14 tests)
│   ├── test_audit_logs.py            # Audit logging endpoints
│   ├── test_reports.py               # Report generation (occupancy, revenue, trends)
│   ├── test_availability.py          # Room availability logic
│   ├── test_integration.py           # End-to-end integration tests
│   └── test_api_smoke.py             # Smoke tests
├── Dockerfile                         # Development image (python:3.12.4-bookworm)
├── Dockerfile.prod                    # Production multi-stage image (Poetry)
├── docker-compose.yml                 # Local dev PostgreSQL + pgAdmin
├── docker-compose.prod.yml            # Production setup with resource limits
├── .dockerignore                      # Reduce build context
├── .env.example                       # Environment template
├── alembic.ini                        # Alembic config
├── pyproject.toml                     # Project metadata & dependencies
├── requirements.txt                   # Python dependencies
├── .github/workflows/ci-tests.yml     # GitHub Actions CI
└── README.md                          # This file

```

---

## Database Schema

### **Core Tables**

#### **users**
Represents staff/admin users with role-based permissions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | User ID |
| username | String(50) | UNIQUE, NOT NULL | Login username |
| password_hash | String | NOT NULL | bcrypt hash |
| permission_level | ENUM | NOT NULL, DEFAULT=REGULAR | REGULAR \| MANAGER \| ADMIN (3-tier RBAC) |
| is_active | Boolean | DEFAULT=True | Account status |
| created_at | DateTime | DEFAULT=now() | Account creation timestamp |
| updated_at | DateTime | onupdate=now() | Last modification timestamp |

#### **guests**
Stores guest information and loyalty/VIP tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Guest ID |
| name | String(100) | NOT NULL | First name |
| surname | String(100) | NOT NULL | Last name |
| phone_number | String(30) | Indexed | Contact number |
| email | String(100) | UNIQUE, Indexed | Email address |
| nationality | String(50) | | Guest nationality |
| gender | String(10) | | M/F/Other |
| birth_date | Date | | Date of birth |
| document_type | String(20) | | passport/id_card/driver_license |
| document_id | String(50) | | Identification number |
| loyalty_points | Integer | DEFAULT=0 | Reward points |
| vip_tier | Integer | DEFAULT=0 | VIP status (0=regular, 1-3=VIP levels) |
| is_active | Boolean | DEFAULT=True | Soft delete flag |
| created_at | DateTime | DEFAULT=now() | Registration timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

#### **room_types**
Defines room categories and base pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Room type ID |
| name | String(50) | UNIQUE, NOT NULL | Type name (Single, Double, Suite, etc.) |
| base_price | Numeric(10,2) | NOT NULL | Base nightly rate |
| capacity | Integer | NOT NULL | Max guest capacity |
| description | String(500) | | Features & amenities |
| created_at | DateTime | DEFAULT=now() | Creation timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

#### **rooms**
Individual room inventory with maintenance tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Room ID |
| number | String(10) | UNIQUE, Indexed | Room number (e.g., 101, 202) |
| room_type_id | Integer | FK→room_types | Room type |
| price_per_night | Numeric(10,2) | NOT NULL | Current nightly rate |
| square_meters | Integer | | Room size |
| floor | Integer | | Floor number |
| maintenance_status | ENUM | DEFAULT=AVAILABLE | AVAILABLE \| MAINTENANCE \| OUT_OF_SERVICE |
| has_view | Boolean | DEFAULT=False | Premium amenity |
| is_smoking | Boolean | DEFAULT=False | Smoking room flag |
| created_at | DateTime | DEFAULT=now() | Creation timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

#### **bookings**
Represents guest reservations with full lifecycle tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Booking ID |
| booking_number | String(20) | UNIQUE, Indexed | Confirmation number (e.g., BK-2024-00001) |
| guest_id | Integer | FK→guests, CASCADE | Guest reference |
| room_id | Integer | FK→rooms, CASCADE | Room reference |
| created_by | Integer | FK→users | Staff member who created booking |
| check_in | Date | Indexed | Check-in date |
| check_out | Date | Indexed | Check-out date |
| number_of_guests | Integer | DEFAULT=1 | Occupancy |
| price_per_night | Numeric(10,2) | NOT NULL | Locked-in rate at booking time |
| total_price | Numeric(10,2) | NOT NULL | check_in → check_out nights × rate |
| status | ENUM | Indexed | PENDING \| CONFIRMED \| CHECKED_IN \| CHECKED_OUT \| CANCELLED \| NO_SHOW |
| actual_check_in | DateTime | Nullable | Actual check-in timestamp |
| actual_check_out | DateTime | Nullable | Actual check-out timestamp |
| cancelled_at | DateTime | Nullable | Cancellation timestamp |
| final_bill | Numeric(10,2) | Nullable | Total amount due (includes extras, penalties) |
| special_requests | String(500) | | Guest notes |
| internal_notes | String(500) | | Staff notes |
| created_at | DateTime | Indexed | Booking creation timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

#### **payments**
Tracks payment records tied to bookings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Payment ID |
| booking_id | Integer | FK→bookings, CASCADE, Indexed | Associated booking |
| amount | Numeric(10,2) | NOT NULL | Payment amount |
| currency | String(10) | DEFAULT='USD' | Currency code |
| method | String(50) | NOT NULL | card/cash/bank_transfer/online |
| status | ENUM | DEFAULT=PENDING | PENDING \| PAID \| FAILED \| REFUNDED |
| created_at | DateTime | DEFAULT=now() | Payment creation timestamp |
| processed_at | DateTime | Nullable | Payment completion timestamp |
| refunded_at | DateTime | Nullable | Refund timestamp |
| reference | String(100) | Nullable | Transaction reference ID |

#### **invoices**
Automatically generated upon payment processing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Invoice ID |
| booking_id | Integer | FK→bookings, CASCADE, Indexed | Associated booking |
| invoice_number | String(50) | UNIQUE, Indexed | Unique invoice number |
| subtotal | Numeric(10,2) | NOT NULL | Base amount |
| tax | Numeric(10,2) | NOT NULL | Tax applied |
| total | Numeric(10,2) | NOT NULL | subtotal + tax |
| issued_at | DateTime | DEFAULT=now() | Invoice issue timestamp |

#### **cancellation_policies**
Defines refund tiers based on days before check-in.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Policy ID |
| name | String(100) | UNIQUE, NOT NULL | Policy name (Standard, Flexible, Non-Refundable) |
| full_refund_days | Integer | DEFAULT=7 | Days before check-in for 100% refund |
| partial_refund_days | Integer | DEFAULT=2 | Days before check-in for partial refund |
| partial_refund_percentage | Numeric(5,2) | DEFAULT=50 | Refund % if within partial_refund_days |
| is_active | Boolean | DEFAULT=True | Policy status |
| created_at | DateTime | DEFAULT=now() | Creation timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

#### **pricing_rules**
Dynamic pricing rules for automated rate adjustments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Rule ID |
| name | String(100) | NOT NULL | Rule name |
| description | String(500) | NULL | Rule description |
| rule_type | String(20) | NOT NULL | seasonal \| weekend \| early_bird \| last_minute \| loyalty \| long_stay \| custom |
| priority | Integer | DEFAULT=0 | Higher priority rules applied first |
| adjustment_type | String(20) | NOT NULL | percentage \| fixed_amount |
| adjustment_value | Numeric(10,2) | NOT NULL | Adjustment value (e.g., 20 = 20% or $20) |
| room_type_id | Integer | FK(room_types), NULL | Applies to specific room type (NULL = all) |
| start_date | Date | NULL | Rule start date (NULL = no restriction) |
| end_date | Date | NULL | Rule end date (NULL = no restriction) |
| applicable_days | String(50) | NULL | JSON array of weekdays [0-6] (0=Monday) |
| min_nights | Integer | NULL | Minimum stay required |
| min_advance_days | Integer | NULL | Minimum days before check-in |
| max_advance_days | Integer | NULL | Maximum days before check-in |
| min_loyalty_tier | Integer | NULL | Minimum guest loyalty tier |
| is_active | Boolean | DEFAULT=True | Rule status |
| created_at | DateTime | DEFAULT=now() | Creation timestamp |
| updated_at | DateTime | onupdate=now() | Last update timestamp |

**Default Rules:**
- Weekend Premium: +20% for Friday/Saturday nights (priority 10)
- Early Bird Discount: -15% for bookings 30+ days in advance (priority 5)
- Long Stay Discount: -10% for 7+ night stays (priority 8)

#### **audit_logs**
Comprehensive tracking of all critical operations for compliance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK | Log ID |
| user_id | Integer | FK(users), NULL | User who performed action |
| username | String(50) | NULL | Denormalized username |
| action | String(50) | NOT NULL | CREATE \| UPDATE \| DELETE \| LOGIN_SUCCESS \| etc. |
| entity_type | String(50) | NOT NULL | booking \| payment \| room \| user \| etc. |
| entity_id | Integer | NULL | ID of affected entity |
| description | String(500) | NULL | Human-readable description |
| old_values | String(2000) | NULL | JSON of old values |
| new_values | String(2000) | NULL | JSON of new values |
| ip_address | String(45) | NULL | Client IP (IPv4/IPv6) |
| user_agent | String(500) | NULL | Client user agent |
| created_at | DateTime | DEFAULT=now(), INDEXED | Timestamp |

---

## API Endpoints

### **Authentication**
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/token | None | OAuth2 token endpoint (form-encoded body: username, password, grant_type) |
| POST | /auth/register | None | Create new user account |

### **Users**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /users/me | Bearer JWT | Any | Current authenticated user info |

### **Room Types**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /room-types/ | Bearer JWT | Any | List all room types |
| POST | /room-types/ | Bearer JWT | MANAGER, ADMIN | Create new room type |
| PUT | /room-types/{id} | Bearer JWT | MANAGER, ADMIN | Update room type |
| DELETE | /room-types/{id} | Bearer JWT | ADMIN | Delete room type |

### **Rooms**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /rooms/ | Bearer JWT | Any | List all rooms with availability check |
| POST | /rooms/ | Bearer JWT | MANAGER, ADMIN | Create room |
| GET | /rooms/{id} | Bearer JWT | Any | Get room details |
| PUT | /rooms/{id} | Bearer JWT | MANAGER, ADMIN | Update room (price, maintenance status) |
| DELETE | /rooms/{id} | Bearer JWT | ADMIN | Delete room |

### **Guests**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /guests/ | Bearer JWT | Any | List all guests |
| POST | /guests/ | Bearer JWT | Any | Register new guest |
| GET | /guests/{id} | Bearer JWT | Any | Get guest details |
| DELETE | /guests/{id} | Bearer JWT | MANAGER, ADMIN | Delete guest |

### **Bookings**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /bookings/ | Bearer JWT | Any | List bookings (REGULAR: own only) |
| POST | /bookings/ | Bearer JWT | Any | Create booking |
| GET | /bookings/{id} | Bearer JWT | Any | Get booking details (RBAC check) |
| PUT | /bookings/{id} | Bearer JWT | MANAGER, ADMIN | Modify booking dates |
| DELETE | /bookings/{id} | Bearer JWT | ADMIN | Delete booking |
| POST | /bookings/{id}/confirm | Bearer JWT | MANAGER, ADMIN | Confirm pending booking |
| POST | /bookings/{id}/check-in | Bearer JWT | MANAGER, ADMIN | Check in guest |
| POST | /bookings/{id}/check-out | Bearer JWT | MANAGER, ADMIN | Check out guest & finalize bill |
| POST | /bookings/{id}/cancel | Bearer JWT | Any | Cancel booking (RBAC: REGULAR own only) |
| POST | /bookings/{id}/no-show | Bearer JWT | MANAGER, ADMIN | Mark no-show & apply penalty |

### **Payments**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /payments/ | Bearer JWT | Any | List payments (REGULAR: own bookings only) |
| POST | /payments/create | Bearer JWT | Any | Create payment for booking |
| POST | /payments/{id}/process | Bearer JWT | MANAGER, ADMIN | Mark payment as PAID & auto-invoice |
| POST | /payments/{id}/fail | Bearer JWT | MANAGER, ADMIN | Mark payment as FAILED |
| POST | /payments/{id}/refund | Bearer JWT | MANAGER, ADMIN | Refund payment (only PAID payments) |

### **Invoices**
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /invoices/ | Bearer JWT | ANY | List all invoices |
| POST | /invoices/{booking_id} | Bearer JWT | MANAGER, ADMIN | Generate invoice for booking |
| GET | /invoices/{invoice_id}/pdf | Bearer JWT | ANY | Download invoice as PDF |

### **Pricing Rules** (Dynamic pricing engine)
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /pricing-rules/ | Bearer JWT | Any | List all pricing rules with filters |
| POST | /pricing-rules/ | Bearer JWT | MANAGER, ADMIN | Create new pricing rule |
| GET | /pricing-rules/{id} | Bearer JWT | Any | Get specific pricing rule |
| PATCH | /pricing-rules/{id} | Bearer JWT | MANAGER, ADMIN | Update pricing rule |
| DELETE | /pricing-rules/{id} | Bearer JWT | ADMIN | Delete pricing rule |
| POST | /pricing-rules/calculate-price | Bearer JWT | Any | Calculate price with applied rules |

**Query Parameters (Pricing Rules):**
- `is_active` (bool) - Filter by active status
- `rule_type` - Filter by type (seasonal, weekend, early_bird, last_minute, loyalty, long_stay, custom)

**Pricing Rule Types:**
- `seasonal` - Date range based pricing (e.g., summer rates)
- `weekend` - Day of week premiums (Friday/Saturday)
- `early_bird` - Advance booking discounts (e.g., 30+ days)
- `last_minute` - Last-minute booking adjustments
- `loyalty` - Loyalty tier based discounts
- `long_stay` - Extended stay discounts (e.g., 7+ nights)
- `custom` - Custom business rules

### **Reports** (Manager/Admin analytics)
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /reports/occupancy | Bearer JWT | MANAGER, ADMIN | Occupancy rate by date range |
| GET | /reports/revenue | Bearer JWT | MANAGER, ADMIN | Revenue totals by date range (SQLite/Postgres compatible) |
| GET | /reports/trends | Bearer JWT | MANAGER, ADMIN | Booking trends over time |

### **Audit Logs** (Admin compliance tracking)
| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | /audit-logs/ | Bearer JWT | MANAGER, ADMIN | List audit logs with filtering and pagination |
| GET | /audit-logs/{id} | Bearer JWT | MANAGER, ADMIN | Get specific audit log details |

**Query Parameters (Audit Logs):**
- `page` (default: 1) - Page number
- `page_size` (default: 50, max: 100) - Items per page
- `user_id` - Filter by user ID
- `action` - Filter by action (CREATE, UPDATE, DELETE, LOGIN_SUCCESS, etc.)
- `entity_type` - Filter by entity type (booking, payment, user, etc.)
- `entity_id` - Filter by specific entity ID
- `date_from` - Filter from date (ISO format)
- `date_to` - Filter to date (ISO format)
- `sort_by` - Sort field (default: created_at)
- `sort_order` - Sort order (asc/desc, default: desc)

**Query Parameters (Reports):**
- `start_date` (YYYY-MM-DD)
- `end_date` (YYYY-MM-DD)

---

## Installation & Setup

### **Prerequisites**
- Python 3.12+
- PostgreSQL 14+ (production) or SQLite (development)
- Docker & Docker Compose (optional but recommended)
- pip or uv package manager

### **Local Development (Without Docker)**

1. **Clone & navigate to project:**
   ```bash
   cd HMS1
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file (from `.env.example`):**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your database URL and JWT secret.

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start backend server:**
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Server runs at `http://127.0.0.1:8000`
   API docs at `http://127.0.0.1:8000/docs` (Swagger UI)

7. **Open frontend:**
   Open `frontend/index.html` in a web browser.
   Default auth: test with `/auth/register` or use seeded credentials.

### **Local Development (With Docker)**

1. **Build & start containers:**
   ```bash
   docker-compose up --build
   ```
   - Backend: `http://localhost:8000`
   - PostgreSQL: `localhost:5432`
   - pgAdmin: `http://localhost:5050` (admin@pgadmin.org / changeme)

2. **Run migrations inside container:**
   ```bash
   docker-compose exec hms_backend alembic upgrade head
   ```

3. **Access frontend:**
   Open `frontend/index.html` in a browser.

### **Production Deployment**

1. **Build production image:**
   ```bash
   docker build -f Dockerfile.prod -t hms:latest .
   ```

2. **Start with production compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Environment variables** (set before running):
   - `DATABASE_URL` – PostgreSQL connection string
   - `JWT_SECRET` – Secret for signing tokens
   - `FRONTEND_ALLOWED_ORIGINS` – Comma-separated CORS whitelist
   - `ENVIRONMENT` – `production` or `development`

---

## Usage Guide

### **Admin Workflow**

1. **Register as first admin:**
   - Go to `frontend/index.html` → Sign In → Create Account
   - Use any username/password (create account as REGULAR by default)
   - Access Admin Panel (⚡ Admin button in header)
   - First registered user can be promoted to ADMIN via admin panel by cycling permissions

2. **Manage users (Admin Panel):**
   - View all users with ID, username, permission level, status, and creation date
   - Cycle user permissions: REGULAR → MANAGER → ADMIN → REGULAR
   - Activate/deactivate user accounts
   - View user statistics (Total, Admins, Managers, Active)

3. **Create room types:**
   - Dashboard → Rooms tab → Form (requires MANAGER/ADMIN role)
   - Input: Type name, base price, capacity

4. **Add rooms:**
   - Dashboard → Rooms tab → Add New Room
   - View rooms in table with: ID, Room #, Type, Price/Night, Size, Max Guests, Floor, Status
   - Delete rooms with confirmation dialog
   - Assign type, price, floor, square meters

4. **Register guests:**
   - Dashboard → Guests tab → Register Guest
   - Minimal: name, surname, email (optional but recommended)

5. **Create bookings:**
   - Dashboard → Bookings tab → New Reservation
   - Select guest, room, check-in/check-out dates
   - System auto-calculates nightly price & total

6. **Manage booking lifecycle:**
   - Confirm → Check-in → Check-out (updates status & calculates final bill)
   - Or Cancel (applies refund policy if within cancellation window)
   - Or Mark No-Show (applies penalty automatically)

7. **Process payments:**
   - Dashboard → Payments tab → Create Payment
   - Specify booking ID, amount, method
   - Admin confirms payment processing (→ PAID, auto-generates invoice)
   - Admin can refund (if PAID) or fail (if PENDING)

8. **Manage invoices:**
   - Dashboard → Invoices tab
   - View all invoices with booking details, amounts, and issue dates
   - Generate invoice manually for checked-out booking
   - Download invoices as PDF with professional formatting

9. **View reports:**
   - Dashboard → Reports tab
   - Select date range and click Occupancy/Revenue/Trends
   - Reports display JSON data (could be formatted as charts in future)

### **Regular User Workflow**

- Create own bookings
- View own bookings, payments, and cancellations
- Cannot process payments or refunds (MANAGER/ADMIN only)
- Cannot access admin panel or user management

---

## Core Features

### **1. User Management & RBAC**
- **Three-tier permission system:**
  - **REGULAR** – Basic users (view own data)
  - **MANAGER** – Staff level (create/modify bookings, payments, guests)
  - **ADMIN** – Full system access (user management, all CRUD operations)
- **Admin Panel:**
  - Table-based user listing with sortable columns
  - Permission cycling via button (REGULAR → MANAGER → ADMIN → REGULAR)
  - User activation/deactivation toggle
  - Real-time user statistics (Total, Admins, Managers, Active)
- **JWT-based authentication** with Bearer tokens
- **bcrypt password hashing** for security

### **2. Room & Booking Management**
- **Table-based UI** with enhanced columns:
  - Rooms: ID, Room #, Type, Price/Night, Size (m²), Max Guests, Floor, Status
  - Bookings: ID, Guest, Room, Check-in, Check-out, Nights, Total Price, Status
  - Status badges with color coding (green=confirmed, blue=checked in, amber=pending)
- **Room availability checking** across date ranges
- **Booking lifecycle:**
  ```
  PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
       or ↓              or ↓
  CANCELLED (refund)    NO_SHOW (penalty)
  ```

### **3. Guest Management**
- **Enhanced guest table** with columns:
  - ID, Name, Email, Phone, Registration Date, Total Bookings
- Guest profile tracking with loyalty points and VIP tiers
- Soft delete support (is_active flag)

### **4. Payment & Invoice System**
- **Payment table** with detailed tracking:
  - ID, Booking, Amount, Currency, Method, Reference, Date, Status
- **Smart badge colors:**
  - Green = paid/completed
  - Amber = pending/processing
  - Blue = refunded
  - Red = failed/declined/canceled
- Auto-generate invoice on payment completion
- Prevent overpayments with validation
- Support for multiple payment methods (card, cash, bank transfer, online)

### **5. Reporting & Analytics**
- **Occupancy Report:** Daily occupancy rates with line chart visualization (520px height)
- **Revenue Report:** Daily revenue trends with aggregation for large date ranges (520px height)
- **Trends Report:** Booking patterns, cancellation rates, average stay duration (420px height, 80% width)
- **Interactive charts** with Chart.js
- **Export functionality** for all report types

### **6. UI/UX Features**
- **Dark/light theme toggle** with localStorage persistence
- **Responsive table layouts** with horizontal scrolling
- **Badge system** with transparent backgrounds and bullet indicators
- **90% base font size** for optimal information density
- **Modular JavaScript architecture:**
  - config.js – API configuration
  - utils.js – Utility functions
  - theme.js – Theme management
  - api.js – HTTP client with auth (includes invoice & PDF download)
  - auth.js – Authentication logic
  - ui.js – CRUD rendering (includes invoice table & PDF download)
  - reports.js – Chart generation
  - app.js – Application initialization (auto-loads data on tab switch)
  - admin.js – User management

### **7. Dynamic Pricing Rules**
- **Rule-based pricing engine** with 7 rule types:
  - **seasonal** – Date range based pricing (e.g., summer/winter rates)
  - **weekend** – Day-of-week premiums (Friday/Saturday)
  - **early_bird** – Advance booking discounts (e.g., 30+ days)
  - **last_minute** – Last-minute booking adjustments
  - **loyalty** – Loyalty tier based discounts
  - **long_stay** – Extended stay discounts (e.g., 7+ nights)
  - **custom** – Custom business rules
- **Priority-based stacking** – Multiple rules apply cumulatively
- **Flexible adjustments** – Percentage or fixed amount
- **Advanced filtering:**
  - Room type specific
  - Date ranges (start_date/end_date)
  - Days of week (JSON array)
  - Minimum nights required
  - Advance booking windows
  - Loyalty tier requirements
- **Price calculation API** returns:
  - Base price and adjusted price
  - List of all applied rules with before/after prices
  - Total savings amount
  - Detailed breakdown for transparency
- **Default rules included:**
  - Weekend Premium: +20%
  - Early Bird: -15% (30+ days advance)
  - Long Stay: -10% (7+ nights)

### **8. Cancellation & Refund Policies**
- **ADMIN:** Full system access – user management, deletions, role changes

Enforced via `@require_role(PermissionLevel.ADMIN, PermissionLevel.MANAGER)` dependency.

### **2. Booking Lifecycle Automation**
```
PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT (final bill calculated)
         or ↓
       CANCELLED (applies refund policy)
         or ↓
       NO_SHOW (applies penalty)
```

### **3. Payment & Invoice System**
- Create payments in PENDING state
- Admin can process (→ PAID), fail (→ FAILED), or refund (→ REFUNDED)
- Auto-generate invoice on PAID
- Prevent overpayments (check against final bill)
- **PDF Invoice Export:**
  - Professional PDF invoices using reportlab library
  - Includes invoice number, booking details, guest information
  - Itemized charges with subtotal, 10% tax, and total
  - Download from Invoices tab or via API endpoint

### **4. Cancellation & Refund Policies**
- Define flexible policies (e.g., 7 days = 100% refund, 2 days = 50% refund, <2 = no refund)
- Automatic calculation on cancellation
- Multiple policies can be configured (currently hardcoded to standard in code; future enhancement for policy selection)

### **5. No-Show Penalties**
- Mark booking as NO_SHOW → automatic penalty fee added to final_bill
- Currently fixed penalty (configurable in code; future: policy-driven)

### **6. Reporting & Analytics**
- **Occupancy Report:** % rooms occupied by date range
- **Revenue Report:** Total revenue grouped by date (SQLite/Postgres compatible via `func.date()`)
- **Trends Report:** Booking volume & patterns over time

### **7. Rate Limiting**
- slowapi middleware configured on `/` (100 requests/minute default)
- Prevents API abuse

### **8. CORS & Security**
- CORS whitelist in `.env` (default: localhost:5500, localhost:3000)
- JWT Bearer tokens with expiration
- Password hashing via bcrypt

---

## Security & RBAC

### **JWT Authentication**
1. Client POSTs credentials (URL-encoded) to `/auth/token`
2. Backend validates, returns `{"access_token": "eyJ...", "token_type": "bearer"}`
3. Client stores token in `authToken` global variable and localStorage
4. All subsequent requests include `Authorization: Bearer <token>` header
5. Backend validates token signature & expiration via `get_current_user` dependency

### **Password Security**
- Passwords hashed with bcrypt (12 rounds)
- Never stored in plain text
- Verified on login via `verify_password()`

### **Endpoint Authorization**
- `get_current_user` – Requires valid token (all endpoints)
- `require_role(PermissionLevel.MANAGER, ...)` – Requires token + role match
- REGULAR users can only view/modify own bookings/payments (checked in service layer)

### **CORS**
- Frontend must be in `FRONTEND_ALLOWED_ORIGINS` (env var)
- Default: `localhost:5500`, `localhost:3000`

### **Rate Limiting**
- 100 requests per minute per IP address
- Returns 429 Too Many Requests when exceeded

---

## Deployment

### **Docker Production Build**

**Multi-stage Dockerfile (`Dockerfile.prod`):**
1. **Builder stage:** Install Python, Poetry, build dependencies
2. **Runtime stage:** Copy built wheels, install app, non-root user, logging directory

**Benefits:**
- Smaller image size (no build tools in final layer)
- Non-root execution (security)
- JSON logging for container orchestration
- Resource limits via `docker-compose.prod.yml`

### **Environment Variables**
```bash
DATABASE_URL=postgresql://user:pass@db:5432/hms_prod
JWT_SECRET=your-super-secret-key-min-32-chars
ENVIRONMENT=production
FRONTEND_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### **Health Checks**
- `GET /` returns `{"message": "Welcome to the Hotel Management System API"}`
- Docker health check can probe this endpoint

### **Logging**
- JSON-formatted logs to `/var/log/hms/app.log` (mounted volume)
- Rotation policy: 10MB per file, 5 backups

### **Database Migrations**
Run before starting app:
```bash
docker-compose exec hms_backend alembic upgrade head
```

---

## Testing

### **Run All Tests**
```bash
pytest tests/ -v
```

### **Run Specific Test File**
```bash
pytest tests/test_bookings.py -v
```

### **Run with Coverage**
```bash
pytest tests/ --cov=backend.app --cov-report=html
```

### **Test Fixtures** (`conftest.py`)
- `client` – FastAPI TestClient
- `admin_headers` – JWT token for ADMIN user
- `regular_headers` – JWT token for REGULAR user
- `db` – SQLite in-memory session

### **Test Categories**
- **Unit Tests:** Service layer logic (PaymentService, BookingService, etc.)
- **Integration Tests:** Full API flow (auth → booking → payment → refund)
- **Smoke Tests:** Basic endpoint health checks

### **GitHub Actions CI**
- Runs on push/PR to master
- Tests against Python 3.12
- Workflow: `.github/workflows/ci-tests.yml`

---

## Key Business Logic

### **Room Availability Check**
```python
# No overlapping confirmed/checked-in bookings
SELECT * FROM bookings 
WHERE room_id = ? 
  AND check_in < end_date 
  AND check_out > start_date 
  AND status != 'cancelled'
```

### **Final Bill Calculation**
```
base_bill = (check_out_date - check_in_date) * price_per_night
final_bill = base_bill + taxes + (no_show_penalty if applicable)
```

### **Refund Amount**
```
days_before = (check_in_date - today).days
if days_before >= full_refund_days:
    refund = 100%
elif days_before >= partial_refund_days:
    refund = partial_refund_percentage
else:
    refund = 0%
```

### **Overpayment Prevention**
```python
paid_total = SUM(payment.amount) WHERE booking_id = ? AND status = 'PAID'
if paid_total + new_payment > booking.final_bill:
    raise HTTPException(400, "Would exceed booking final bill")
```

### **No-Show Penalty**
```python
if booking.status != 'checked_in' and booking.check_in < today:
    penalty_amount = booking.final_bill * 0.2  # 20% penalty (configurable)
    booking.final_bill += penalty_amount
    booking.status = 'no_show'
```

---

## Future Enhancements

1. **Mobile App** – React Native or Flutter client
2. **Email Notifications** – Booking confirmations, check-in reminders, invoices
3. **SMS Alerts** – Payment notifications, check-in codes
4. **Advanced Pricing** – Seasonal rates, dynamic pricing, discounts
5. **Loyalty Program** – Points accumulation, tier-based benefits
6. **Staff Scheduling** – Employee shifts, availability tracking
7. **Housekeeping Management** – Room cleaning tasks, inspections
8. **Integration** – Payment gateways (Stripe, PayPal), third-party booking (OTA sync)
9. **Analytics Dashboard** – Charts, KPIs, forecasting
10. **Audit Logging** – Track all data modifications for compliance
11. **Multi-Property Support** – Manage multiple hotels from one system
12. **Guest Portal** – Self-service check-in, booking modifications, invoices

---

## Support & Documentation

- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **GitHub Issues:** Report bugs or request features
- **Database Migrations:** See `alembic/versions/` for schema evolution history
- **Tests:** See `tests/` directory for usage examples

---

## License & Credits

Built as a comprehensive demonstration of enterprise Python web development patterns, suitable for production deployment or academic purposes.

---
