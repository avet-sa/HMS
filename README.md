# Hotel Management System (Python) – Full Diploma Project Blueprint

## 1. Recommended Form: Web App vs Desktop App
**Choose: Web App**
- Easier to build
- Accessible on multiple devices
- Better for diplomas (architecture + API = more points)
- Cleaner separation of frontend & backend
- Demonstrates modern development practices

Desktop apps (Tkinter, PyQt) look outdated and are harder to structure.

---

# 2. Full Tech Stack (Python-Based HMS)
## Frontend
- **HTML + TailwindCSS + Vanilla JS** (simple & clean)
- Optional: **React + Vite** (if you want more modern UI)

## Backend
- **Python + FastAPI** (clean, fast, ideal for CRUD systems)

## Database
- **PostgreSQL** (production)
- **SQLite** (development)

## ORM
- **SQLAlchemy + Alembic** (migrations)

## Authentication
- **JWT (python-jose)**
- **Password hashing** (PassLib)

## Deployment
- **Docker** (optional)

---

# 3. Full Project Architecture (Folders & Files)
```
hotel-management-system/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── bookings.py
│   │   │   ├── rooms.py
│   │   │   ├── guests.py
│   │   │   └── auth.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── schemas/
│   │   │   ├── booking.py
│   │   │   ├── room.py
│   │   │   ├── guest.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── booking_service.py
│   │   │   └── room_service.py
│   │   └── utils/
│   │       └── availability.py
│   └── alembic/
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       └── app.js
│
└── docker-compose.yml
```

---

# 4. Database Schema
## Tables:
### **rooms**
| Field | Type | Description |
|-------|------|-------------|
| id | int (PK) | Room ID |
| number | text | Room number |
| type | text | single/double/suite |
| price | float | Price per night |
| status | text | available/booked/maintenance |

### **guests**
| Field | Type |
|-------|------|
| id | int (PK) |
| fullname | text |
| phone | text |
| email | text |

### **bookings**
| Field | Type |
|-------|------|
| id | int (PK) |
| room_id | FK -> rooms.id |
| guest_id | FK -> guests.id |
| check_in | date |
| check_out | date |
| status | text (booked/checked_in/checked_out/cancelled) |

### **users (staff)**
| Field | Type |
|-------|------|
| id | int (PK) |
| username | text |
| password_hash | text |
| role | text (admin/staff) |

---

# 5. API Endpoints List
## **Auth**
- POST /auth/login

## **Rooms**
- GET /rooms
- POST /rooms
- GET /rooms/{id}
- PUT /rooms/{id}
- DELETE /rooms/{id}

## **Guests**
- GET /guests
- POST /guests
- GET /guests/{id}

## **Bookings**
- GET /bookings
- POST /bookings
- GET /bookings/{id}
- PUT /bookings/{id} (modify dates)
- POST /bookings/{id}/checkin
- POST /bookings/{id}/checkout
- POST /bookings/{id}/cancel

---

# 6. Minimal Backend Boilerplate (FastAPI)
```python
# main.py
from fastapi import FastAPI
from app.api import rooms, bookings, guests, auth

app = FastAPI(title="Hotel Management System")

app.include_router(auth.router)
ap include_router(rooms.router)
ap.include_router(guests.router)
ap.include_router(bookings.router)
```

---
```python
# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .session import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    number = Column(String)
    type = Column(String)
    price = Column(Float)
    status = Column(String, default="available")

class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    phone = Column(String)
    email = Column(String)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_id = Column(Integer, ForeignKey("guests.id"))
    check_in = Column(Date)
    check_out = Column(Date)
    status = Column(String, default="booked")
```

---
```python
# booking_service.py
from datetime import date
from sqlalchemy.orm import Session
from app.db.models import Booking, Room

def is_room_available(db: Session, room_id: int, start: date, end: date):
    overlap = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.check_in < end,
        Booking.check_out > start,
        Booking.status != "cancelled"
    ).first()
    return overlap is None
```

---

# 7. Logic Flow (Booking, Check-In, Check-Out)
## **Booking Flow**
1. User selects dates & room
2. System checks availability (`is_room_available`)
3. If available → create booking
4. Room status remains "available" until check-in

## **Check-In Flow**
1. Staff selects booking
2. System verifies today >= check_in
3. Booking.status = "checked_in"
4. Room.status = "booked"

## **Check-Out Flow**
1. Staff confirms checkout
2. Booking.status = "checked_out"
3. Room.status = "available"

---

# 8. What to Write in Diploma Explanation Section
## **1. Problem Definition**
Hotels need structured systems to manage rooms, bookings, guests, and daily operations.
Your HMS provides:
- Automation
- Accuracy
- Reduced human error
- Efficient workflow

## **2. Why a Web App?**
- Works on any device
- Centralized data
- Multi-user staff access
- Modern & maintainable structure

## **3. Technology Justification**
- **Python** → simple, clear logic, perfect for CRUD systems
- **FastAPI** → high performance, automatic docs, modern API design
- **PostgreSQL** → stable, relational, safe for financial data
- **SQLAlchemy** → scalable ORM
- **JWT** → secure authentication

## **4. System Architecture**
Explain:
- API layer
- Service layer
- DB layer
- Frontend consuming backend

## **5. Data Integrity & Constraints**
- Foreign keys (room → booking → guest)
- Prevent overlapping bookings
- Room status transitions

## **6. Limitations and Future Work**
- Add payment system
- Add analytics
- Add mobile app
- Add staff roles

---

# Final Note
This .md file is a complete blueprint. It contains everything needed for a real, defensible diploma project.

