# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255), nullable=False)
    precio = Column(String(20), nullable=True)
    img = Column(String(255), nullable=True)  # Para la URL de la imagen
