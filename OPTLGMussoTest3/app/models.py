from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

class Orden(Base):
    __tablename__ = "ordenes"
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, index=True)
