# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import Optional
from sqlmodel import SQLModel

# DEFINE EL ESQUEMA DE ENTRADA PARA ACTUALIZAR UN PERFIL DE USUARIO
class UserUpdateRequest(SQLModel):
    phone: Optional[str] = None
    points: Optional[int] = None
    driverStatus: Optional[str] = None
    vehicleType: Optional[str] = None
    licensePlate: Optional[str] = None
