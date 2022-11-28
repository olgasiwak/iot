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

@app.get("/client/{id}", response_model=List[schemas.Client])
def read_client(id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return [client]

