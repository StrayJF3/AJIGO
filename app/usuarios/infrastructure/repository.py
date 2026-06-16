# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL
from typing import Optional
from sqlmodel import Session, select
from domain.models import Usuario

# CONSULTA UN USUARIO POR SU DIRECCION DE CORREO ELECTRONICO
def get_user_by_email(session: Session, email: str) -> Optional[Usuario]:
    statement = select(Usuario).where(Usuario.Email == email)
    results = session.exec(statement)
    return results.first()

# ACTUALIZA O GUARDA EL REGISTRO DE UN USUARIO EN LA BASE DE DATOS
def update_user(session: Session, user: Usuario) -> Usuario:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# OBTIENE TODOS LOS USUARIOS DE LA BASE DE DATOS
def get_all_users(session: Session) -> list[Usuario]:
    statement = select(Usuario)
    return session.exec(statement).all()

# BUSCA UN USUARIO POR SU ID ENTERO EN LA BASE DE DATOS
def get_user_by_id(session: Session, user_id: int) -> Optional[Usuario]:
    return session.get(Usuario, user_id)
