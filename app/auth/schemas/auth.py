# IMPORTA LAS TIPACIONES REQUERIDAS DE PYDANTIC Y SQLMODEL
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr

# ESQUEMA DE ENTRADA PARA EL REGISTRO DE USUARIOS
class RegisterRequest(SQLModel):
    name: str
    email: EmailStr
    password: str
    role: str
    restaurantAdminFor: Optional[str] = None

# ESQUEMA DE ENTRADA PARA EL INICIO DE SESION
class LoginRequest(SQLModel):
    email: EmailStr
    password: str
    role: str
    restaurantAdminFor: Optional[str] = None

# ESQUEMA DE RESPUESTA DE AUTENTICACION CON EL TOKEN
class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: dict