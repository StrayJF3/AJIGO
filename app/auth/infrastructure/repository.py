# IMPORTA LOS MODELOS Y LA SESION DE LA BASE DE DATOS
from typing import Optional
from sqlmodel import Session, select
from domain.models import Usuario

# BUSCA UN USUARIO POR SU DIRECCION DE CORREO ELECTRONICO
def get_user_by_email(session: Session, email: str) -> Optional[Usuario]:
    statement = select(Usuario).where(Usuario.Email == email)
    results = session.exec(statement)
    return results.first()

# REGISTRA UN NUEVO USUARIO EN LA BASE DE DATOS
def create_user(session: Session, user: Usuario) -> Usuario:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# BUSCA TODOS LOS REPARTIDORES CON SOLICITUD PENDIENTE
def get_pending_drivers(session: Session) -> list[Usuario]:
    statement = select(Usuario).where(Usuario.DriverStatus == "pending")
    return session.exec(statement).all()

# BUSCA UN USUARIO POR SU IDENTIFICADOR NUMERICO
def get_user_by_id(session: Session, user_id: int) -> Optional[Usuario]:
    return session.get(Usuario, user_id)

# ACTUALIZA LOS VALORES DE UN USUARIO EXISTENTE
def update_user(session: Session, user: Usuario) -> Usuario:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
