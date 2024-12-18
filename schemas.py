# schemas.py
from pydantic import BaseModel
from typing import Optional

class ProductoCreate(BaseModel):
    descripcion: str
    precio: str
    img: Optional[str] = None  # Opcional al crear el producto

class Producto(BaseModel):
    id: int
    descripcion: str
    precio: str
    img: Optional[str] = None  # URL de la imagen

    class Config:
        orm_mode = True
