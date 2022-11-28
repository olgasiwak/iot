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

    #groups = relationship("Groups", back_populates="client")

