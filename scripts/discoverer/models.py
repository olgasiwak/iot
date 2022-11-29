from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


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

    def __repr__(self):
        return "<Device(udid='%s', mac='%s', ...)>" % (self.udid, self.mac)


class Versions(Base):
    __tablename__ = "versions"
    id = Column(String, primary_key=True)
    hw_type = Column(String)
    description = Column(String)

    devices = relationship("Devices", back_populates="version")

    def __repr__(self):
        return "<Versions(hw_type='%s', ...)>" % (self.hw_type)


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)
    description = Column(String)
    configuration = Column(JSON)
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Clients", back_populates="groups")
    devices = relationship("Devices", back_populates="group")

    def __repr__(self):
        return "<Groups(client_id='%s', configuration='%s'...)>" \
                % (self.client_id, self.configuration)


class Clients(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)

    groups = relationship("Groups", back_populates="client")

    def __repr__(self):
        return "<Clients(name='%s', ...)>" % (self.name)
