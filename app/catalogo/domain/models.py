# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import Optional
from sqlmodel import SQLModel, Field

# DEFINE EL MODELO DE RESTAURANTES DE LA BASE DE DATOS
class Restaurante(SQLModel, table=True):
    __tablename__ = "RESTAURANTES"

    RestauranteID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    NombreRestaurante: str

    LogoURL: Optional[str] = None

    Descripcion: Optional[str] = None

    Activo: bool = True

    Slug: str

    Tagline: Optional[str] = None

    BannerColor: Optional[str] = None

    BadgeText: Optional[str] = None

    UseImage: Optional[bool] = False

# DEFINE EL MODELO DE PRODUCTOS DE LA BASE DE DATOS
class Producto(SQLModel, table=True):
    __tablename__ = "PRODUCTOS"

    ProductoID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    SucursalID: int

    CategoriaID: int

    NombreProducto: str

    Descripcion: Optional[str] = None

    ImagenURL: Optional[str] = None

    Precio: float

    Stock: int

    Activo: bool = True

    Tag: Optional[str] = None

    BadgeText: Optional[str] = None

    SpicyLevel: Optional[int] = 0

    Sizes: Optional[str] = None  # REPRESENTACION JSON EN TEXTO DE LOS TAMANOS

    Extras: Optional[str] = None  # REPRESENTACION JSON EN TEXTO DE LOS EXTRAS
