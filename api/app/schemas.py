from typing import List, Union

from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    description: str


class Client(ClientBase):
    id: int

    class Config:
        orm_mode = True

