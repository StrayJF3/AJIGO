# IMPORTA LAS DEPENDENCIAS DE SEGURIDAD Y HASHING
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

# CARGA EL SECRETO Y ALGORITMO DE LAS VARIABLES DE ENTORNO
SECRET_KEY = os.getenv("JWT_SECRET", "AJIGOSecretKeySuperSecure2026!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# VERIFICA SI UNA CONTRASENA COINCIDE CON SU HASH CON BCRYPT
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # CONVIERTE LA CONTRASENA PLANA Y EL HASH A BYTES, RECORTANDO A 72 BYTES MAXIMO
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        # RETORNA FALSO EN CASO DE CUALQUIER FALLA DE VERIFICACION
        return False

# GENERA UN HASH SEGURO BCRYPT PARA LA CONTRASENA
def get_password_hash(password: str) -> str:
    # CONVIERTE A BYTES Y RECORTA A 72 BYTES PARA EVITAR LIMITACIONES
    pwd_bytes = password.encode('utf-8')[:72]
    # GENERA LA SEMILLA Y GENERA EL HASH
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

# CREA UN TOKEN DE ACCESO JWT FIRMADO
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
