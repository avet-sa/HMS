from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_in.password = hash_password(user_in.password)
    return UserService.create_user(db, user_in)

@router.post("/login")
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, user_in.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not pwd_context.verify(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"detail": "Login successful"}
