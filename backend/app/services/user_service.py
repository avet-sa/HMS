from sqlalchemy.orm import Session
from typing import Optional

from ..db import models
from ..schemas.user import UserCreate, UserUpdate

class UserService:

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> models.User:
        user = models.User(
            username=user_in.username,
            password_hash=user_in.password,
            # permission_level defaults to REGULAR in the model
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[models.User]:
        user = UserService.get_user(db, user_id)
        if not user:
            return None

        for field, value in user_in.model_dump(exclude_unset=True).items():
            if field == "password":
                setattr(user, "password_hash", value)
            else:
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> Optional[models.User]:
        user = UserService.get_user(db, user_id)
        if not user:
            return None
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
