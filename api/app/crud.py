from sqlalchemy.orm import Session

from . import models, schemas


def get_client(db: Session, id: int):
    return db.query(models.Clients).filter(models.Clients.id == id).first()

def get_clients(db: Session):
     return db.query(models.Clients).all()

def get_group(db: Session, id: int):
    return db.query(models.Groups).filter(models.Groups.id == id).first()

def get_groups(db: Session):
     return db.query(models.Groups).all()

def get_version(db: Session, id: int):
    return db.query(models.Versions).filter(models.Versions.id == id).first()

def get_versions(db: Session):
     return db.query(models.Versions).all()

def get_device(db: Session, id: int):
    return db.query(models.Devices).filter(models.Devices.id == id).first()

def get_devices(db: Session):
     return db.query(models.Devices).all()
