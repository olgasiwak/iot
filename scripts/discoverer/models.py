from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Devices(Base):
    __tabelname__ = "devices"
    udid = Column(String, primary_key=True)
    mac = Column(String, nullable=False, unique=True)
    longitude = Column(String, nullable=False)
    latitude = Column(String, nullable=False)
    version_id = Column(Integer, ForeignKey("versions.hw_type"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    version = relationship("Versions", back_populates="devices")
    group = relationship("Groups", back_populates="devices")


class Versions(Base):
    __tabelname__ = "versions"
    hw_type = Column(String, primary_key=True)
    description = Column(String)


class Groups(Base):
    __tabelname__ = "groups"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)
    description = Column(String)
    configuration = Column(JSON)
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Clients", back_populates="groups")


class Clients(Base):
    __tabelname__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
