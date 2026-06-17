# IMPORTA LAS DEPENDENCIAS REQUERIDAS DE SQLMODEL
from sqlmodel import create_engine, Session

# IMPORTA LOS PARAMETROS DESDE LA CONFIGURACION
from config import (
    DB_SERVER,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

# CONSTRUYE LA CADENA DE CONEXION DE LA BASE DE DATOS DE FORMA DIRECTA
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

# INICIALIZA EL MOTOR DE BASE DE DATOS DE LA APLICACION
engine = create_engine(
    DATABASE_URL,
    echo=True,
    implicit_returning=False
)

# GENERA LAS SESIONES DE BASE DE DATOS UTILIZADAS PARA CADA SOLICITUD
def get_session():
    with Session(engine) as session:
        yield session
