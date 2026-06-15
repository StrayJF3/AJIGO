# IMPORTA LAS BIBLIOTECAS REQUERIDAS DE SQLMODEL
from sqlmodel import create_engine, Session

# IMPORTA LOS PARAMETROS DE CONFIGURACION GENERALES
from config import (
    DB_SERVER,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

# CONSTRUYE LA CADENA DE CONEXION COMPATIBLE CON SQL SERVER Y DRIVER 18 (CON CERTIFICADO DE CONFIANZA HABILITADO)
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

# CREA EL MOTOR DE CONEXION DE LA BASE DE DATOS
engine = create_engine(
    DATABASE_URL,
    echo=True,
    implicit_returning=False
)

# DEFINE EL PROVEEDOR DE SESIONES DE LA BASE DE DATOS PARA LA INYECCION DE DEPENDENCIAS
def get_session():
    with Session(engine) as session:
        yield session