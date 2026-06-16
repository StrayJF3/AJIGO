# IMPORTA LAS BIBLIOTECAS REQUERIDAS Y MODELOS
from typing import Optional
from sqlmodel import Session, text
from domain.models import Usuario
from infrastructure.jwt import get_password_hash, verify_password, create_access_token
from infrastructure.repository import get_user_by_email, create_user

# GESTIONA EL REGISTRO DE UN NUEVO USUARIO Y ASIGNACION DE ROLES Y LOCALES
def register_user(session: Session, name: str, email: str, password: str, role: str, restaurant_admin_for: Optional[str] = None) -> Usuario:
    # COMPRUEBA SI EL CORREO ELECTRONICO YA HA SIDO REGISTRADO
    existing_user = get_user_by_email(session, email)
    if existing_user:
        raise ValueError("El correo electronico ya esta registrado.")

    # DETERMINA EL ROLID DE ACUERDO AL ROL DE TEXTO ENVIADO POR EL FRONTEND
    rol_id = 1  # POR DEFECTO CLIENTE
    driver_status = "none"
    
    if role == "driver":
        rol_id = 2
        driver_status = "pending"  # EN ESTADO PENDIENTE DE APROBACION AL REGISTRARSE
    elif role == "admin":
        rol_id = 3

    # CREA LA ENTIDAD DE USUARIO CON LA CONTRASENA ENCRIPTADA
    new_user = Usuario(
        NombreUsuario=name,
        Email=email,
        Contrasena=get_password_hash(password),
        RolID=rol_id,
        Activo=True,
        PuntosAJIGO=0,
        DriverStatus=driver_status
    )
    
    # GUARDA EL REGISTRO EN LA BASE DE DATOS
    saved_user = create_user(session, new_user)

    # SI ES UN ADMINISTRADOR DE LOCAL, SE ASIGNA A LA SUCURSAL CORRESPONDIENTE
    if role == "admin" and restaurant_admin_for:
        # BUSCA EL RESTAURANTE POR NOMBRE PARA ENCONTRAR SU ID
        rest_query = text("SELECT RestauranteID FROM RESTAURANTES WHERE NombreRestaurante = :name")
        rest_result = session.execute(rest_query, {"name": restaurant_admin_for}).first()
        if rest_result:
            rest_id = rest_result[0]
            # ACTUALIZA LA SUCURSAL VINCULANDOLE EL USUARIOID ADMINISTRADOR
            update_query = text("UPDATE SUCURSALES SET UsuarioID = :uid WHERE RestauranteID = :rid")
            session.execute(update_query, {"uid": saved_user.UsuarioID, "rid": rest_id})
            session.commit()

    return saved_user

# COMPRUEBA LAS CREDENCIALES DE ACCESO Y RETORNA LOS DATOS DE SESION Y EL TOKEN
def login_user(session: Session, email: str, password: str, role: str, restaurant_admin_for: Optional[str] = None) -> dict:
    # BUSCA AL USUARIO EN LA BASE DE DATOS
    user = get_user_by_email(session, email)
    if not user:
        raise ValueError("Credenciales incorrectas.")

    # COMPARA LA CONTRASENA PROPORCIONADA
    if not verify_password(password, user.Contrasena):
        raise ValueError("Credenciales incorrectas.")

    # VALIDA QUE EL ROL COINCIDA CON EL DE ACCESO SELECCIONADO
    rol_map = {1: "customer", 2: "driver", 3: "admin", 4: "master"}
    mapped_role = rol_map.get(user.RolID, "customer")
    
    # El Usuario Maestro se salta la comprobacion del dropdown de roles
    if mapped_role != "master" and mapped_role != role:
        if not (mapped_role == "driver" and role == "customer"):
            raise ValueError("El rol seleccionado no coincide con la cuenta.")

    # SI ES REPARTIDOR, DEBE ESTAR APROBADO
    if mapped_role == "driver" and user.DriverStatus != "approved":
        raise ValueError("Tu solicitud de repartidor está pendiente de aprobación por el Usuario Maestro.")

    # SI EL USUARIO ES ADMIN, SE BUSCA EL NOMBRE DEL LOCAL PARA RETORNARLO AL FRONTEND
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
        
        # Validacion estricta del local
        if restaurant_name != restaurant_admin_for:
            raise ValueError(f"No tienes permisos para administrar el restaurante {restaurant_admin_for}.")

    # GENERA EL TOKEN DE ACCESO JWT
    token_data = {"sub": user.Email, "role": mapped_role}
    token = create_access_token(data=token_data)

    # CONSTRUYE EL DATO DE RETORNO PARA EL FRONTEND
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user.NombreUsuario,
            "email": user.Email,
            "role": mapped_role,
            "points": user.PuntosAJIGO,
            "phone": user.Telefono,
            "driverStatus": user.DriverStatus,
            "vehicleType": user.VehicleType,
            "licensePlate": user.LicensePlate,
            "restaurantAdminFor": restaurant_name,
            "accessToken": token,
            "loginViewMode": "master" if mapped_role == "master" else role
        }
    }
