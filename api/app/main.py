from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/client/{id}/", response_model=schemas.Client)
def read_client_by_id(id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, id)
    if client is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return client

@app.get("/clients/", response_model=List[schemas.Client])
def read_clients(db: Session = Depends(get_db)):
    clients = crud.get_clients(db)
    return clients

@app.get("/group/{id}/", response_model=schemas.Group)
def read_group_by_id(id: int, db:Session = Depends(get_db)):
    group = crud.get_group(db, id)
    if group is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return group

@app.get("/groups/", response_model=List[schemas.Group])
def read_groups(db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

@app.get("/version/{id}/", response_model=schemas.Version)
def read_version_by_id(id: int, db:Session = Depends(get_db)):
    version = crud.get_version(db, id)
    if version is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return version

@app.get("/versions/", response_model=List[schemas.Version])
def read_versions(db: Session = Depends(get_db)):
    versions = crud.get_versions(db)
    return versions

@app.get("/device/{id}/", response_model=schemas.Device)
def read_device_by_id(id: int, db:Session = Depends(get_db)):
    device = crud.get_device(db, id)
    if device is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return device

@app.get("/devices/", response_model=List[schemas.Device])
def read_devices(db: Session = Depends(get_db)):
    devices = crud.get_devices(db)
    return devices

