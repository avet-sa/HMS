from sqlalchemy.orm import Session
from ..db import models
from ..schemas.room import RoomCreate, RoomUpdate


class RoomService:

    @staticmethod
    def create_room(db: Session, data: RoomCreate) -> models.Room:
        room = models.Room(
            number=data.number,
            type=data.type,
            price=data.price,
            is_available=True
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def get_room(db: Session, room_id: int) -> models.Room | None:
        return db.query(models.Room).filter(models.Room.id == room_id).first()

    @staticmethod
    def list_rooms(db: Session):
        return db.query(models.Room).all()

    @staticmethod
    def update_room(db: Session, room_id: int, data: RoomUpdate):
        room = RoomService.get_room(db, room_id)
        if not room:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(room, field, value)

        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def delete_room(db: Session, room_id: int):
        room = RoomService.get_room(db, room_id)
        if not room:
            return None

        db.delete(room)
        db.commit()
        return True

    @staticmethod
    def mark_room_available(db: Session, room_id: int, value: bool):
        room = RoomService.get_room(db, room_id)
        if not room:
            return None

        room.is_available = value
        db.commit()
        return room
