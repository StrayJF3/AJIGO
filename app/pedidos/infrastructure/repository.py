# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import Optional, List
from sqlmodel import Session, select, text
from datetime import datetime
from domain.models import Pedido, DetallePedido, Envio

# GUARDA UN REGISTRO DE PEDIDO EN LA BASE DE DATOS
def save_pedido(session: Session, pedido: Pedido) -> Pedido:
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido

# GUARDA UN DETALLE DE PEDIDO VINCULADO
def save_detalle(session: Session, detalle: DetallePedido) -> DetallePedido:
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle

# OBTIENE UN PEDIDO POR SU IDENTIFICADOR NUMERICO
def get_pedido_by_id(session: Session, pedido_id: int) -> Optional[Pedido]:
    return session.get(Pedido, pedido_id)

# OBTIENE UN ENVIO ASOCIADO A UN PEDIDO
def get_envio_by_pedido_id(session: Session, pedido_id: int) -> Optional[Envio]:
    statement = select(Envio).where(Envio.PedidoID == pedido_id)
    return session.exec(statement).first()

# GUARDA O ACTUALIZA EL REGISTRO DE ENVIO
def save_envio(session: Session, envio: Envio) -> Envio:
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio
