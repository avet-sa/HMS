from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import hashlib

from ..db.session import get_db
from ..schemas.user import UserCreate, UserResponse
from ..services.user_service import UserService

router = APIRouter()

def hash_password(password: str) -> str:
    """Hash password with bcrypt, handling 72-byte limit by pre-hashing long passwords."""
    # Truncate/pre-hash if longer than 72 bytes to avoid bcrypt limits
    if len(password.encode()) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    # Apply same pre-hash logic if password is long
    if len(plain.encode()) > 72:
        plain = hashlib.sha256(plain.encode()).hexdigest()
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_in.password = hash_password(user_in.password)
    return UserService.create_user(db, user_in)

@router.post("/login")
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, user_in.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"detail": "Login successful", "username": user.username}
