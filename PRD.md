# Hotel Management System — Product Requirements Document (PRD)

**Version:** 1.0  
**Author:** Avet  
**Date:** 2025  
**Status:** Draft

---

## 15. Database Schema Considerations

### 15.1. Key Tables

- [ ] **users** - staff and customer accounts
- [ ] **rooms** - room inventory
- [ ] **room_types** - standard, deluxe, suite, etc.
- [ ] **bookings** - reservation records
- [ ] **payments** - payment transactions
- [ ] **pricing_rules** - seasonal and dynamic pricing
- [ ] **housekeeping_tasks** - cleaning assignments
- [ ] **audit_logs** - track all critical operations

### 15.2. Important Indexes

- [ ] bookings(check_in_date, check_out_date, status)
- [ ] rooms(status, room_type_id)
- [ ] payments(booking_id, status)
- [ ] audit_logs(timestamp, user_id)

### 15.3. Data Integrity

- [ ] Foreign key constraints
- [ ] Check constraints for dates (check_out > check_in)
- [ ] Unique constraints on room numbers
- [ ] Soft deletes for bookings and payments

---

## 16. API Design Principles

### 16.1. RESTful Conventions

- [ ] Use proper HTTP verbs (GET, POST, PUT, PATCH, DELETE)
- [ ] Consistent naming: `/api/v1/bookings`, `/api/v1/rooms`
- [ ] Proper status codes (200, 201, 400, 401, 403, 404, 500)
- [ ] Pagination for list endpoints
- [ ] Filtering and sorting support

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

- [ ] Environment variables for secrets
- [ ] Database migrations with Alembic
- [ ] Health check endpoints
- [ ] Graceful shutdown handling
- [ ] Rate limiting
- [ ] CORS configuration

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

- [ ] Room management
- [ ] Booking system with availability engine
- [ ] User authentication & role-based permissions
- [ ] Check-in/out workflows
- [ ] Payment simulation
- [ ] Housekeeping workflow
- [ ] Reporting (dashboard endpoints)
- [ ] Background tasks & scheduled tasks
- [ ] PDF generation (invoices / confirmations)
- [ ] Monitoring & logging
- [ ] Minimal but functional frontend UI in dark theme
- [ ] Email notifications (simulated or SMTP)
- [ ] Audit logging for critical operations

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

- [ ] JWT-based login
- [ ] Token contains user role
- [ ] Role-based route protection
- [ ] Password hashing (bcrypt)

### 4.2. Room Management

**Features:**

- [ ] Room CRUD
- [ ] Room types
- [ ] Room status (AVAILABLE, OCCUPIED, CLEANING, OUT_OF_SERVICE)
- [ ] Facilities & metadata

### 4.3. Booking System

The heart of the application.

#### 4.3.1. Availability Engine

**Inputs:**

- [ ] check-in date
- [ ] check-out date
- [ ] number of guests
- [ ] room type (optional)

**Output:**

- [ ] available rooms list
- [ ] price breakdown
- [ ] alerts (conflicts, high occupancy)

**Business Rules:**

- [ ] Minimum 1 night stay
- [ ] Maximum advance booking: 365 days
- [ ] Check-in time: 14:00, Check-out time: 11:00
- [ ] Same-day booking allowed if before check-in time
- [ ] Handle edge cases: leap years, timezone considerations

#### 4.3.2. Overbooking Prevention

- [ ] Database-level transactional locking
- [ ] Prevent double booking
- [ ] Atomic room assignment

#### 4.3.3. Booking States

- [ ] PENDING_PAYMENT (new reservation, awaiting payment)
- [ ] CONFIRMED (payment received)
- [ ] CHECKED_IN
- [ ] CHECKED_OUT
- [ ] CANCELLED
- [ ] NO_SHOW

**State Transitions:**

- [ ] PENDING_PAYMENT → CONFIRMED (on payment)
- [ ] PENDING_PAYMENT → CANCELLED (timeout or manual)
- [ ] CONFIRMED → CHECKED_IN (on arrival)
- [ ] CHECKED_IN → CHECKED_OUT (on departure)
- [ ] CONFIRMED → NO_SHOW (if guest doesn't arrive)

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

- [ ] Calculate extras (if any)
- [ ] Produce invoice PDF
- [ ] Set room → CLEANING
- [ ] Free room after cleaning

### 4.6. Payments (Mock)

**Types:**

- [ ] Card (mock API)
- [ ] Pay at desk
- [ ] Refund simulation

**Flows:**

- [ ] payment pending
- [ ] payment successful
- [ ] payment failed
- [ ] refund issued

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

- [ ] Occupancy rate
- [ ] Revenue charts
- [ ] Housekeeping stats
- [ ] Upcoming arrivals & departures

### 6.2. Front Office Dashboard

- [ ] Today's check-ins
- [ ] Today's check-outs
- [ ] Rooms needing cleaning

---

## 7. PDF Generation

Using ReportLab or HTML-to-PDF.

**Documents:**

- [ ] Booking confirmation
- [ ] Registration card
- [ ] Invoice
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

- [ ] Login page
- [ ] Dashboard (role-based)
- [ ] Booking creation form
- [ ] Availability calendar view
- [ ] Check-in/out panel
- [ ] Housekeeping screen

**UI does NOT need to be pretty — just functional, clean, dark themed.**

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

- [ ] availability logic tests
- [ ] booking creation tests
- [ ] role/permission tests
- [ ] check-in/out tests
- [ ] service layer unit tests
- [ ] integration tests with test DB

---

## 13. Deliverables

- [ ] Backend codebase
- [ ] Frontend (admin & housekeeping panel)
- [ ] Database schema diagram
- [ ] Architecture diagram
- [ ] PRD & README
- [ ] Deployment (Docker Compose or VPS)
- [ ] Screenshots for diploma defense
- [ ] Final report documentation

---

## 14. Success Criteria

The system is considered "complete" if:

- [ ] Booking system fully works with no double bookings
- [ ] End-to-end check-in/out works
- [ ] Pricing engine functional
- [ ] Housekeeping workflow works
- [ ] UI panels functional
- [ ] At least 10 tests pass
- [ ] PDF documents generate correctly
- [ ] Clean and stable architecture
- [ ] Deployed or runnable with one command