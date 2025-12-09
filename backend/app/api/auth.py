from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..db.session import get_db
from ..schemas.user import UserCreate, UserResponse
from ..services.user_service import UserService
from ..core import security
from ..utils.audit import log_login
from ..dependencies.security import get_current_user
from ..db.models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # UserService.create_user will hash the password via security helpers
    return UserService.create_user(db, user_in)


@router.post("/token")
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = UserService.get_user_by_username(db, form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        # Log failed login attempt if user exists
        if user:
            log_login(db, user, request, success=False)
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Log successful login
    log_login(db, user, request, success=True)
    
    access_token_expires = timedelta(minutes=int(security.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = security.create_access_token(subject=user.username, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
