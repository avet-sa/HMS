from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api import rooms, guests, bookings, auth

app = FastAPI(
    title="Hotel Management System",
    description="Backend API for a full-featured hotel management system",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
app.include_router(guests.router, prefix="/guests", tags=["Guests"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Hotel Management System API"}
