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
