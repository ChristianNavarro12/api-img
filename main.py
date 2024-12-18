# main.py
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal, create_db
from models import Producto
from schemas import ProductoCreate, Producto as ProductoSchema
from pathlib import Path
from uuid import uuid4
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Crear la base de datos al iniciar la app
create_db()

# Carpeta para guardar las imágenes
UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Servir archivos estáticos (como imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def hola_mundo():
    return {"HOLA" : "mundo"}

# Endpoint GET /productos para obtener todos los productos
@app.get("/productos", response_model=list[ProductoSchema])
def get_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos

# Endpoint GET /productos/{producto_id} para obtener un producto por su ID
@app.get("/productos/{producto_id}", response_model=ProductoSchema)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.post("/productos", response_model=ProductoSchema)
async def create_producto(
    descripcion: str = Form(...),  # Campo texto: descripcion
    precio: str = Form(...),       # Campo texto: precio
    file: UploadFile = File(None), # Campo archivo: imagen
    db: Session = Depends(get_db)
):
    # Si se recibe una imagen
    img_url = None
    if file:
        img_filename = f"{uuid4().hex}_{file.filename}"
        img_filepath = UPLOAD_DIR / img_filename
        with open(img_filepath, "wb") as buffer:
            buffer.write(await file.read())
        img_url = f"/static/images/{img_filename}"

    # Crear el producto con la imagen
    db_producto = Producto(descripcion=descripcion, precio=precio, img=img_url)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@app.put("/productos/{producto_id}", response_model=ProductoSchema)
async def update_producto(
    producto_id: int, 
    descripcion: str = Form(...),  # Campo texto: descripcion
    precio: str = Form(...),       # Campo texto: precio
    file: UploadFile = File(None), # Campo archivo: imagen
    db: Session = Depends(get_db)
):
    # Buscar el producto existente por ID
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Actualizar los campos del producto
    db_producto.descripcion = descripcion
    db_producto.precio = precio

    # Si se recibe una nueva imagen
    if file:
        # Eliminar la imagen anterior si existe
        if db_producto.img:
            img_path = Path(f"static{db_producto.img}")
            if img_path.exists():
                img_path.unlink()

        # Guardar la nueva imagen
        img_filename = f"{uuid4().hex}_{file.filename}"
        img_filepath = UPLOAD_DIR / img_filename
        with open(img_filepath, "wb") as buffer:
            buffer.write(await file.read())
        db_producto.img = f"/static/images/{img_filename}"

    # Guardar los cambios en la base de datos
    db.commit()
    db.refresh(db_producto)
    
    return db_producto

# main.py
@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Eliminar la imagen del servidor si existe
    if db_producto.img:
        img_filename = db_producto.img.split("/")[-1]
        img_filepath = UPLOAD_DIR / img_filename
        if img_filepath.exists():
            os.remove(img_filepath)

    db.delete(db_producto)
    db.commit()
    return {"detail": "Producto y su imagen eliminados"}
