# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import List, Dict, Optional
from sqlmodel import SQLModel

# ESQUEMA DE ENTRADA PARA LA CREACION DE UN NUEVO PEDIDO
class OrderCreateRequest(SQLModel):
    userEmail: str
    items: List[Dict]
    subtotal: float
    deliveryFee: float
    discount: float
    tax: float
    total: float
    coupon: Optional[str] = None
    deliveryDetails: Dict
    restaurant: str
    transferReceipt: Optional[str] = None


# ESQUEMA DE ENTRADA PARA ACTUALIZAR EL ESTADO DE UN PEDIDO
class StatusUpdateRequest(SQLModel):
    status: int

# ESQUEMA DE ENTRADA PARA ASIGNAR UN REPARTIDOR A UN PEDIDO
class DriverAssignRequest(SQLModel):
    driverName: str
    driverEmail: str


# ESQUEMA DE ENTRADA PARA PERSISTIR EL CARRITO
class CartItemSchema(SQLModel):
    baseId: str
    name: str
    price: float
    quantity: int
    size: str
    extras: List[str]
    notes: str

class CartSaveRequest(SQLModel):
    email: str
    items: List[CartItemSchema]

