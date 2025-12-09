# Hotel Management System — Product Requirements Document (PRD)

**Version:** 1.0  
**Author:** Avet  
**Date:** 2025  
**Status:** Draft

---

## 15. Database Schema Considerations

### 15.1. Key Tables

- [x] **users** - staff and customer accounts
- [x] **rooms** - room inventory
- [x] **room_types** - standard, deluxe, suite, etc.
- [x] **bookings** - reservation records
- [x] **payments** - payment transactions
- [x] **invoices** - auto-generated invoices
- [x] **guests** - guest information and loyalty tracking
- [x] **cancellation_policies** - refund policy definitions
- [ ] **pricing_rules** - seasonal and dynamic pricing
- [ ] **housekeeping_tasks** - cleaning assignments
- [ ] **audit_logs** - track all critical operations

### 15.2. Important Indexes

- [x] bookings(check_in, check_out, status)
- [x] rooms(number, room_type_id)
- [x] payments(booking_id, status)
- [x] guests(email, phone_number)
- [x] bookings(booking_number, created_at)
- [ ] audit_logs(timestamp, user_id)

### 15.3. Data Integrity

- [x] Foreign key constraints
- [x] Check constraints for dates (check_out > check_in)
- [x] Unique constraints on room numbers
- [x] Soft deletes for guests (is_active flag)
- [x] Unique constraints on booking numbers
- [x] Cascade deletes configured

---

## 16. API Design Principles

### 16.1. RESTful Conventions

- [x] Use proper HTTP verbs (GET, POST, PUT, PATCH, DELETE)
- [x] Consistent naming: `/bookings`, `/rooms`, `/guests`, `/payments`
- [x] Proper status codes (200, 201, 400, 401, 403, 404, 500)
- [x] Pagination for list endpoints (page, page_size params with PaginatedResponse)
- [x] Filtering and sorting support (status, dates, search queries)

### 16.2. Response Format

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 16.3. Error Format

```json
{
  "success": false,
  "error": {
    "code": "BOOKING_CONFLICT",
    "message": "Room already booked for these dates",
    "details": {...}
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 17. Deployment Strategy

### 17.1. Development Environment

- Docker Compose with:
  - FastAPI app
  - PostgreSQL
  - Redis (for Celery)
  - Nginx (reverse proxy)

### 17.2. Production Considerations

- [x] Environment variables for secrets
- [x] Database migrations with Alembic
- [x] Health check endpoints
- [x] Graceful shutdown handling (SIGTERM/SIGINT with 10s timeout)
- [x] Rate limiting (slowapi)
- [x] CORS configuration

### 17.3. CI/CD Pipeline (Optional)

- [ ] GitHub Actions or GitLab CI
- [ ] Run tests on PR
- [ ] Linting and code quality checks
- [ ] Auto-deploy to staging on merge to main

---

## 18. Future Enhancements (Post-MVP)

- Guest portal for self-service booking
- Email/SMS notifications with templates
- Integration with payment gateways
- Multi-language support
- Advanced analytics and BI dashboards
- Mobile apps (iOS/Android)
- Loyalty program
- Integration with channel managers
- API rate limiting per user
- Websockets for real-time updates

---

## 1. Overview

### 1.1. Purpose

The purpose of this project is to build a production-grade Hotel Management System (HMS) with a clean backend architecture, real-world business logic, and a functional administrative UI. The system should resemble professional hotel software, not a simple CRUD student project.

### 1.2. Goals

- Provide a robust backend API built with FastAPI, PostgreSQL, SQLAlchemy, JWT, and Alembic.
- Implement real hotel logic, not simplified models (availability, pricing, check-in/out, room assignment).
- Deliver a usable web-based front office panel.
- Demonstrate engineering principles: modular architecture, tests, documentation, CI, deployment.

---

## 2. Scope

### 2.1. In-Scope

- [x] Room management
- [x] Booking system with availability engine
- [x] User authentication & role-based permissions (3-tier: REGULAR, MANAGER, ADMIN)
- [x] Check-in/out workflows
- [x] Payment simulation
- [ ] Housekeeping workflow
- [x] Reporting (occupancy, revenue, trends)
- [ ] Background tasks & scheduled tasks
- [x] PDF generation capability (invoice service)
- [x] Monitoring & logging
- [x] Minimal but functional frontend UI in dark theme
- [ ] Email notifications (simulated or SMTP)
- [x] Audit logging for critical operations (bookings, payments, auth)

### 2.2. Out-of-Scope

- Real payment integration (Stripe, etc.)
- Mobile app
- Multi-hotel cluster management (optional future extension)
- Guest loyalty/rewards program
- Restaurant/spa/amenities booking
- Channel manager integrations (Booking.com, Expedia)

---

## 3. User Roles & Permissions

### 3.1. System Admin

- Manage all data
- CRUD rooms, users, pricing rules
- Access all reports and logs

### 3.2. Front Office Agent

- Create bookings
- Perform check-in/out
- Assign rooms
- View availability calendar
- View guest info and payment status

### 3.3. Manager

- Access analytics dashboard
- Revenue, occupancy, reports
- Override pricing and room assignment

### 3.4. Housekeeper

- See room cleaning tasks
- Mark room as cleaned
- See daily cleaning schedule

### 3.5. Customer (optional)

- View booking info
- Download confirmation
- Update personal data

---

## 4. Core Features

### 4.1. Authentication & Authorization

- [x] JWT-based login
- [x] Token contains user role (permission_level)
- [x] Role-based route protection (require_role dependency)
- [x] Password hashing (bcrypt)

### 4.2. Room Management

**Features:**

- [x] Room CRUD
- [x] Room types with base pricing and capacity
- [x] Room status (maintenance_status: AVAILABLE, MAINTENANCE, OUT_OF_SERVICE)
- [x] Facilities & metadata (square_meters, floor, has_view, is_smoking)

### 4.3. Booking System

The heart of the application.

#### 4.3.1. Availability Engine

**Inputs:**

- [x] check-in date
- [x] check-out date
- [x] number of guests
- [x] room type (optional)

**Output:**

- [x] available rooms list
- [x] price breakdown
- [ ] alerts (conflicts, high occupancy)

**Business Rules:**

- [x] Minimum 1 night stay
- [ ] Maximum advance booking: 365 days
- [ ] Check-in time: 14:00, Check-out time: 11:00
- [x] Same-day booking allowed
- [x] Handle edge cases with date validation

#### 4.3.2. Overbooking Prevention

- [x] Database-level transactional locking
- [x] Prevent double booking (availability check)
- [x] Atomic room assignment

#### 4.3.3. Booking States

- [x] PENDING (new reservation, awaiting payment)
- [x] CONFIRMED (payment received)
- [x] CHECKED_IN
- [x] CHECKED_OUT
- [x] CANCELLED
- [x] NO_SHOW

**State Transitions:**

- [x] PENDING → CONFIRMED (on payment)
- [x] PENDING → CANCELLED (manual)
- [x] CONFIRMED → CHECKED_IN (on arrival)
- [x] CHECKED_IN → CHECKED_OUT (on departure)
- [x] CONFIRMED → NO_SHOW (if guest doesn't arrive)

#### 4.3.4. Room Assignment Algorithm

**Rules:**

- [ ] Prefer clean & available rooms
- [ ] Minimize room switching
- [ ] Prefer same-floor continuity
- [ ] Avoid assigning rooms under maintenance

### 4.4. Pricing Engine

- [ ] Seasonal pricing
- [ ] Weekend multiplier
- [ ] Last-minute discount
- [ ] Manager override
- [ ] Store all price rules in DB
- [ ] Produce final price per booking

### 4.5. Check-in / Check-out Workflow

**Check-in:**

- [ ] Validate booking
- [ ] Assign room
- [ ] Change room status to OCCUPIED
- [ ] Generate registration card PDF

**Check-out:**

- [x] Calculate extras (if any)
- [x] Produce invoice PDF (via invoices tab or auto-generated on payment)
- [ ] Set room → CLEANING
- [ ] Free room after cleaning

### 4.6. Payments (Mock)

**Types:**

- [x] Card (mock API)
- [x] Cash
- [x] Bank transfer
- [x] Online
- [x] Refund simulation

**Flows:**

- [x] payment pending
- [x] payment successful (paid/completed)
- [x] payment failed
- [x] refund issued

### 4.7. Housekeeping Module

- [ ] Daily auto-generated cleaning tasks
- [ ] Housekeeper panel
- [ ] Room cleaning status
- [ ] Manager overview

---

## 5. Background Tasks

Powered by FastAPI BackgroundTasks or Celery + Redis.

- [ ] Send reservation confirmation emails
- [ ] Generate daily cleaning schedule at midnight
- [ ] Auto-cancel unpaid reservations
- [ ] Logging & metrics aggregation

---

## 6. Reports & Dashboards

### 6.1. Manager Dashboard

- [x] Occupancy rate (daily, average, min, max)
- [x] Revenue charts (daily revenue with Chart.js)
- [ ] Housekeeping stats
- [ ] Upcoming arrivals & departures

### 6.2. Front Office Dashboard

- [x] Today's check-ins (via booking filters)
- [x] Today's check-outs (via booking filters)
- [ ] Rooms needing cleaning

---

## 7. PDF Generation

Using ReportLab for professional PDF documents.

**Documents:**

- [ ] Booking confirmation
- [ ] Registration card
- [x] Invoice (auto-generated on payment + manual generation + PDF download)
- [ ] Daily report

---

## 8. Logging & Monitoring

### 8.1. Logging

- [ ] JSON logs
- [ ] request_id generated per request
- [ ] store user_id, endpoint, status, latency

### 8.2. Monitoring (Prometheus)

**Custom metrics:**

- [ ] API latency
- [ ] error count
- [ ] active bookings count
- [ ] occupancy rate

**Optional:** 
- [ ] Grafana dashboard

---

## 9. Frontend Requirements

### 9.1. Technologies

- [ ] React or Vue
- [ ] Minimal, dark modern theme
- [ ] Uses your backend's REST API
- [ ] Token stored in memory or secure cookie

### 9.2. Features

- [x] Login page
- [x] Dashboard (role-based with 3-tier permissions)
- [x] Booking creation form
- [x] Room management with table view
- [x] Guest management with enhanced details
- [x] Payment processing interface
- [x] Reports with interactive charts
- [x] Admin panel for user management
- [ ] Availability calendar view
- [x] Check-in/out panel (status transitions)
- [ ] Housekeeping screen

**UI is functional, clean, dark themed with table-based layouts and badge system.**

---

## 10. Non-Functional Requirements

### 10.1. Performance

- [ ] system must handle 50 concurrent users
- [ ] booking creation must respond < 250ms
- [ ] availability search < 400ms

### 10.2. Security

- [ ] JWT authentication
- [ ] minimal password requirements
- [ ] protection against overbooking
- [ ] role-based route access

### 10.3. Reliability

- [ ] transactional guarantees on booking
- [ ] 100% consistency of room status

### 10.4. Scalability

- [ ] database indexing
- [ ] horizontal scaling possible

---

## 11. Project Architecture

**Layers:**

- API (FastAPI routers)
- Services (business logic)
- Repository (DB access)
- Models (SQLAlchemy)
- Schemas (Pydantic)
- Core (config, security)
- Tasks (async/cron)

All orchestrated in a clean, maintainable structure.

---

## 12. Testing

**Required tests:**

- [x] availability logic tests
- [x] booking creation tests
- [x] role/permission tests
- [x] check-in/out tests
- [x] service layer unit tests
- [x] integration tests with test DB
- [x] payment processing tests
- [x] cancellation & refund tests
- [x] no-show penalty tests
- [x] invoice generation tests

---

## 13. Deliverables

- [x] Backend codebase (FastAPI, SQLAlchemy, JWT, Alembic)
- [x] Frontend (admin panel & dashboard with dark theme)
- [ ] Database schema diagram
- [ ] Architecture diagram
- [x] PRD & README (comprehensive documentation)
- [x] Deployment (Docker Compose with PostgreSQL)
- [ ] Screenshots for diploma defense
- [ ] Final report documentation

---

## 14. Success Criteria

The system is considered "complete" if:

- [x] Booking system fully works with no double bookings
- [x] End-to-end check-in/out works
- [x] Pricing engine functional (room rates, total calculation)
- [ ] Housekeeping workflow works
- [x] UI panels functional (rooms, guests, bookings, payments, reports, admin)
- [x] At least 10 tests pass (15+ comprehensive tests)
- [x] PDF documents generate correctly (invoices)
- [x] Clean and stable architecture (modular services, API, schemas)
- [x] Deployed or runnable with one command (docker-compose up)