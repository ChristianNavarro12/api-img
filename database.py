# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from config import DATABASE_URL

# Crear el motor de conexión
engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base (esto se ejecuta cuando se crea la base de datos)
def create_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
