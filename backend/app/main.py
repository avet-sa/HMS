import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import os

# Import routers
from backend.app.api import reports, rooms, guests, bookings, auth, room_types, users, payments, invoices

# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hotel Management System",
    description="Backend API for a full-featured hotel management system",
    version="1.0.0",
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Too many requests."},
    )

# Enable CORS for frontend. Use environment variable in production to restrict allowed origins.
allowed_origins = os.getenv("FRONTEND_ALLOWED_ORIGINS")
if allowed_origins:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    origins = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(room_types.router, prefix="/room-types", tags=["Room Types"])
app.include_router(guests.router, prefix="/guests", tags=["Guests"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(invoices.router, tags=["Invoices"])
app.include_router(reports.router, tags=["Reports"])

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


# Root endpoint
@app.get("/")
# @limiter.limit("100/minute")
def root():
    return {"message": "Welcome to the Hotel Management System API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
