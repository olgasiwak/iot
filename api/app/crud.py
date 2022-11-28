from sqlalchemy.orm import Session

from . import models, schemas


def get_client(db: Session, id: int):
    return db.query(models.Clients).filter(models.Clients.id == id).first()
