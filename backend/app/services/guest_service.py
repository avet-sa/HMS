from sqlalchemy.orm import Session
from typing import Optional, List

from ..db import models
from ..schemas.guest import GuestCreate, GuestUpdate

class GuestService:

    @staticmethod
    def create_guest(db: Session, guest_in: GuestCreate) -> models.Guest:
        guest = models.Guest(**guest_in.model_dump())
        db.add(guest)
        db.commit()
        db.refresh(guest)
        return guest

    @staticmethod
    def get_guest(db: Session, guest_id: int) -> Optional[models.Guest]:
        return db.query(models.Guest).filter(models.Guest.id == guest_id).first()

    @staticmethod
    def list_guests(db: Session) -> List[models.Guest]:
        return db.query(models.Guest).all()

    @staticmethod
    def update_guest(db: Session, guest_id: int, guest_in: GuestUpdate) -> Optional[models.Guest]:
        guest = GuestService.get_guest(db, guest_id)
        if not guest:
            return None

        for field, value in guest_in.model_dump(exclude_unset=True).items():
            setattr(guest, field, value)

        db.commit()
        db.refresh(guest)
        return guest

    @staticmethod
    def delete_guest(db: Session, guest_id: int) -> bool:
        guest = GuestService.get_guest(db, guest_id)
        if not guest:
            return False
        db.delete(guest)
        db.commit()
        return True
