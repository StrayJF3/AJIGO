# IMPORTA LA LECTURA DE VARIABLES DE ENTORNO
from dotenv import load_dotenv
import os

# CARGA EL ARCHIVO .ENV
load_dotenv()

# LEE LOS VALORES DE CONEXION DE LA BASE DE DATOS
DB_SERVER = os.getenv("DB_SERVER")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
