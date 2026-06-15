# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import List, Optional
from sqlmodel import Session, select
from domain.models import Restaurante, Producto

# OBTIENE TODOS LOS RESTAURANTES ACTIVOS DE LA BASE DE DATOS
def get_all_restaurants(session: Session) -> List[Restaurante]:
    statement = select(Restaurante).where(Restaurante.Activo == True)
    return session.exec(statement).all()

# CONSULTA UN RESTAURANTE ESPECIFICO FILTRADO POR SU SLUG
def get_restaurant_by_slug(session: Session, slug: str) -> Optional[Restaurante]:
    statement = select(Restaurante).where(Restaurante.Slug == slug)
    return session.exec(statement).first()

# ACTUALIZA LOS VALORES DE UN RESTAURANTE EXISTENTE
def update_restaurant_data(session: Session, restaurant: Restaurante) -> Restaurante:
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant

# OBTIENE TODOS LOS PRODUCTOS ACTIVOS DE LA BASE DE DATOS
def get_all_products(session: Session) -> List[Producto]:
    statement = select(Producto).where(Producto.Activo == True)
    return session.exec(statement).all()

# BUSCA UN PRODUCTO POR SU IDENTIFICADOR NUMERICO
def get_product_by_id(session: Session, product_id: int) -> Optional[Producto]:
    return session.get(Producto, product_id)

# GUARDA UN NUEVO PRODUCTO EN EL INVENTARIO DE LA SUCURSAL
def save_new_product(session: Session, product: Producto) -> Producto:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# ELIMINA LOGICAMENTE O DE FORMA FISICA UN PRODUCTO SEGUN LA PETICION
def delete_product_data(session: Session, product: Producto) -> None:
    session.delete(product)
    session.commit()
