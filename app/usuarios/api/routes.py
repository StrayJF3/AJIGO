# IMPORTA LAS LIBRERIAS Y BASE DE DATOS REQUERIDAS
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, text
from infrastructure.database import get_session
from schemas.usuarios import UserUpdateRequest
from domain.service import update_user_profile
from infrastructure.repository import get_all_users, get_user_by_id

# INSTANCIA EL ENRUTADOR CON SU PREFIJO Y ETIQUETA
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# RUTA PARA VERIFICAR LA SALUD DEL SERVICIO
@router.get("/health")
def health():
    return {"status": "ok"}

# RUTA PARA ACTUALIZAR EL PERFIL DE UN USUARIO POR CORREO
@router.put("/{email}")
def update_profile(email: str, req: UserUpdateRequest, session: Session = Depends(get_session)):
    try:
        # CONVIERTE LOS DATOS DE ENTRADA EN DICCIONARIO IGNORANDO VALORES NULOS
        update_data = req.dict(exclude_unset=True)
        
        # PROCESA LA ACTUALIZACION DE LOS CAMPOS
        user = update_user_profile(session, email, update_data)
        
        # DETERMINA EL ROL DE TEXTO ACORDE AL ROLID
        rol_map = {1: "customer", 2: "driver", 3: "admin"}
        mapped_role = rol_map.get(user.RolID, "customer")
        
        # BUSCA LA SUCURSAL SI EL ROL ES ADMINISTRADOR
        restaurant_name = None
        if mapped_role == "admin":
            suc_query = text(
                "SELECT r.NombreRestaurante FROM SUCURSALES s "
                "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
                "WHERE s.UsuarioID = :uid"
            )
            suc_result = session.execute(suc_query, {"uid": user.UsuarioID}).first()
            if suc_result:
                restaurant_name = suc_result[0]
                
        # RETORNA EL FORMATO ESPERADO POR EL FRONTEND
        return {
            "name": user.NombreUsuario,
            "email": user.Email,
            "role": mapped_role,
            "points": user.PuntosAJIGO,
            "phone": user.Telefono,
            "driverStatus": user.DriverStatus,
            "vehicleType": user.VehicleType,
            "licensePlate": user.LicensePlate,
            "restaurantAdminFor": restaurant_name
        }
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

# RUTA PARA OBTENER TODOS LOS USUARIOS
@router.get("")
def get_all(session: Session = Depends(get_session)):
    try:
        users = get_all_users(session)
        rol_map = {1: "customer", 2: "driver", 3: "admin", 4: "master"}
        result = []
        for user in users:
            mapped_role = rol_map.get(user.RolID, "customer")
            result.append({
                "id": user.UsuarioID,
                "name": user.NombreUsuario,
                "email": user.Email,
                "role": mapped_role,
                "points": user.PuntosAJIGO,
                "phone": user.Telefono,
                "driverStatus": user.DriverStatus,
                "vehicleType": user.VehicleType,
                "licensePlate": user.LicensePlate
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# RUTA PARA OBTENER UN USUARIO POR ID
@router.get("/{user_id:int}")
def get_by_id(user_id: int, session: Session = Depends(get_session)):
    try:
        user = get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        rol_map = {1: "customer", 2: "driver", 3: "admin", 4: "master"}
        mapped_role = rol_map.get(user.RolID, "customer")
        return {
            "id": user.UsuarioID,
            "name": user.NombreUsuario,
            "email": user.Email,
            "role": mapped_role,
            "points": user.PuntosAJIGO,
            "phone": user.Telefono,
            "driverStatus": user.DriverStatus,
            "vehicleType": user.VehicleType,
            "licensePlate": user.LicensePlate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

