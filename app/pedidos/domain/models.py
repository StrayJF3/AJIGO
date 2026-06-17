# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import Optional
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Field

# AYUDANTE PARA OBTENER LA HORA LOCAL DE ECUADOR (UTC-5)
def get_ecuador_time() -> datetime:
    ecuador_tz = timezone(timedelta(hours=-5))
    return datetime.now(ecuador_tz).replace(tzinfo=None)

# DEFINE EL MODELO DE PEDIDOS DE LA BASE DE DATOS
class Pedido(SQLModel, table=True):
    __tablename__ = "PEDIDOS"
    __table_args__ = {"implicit_returning": False}

    PedidoID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    UsuarioID: int

    SucursalID: int

    DireccionUsuarioID: Optional[int] = None

    TipoEntregaID: int

    EstadoPedidoID: int

    Subtotal: float

    CostoEnvio: float

    MontoTotal: float

    FechaPedido: datetime = Field(default_factory=get_ecuador_time)

# DEFINE EL MODELO DE DETALLES DE PEDIDO DE LA BASE DE DATOS
class DetallePedido(SQLModel, table=True):
    __tablename__ = "DETALLE_PEDIDO"
    __table_args__ = {"implicit_returning": False}

    DetalleID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    PedidoID: int

    ProductoID: int

    Cantidad: int

    PrecioUnitario: float

    PrecioFinal: float

    Notas: Optional[str] = None

# DEFINE EL MODELO DE ENVIOS DE LA BASE DE DATOS
class Envio(SQLModel, table=True):
    __tablename__ = "ENVIOS"
    __table_args__ = {"implicit_returning": False}

    EnvioID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    PedidoID: int

    UsuarioID: int  # REPARTIDOR ASIGNADO

    EstadoID: int  # ESTADO DE LA LOGISTICA DE ENVIO

    FechaInicio: datetime = Field(default_factory=get_ecuador_time)

    FechaEntrega: Optional[datetime] = None


# DEFINE EL MODELO DE CARRITOS DE LA BASE DE DATOS
class Carrito(SQLModel, table=True):
    __tablename__ = "CARRITOS"
    __table_args__ = {"implicit_returning": False}

    CarritoID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    UsuarioID: int

    SucursalID: int

    FechaActualizacion: datetime = Field(default_factory=get_ecuador_time)


# DEFINE EL MODELO DE CARRITO_ITEMS DE LA BASE DE DATOS
class CarritoItem(SQLModel, table=True):
    __tablename__ = "CARRITO_ITEMS"
    __table_args__ = {"implicit_returning": False}

    ItemID: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    CarritoID: int

    ProductoID: int

    Cantidad: int

    Notas: Optional[str] = None

