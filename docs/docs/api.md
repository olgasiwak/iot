# API

- [API](#api)
  * [Opis](#opis)
  * [Endpointy](#endpointy)
    + [GET `/client/{id}/`](#get---client--id---)
    + [GET `/clients/`](#get---clients--)
    + [GET `/group/{id}/`](#get---group--id---)
    + [PUT `/group/{id}/`](#put---group--id---)
    + [GET `/groups/`](#get---groups--)
    + [GET `/version/{id}/`](#get---version--id---)
    + [GET `/versions/`](#get---versions--)
    + [GET `/device/{id}/`](#get---device--id---)
    + [GET `/devices/`](#get---devices--)
    + [Przykładowe polecenia CURL do API](#przyk-adowe-polecenia-curl-do-api)
      - [Przykładowy GET](#przyk-adowy-get)
      - [Przykładowy PUT](#przyk-adowy-put)
  * [Kod, który tworzy API:](#kod--kt-ry-tworzy-api-)
    + [`database.py` - połączenie do Asset DB](#-databasepy----po--czenie-do-asset-db)
    + [`models.py` - modele obiektów w bazie](#-modelspy----modele-obiekt-w-w-bazie)
    + [`schemas.py` - schematy interakcji z obiektami](#-schemaspy----schematy-interakcji-z-obiektami)
    + [`crud.py` - definicja operacji CRUD-owych](#-crudpy----definicja-operacji-crud-owych)
    + [`main.py` - definicja endpointów i uruchomienie API](#-mainpy----definicja-endpoint-w-i-uruchomienie-api)
  * [Uruchomienie API](#uruchomienie-api)

## Opis
API zostało przygotowane w celu łatwego dostępu do Asset DB - do czytania wartości w bazie danych i modyfikacji wartości rozświetlenia.

Interaktywna dokumentacja uruchomiona została pod adresem: [Interaktywna dokumentacja swaggerUI](http://45.56.71.54:8888/docs#/)

## Endpointy

### GET `/client/{id}/`
opis: wyświetlenie pojedynczego klienta

parametry: id: int

### GET `/clients/`
opis: wyświetlenie wszystkich klientów

### GET `/group/{id}/`
opis: wyświetlanie pojedynczej grupy

parametry: id: int

### PUT `/group/{id}/`
opis: aktualizacja wartości rozjaśnienia dla pojedynczej grupy

parametry: id: int; upper_threshold: float

### GET `/groups/`
opis: wyświetlanie wszystkich grup

### GET `/version/{id}/`
opis: wyświetlanie pojedynczej wersji

parametry: id: int

### GET `/versions/`
opis: wyświetlanie wszystkich wersji

### GET `/device/{id}/`
opis: wyświetlanie pojedynczego urządzenia

parametry: id: int

### GET `/devices/`
opis: wyświetlanie wszystkich urządzeń

### Przykładowe polecenia CURL do API
Poniżej przedstawiono przykładowe polecenia, którymi możemy prowadzić interakcje z API.
#### Przykładowy GET
```
curl -X 'GET' \
  'http://45.56.71.54:8888/group/1/' \
  -H 'accept: application/json'
```
Odpowiedź:
```
{
  "quantity": 5,
  "description": "opis",
  "configuration": {
    "lower_threshold": 0.2,
    "upper_threshold": 0.75
  },
  "client_id": 1,
  "id": 1
}
```

#### Przykładowy PUT
```
curl -X 'PUT' \
  'http://45.56.71.54:8888/group/1/?upper_threshold=0.75' \
  -H 'accept: application/json'
```
Odpowiedź:
```
{
  "quantity": 5,
  "description": "opis",
  "configuration": {
    "lower_threshold": 0.2,
    "upper_threshold": 0.75
  },
  "client_id": 1,
  "id": 1
}
```

## Kod, który tworzy API:
Kod został napisany w oparciu o dokumentację Python fastAPI: [Dokumentacja fastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/)
### `database.py` - połączenie do Asset DB
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Baremetal
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@127.0.0.1/main"
# Docker container
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@172.17.0.2/main"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```
### `models.py` - modele obiektów w bazie
```python
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .database import Base


class Devices(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True)
    udid = Column(String, nullable=False, unique=True)
    mac = Column(String, nullable=False, unique=True)
    longitude = Column(String, nullable=False)
    latitude = Column(String, nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    version = relationship("Versions", back_populates="devices")
    group = relationship("Groups", back_populates="devices")


class Versions(Base):
    __tablename__ = "versions"
    id = Column(String, primary_key=True)
    hw_type = Column(String)
    description = Column(String)

    devices = relationship("Devices", back_populates="version")


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)
    description = Column(String)
    configuration = Column(JSON)
    client_id = Column(Integer, ForeignKey("clients.id"))

    #client = relationship("Clients", back_populates="groups")
    devices = relationship("Devices", back_populates="group")


class Clients(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    groups = relationship("Groups", back_populates="client")
```

### `schemas.py` - schematy interakcji z obiektami
```python
from typing import List, Union

from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    description: str


class Client(ClientBase):
    id: int

    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    quantity: int
    description: str
    configuration: dict
    client_id: int

class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True

class VersionBase(BaseModel):
    hw_type: str
    description: str

class Version(VersionBase):
    id: int

    class Config:
        orm_mode = True

class DeviceBase(BaseModel):
    udid: str
    mac: str
    longitude: str
    latitude: str
    version_id: int
    group_id: int

class Device(DeviceBase):
    id: int

    class Config:
        orm_mode = True
```

### `crud.py` - definicja operacji CRUD-owych
```python
from sqlalchemy.orm import Session

from . import models, schemas


def get_client(db: Session, id: int):
    return db.query(models.Clients).filter(models.Clients.id == id).first()

def get_clients(db: Session):
     return db.query(models.Clients).all()

def get_group(db: Session, id: int):
    return db.query(models.Groups).filter(models.Groups.id == id).first()

def update_group(db: Session, group: models.Groups, id: int, upper_threshold: float):
    db_group = db.query(models.Groups).filter(models.Groups.id == id).first()
    db_group.configuration = {"lower_threshold":0.2,"upper_threshold":upper_threshold}
    db.commit()
    db.refresh(db_group)
    return db_group

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
```

### `main.py` - definicja endpointów i uruchomienie API
```python
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
    )


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

@app.put("/group/{id}/", response_model=schemas.Group)
def update_group(id: int, upper_threshold: float, db:Session = Depends(get_db)):
    group = crud.get_group(db, id)
    if group is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return crud.update_group(db=db, group=group, id=id, upper_threshold=upper_threshold)

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
```

## Uruchomienie API
Do uruchomienia API potrzebne jest zbudowanie i uruchomienie kontenera Docker:

Dockerfile:
```
FROM python:3.9
WORKDIR /api/
COPY ./requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt
COPY ./app /api/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]
```

requirements.txt:
```
fastapi>=0.68.0,<0.69.0
pydantic>=1.8.0,<2.0.0
uvicorn>=0.15.0,<0.16.0
sqlalchemy
psycopg2-binary
```

Komendy uruchamiające API :
```
cd PATH_TO_DOCKERFILE_LOCATION
docker build -t api_image .
docker run -d --name uvicorn_api -p 8888:8888 api_image
```

