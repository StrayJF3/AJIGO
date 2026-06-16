# IMPORTA LAS DEPENDENCIAS DE FASTAPI Y BASE DE DATOS
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from infrastructure.database import get_session
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from domain.service import register_user, login_user

# INSTANCIA EL ENRUTADOR CON SUS PROPIAS ETIQUETAS
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# RUTA PARA VERIFICAR LA SALUD DEL MICROSERVICIO
@router.get("/health")
def health():
    return {
        "status": "ok"
    }

# RUTA PARA REGISTRAR UN NUEVO USUARIO EN EL SISTEMA
@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    try:
        # REGISTRA AL USUARIO Y LO ASIGNA SEGUN SU ROL
        user = register_user(
            session=session,
            name=req.name,
            email=req.email,
            password=req.password,
            role=req.role,
            restaurant_admin_for=req.restaurantAdminFor
        )
        
        # INICIA LA SESION DE FORMA AUTOMATICA LUEGO DEL REGISTRO EXITOSO
        login_data = login_user(
            session=session,
            email=req.email,
            password=req.password,
            role=req.role
        )
        return login_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# RUTA PARA INICIAR SESION Y OBTENER LOS DETALLES DE SESION
@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, session: Session = Depends(get_session)):
    try:
        # EFECTUA LA VALIDACION DE CREDENCIALES
        login_data = login_user(
            session=session,
            email=req.email,
            password=req.password,
            role=req.role,
            restaurant_admin_for=req.restaurantAdminFor
        )
        return login_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# ENLACE DE SEGURIDAD Y JWT PARA VALIDAR AL MAESTRO
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET", "AJIGOSecretKeySuperSecure2026!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_current_master(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "master":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requiere el rol de Usuario Maestro."
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado."
        )

# ENDPOINTS DE CONTROL PARA EL MAESTRO
@router.get("/usuarios/pendientes")
def get_pending_users(session: Session = Depends(get_session), master: dict = Depends(get_current_master)):
    from infrastructure.repository import get_pending_drivers
    drivers = get_pending_drivers(session)
    return [{
        "id": d.UsuarioID,
        "name": d.NombreUsuario,
        "email": d.Email,
        "driverStatus": d.DriverStatus,
        "vehicleType": d.VehicleType,
        "licensePlate": d.LicensePlate,
        "phone": d.Telefono
    } for d in drivers]

@router.patch("/usuarios/{user_id}/aprobar")
def approve_user(user_id: int, session: Session = Depends(get_session), master: dict = Depends(get_current_master)):
    from infrastructure.repository import get_user_by_id, update_user
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.DriverStatus = "approved"
    user.RolID = 2  # Cambia rol a Repartidor
    update_user(session, user)
    return {"status": "success", "message": "Usuario aprobado con éxito."}

@router.patch("/usuarios/{user_id}/rechazar")
def reject_user(user_id: int, session: Session = Depends(get_session), master: dict = Depends(get_current_master)):
    from infrastructure.repository import get_user_by_id, update_user
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.DriverStatus = "none"  # Revierte estado a ninguno/rechazado
    update_user(session, user)
    return {"status": "success", "message": "Usuario rechazado con éxito."}