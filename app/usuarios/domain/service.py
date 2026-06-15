# IMPORTA LAS TIPACIONES REQUERIDAS DE LA APLICACION
from typing import Optional
from sqlmodel import Session
from domain.models import Usuario
from infrastructure.repository import get_user_by_email, update_user

# MODIFICA LOS DETALLES DEL USUARIO Y GESTIONA LAS TRANSICIONES DE ROLES Y PUNTOS
def update_user_profile(session: Session, email: str, data: dict) -> Usuario:
    # RECUPERA EL USUARIO ASOCIADO AL CORREO ELECTRONICO
    user = get_user_by_email(session, email)
    if not user:
        raise ValueError("Usuario no encontrado.")

    # ACTUALIZA EL TELEFONO SI ES SUMINISTRADO
    if "phone" in data:
        user.Telefono = data["phone"]

    # ACTUALIZA LOS PUNTOS ACUMULADOS SI SE MODIFICAN
    if "points" in data:
        user.PuntosAJIGO = data["points"]

    # ACTUALIZA EL ESTADO DE REPARTIDOR Y CAMBIA EL ROLID SI SE APRUEBA
    if "driverStatus" in data:
        user.DriverStatus = data["driverStatus"]
        if data["driverStatus"] == "approved":
            user.RolID = 2  # CAMBIA EL ROL AL DE REPARTIDOR

    # ACTUALIZA EL TIPO DE VEHICULO Y MATRICULA SI CORRESPONDE
    if "vehicleType" in data:
        user.VehicleType = data["vehicleType"]
    if "licensePlate" in data:
        user.LicensePlate = data["licensePlate"]

    # GUARDA LOS CAMBIOS EN EL REPOSITORIO
    return update_user(session, user)
