# IMPORTA LAS TIPACIONES REQUERIDAS
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

# DEFINE LA ENTIDAD DE USUARIO DE LA BASE DE DATOS
class Usuario(SQLModel, table=True):
    __tablename__ = "USUARIOS"

    UsuarioID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    RolID: int

    NombreUsuario: Optional[str] = None

    Email: str

    Contrasena: str

    Telefono: Optional[str] = None

    Activo: bool = True

    PuntosAJIGO: Optional[int] = 0

    FechaRegistro: datetime = Field(default_factory=datetime.now)

    DriverStatus: Optional[str] = "none"

    VehicleType: Optional[str] = None

    LicensePlate: Optional[str] = None