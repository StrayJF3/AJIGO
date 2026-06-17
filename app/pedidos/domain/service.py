# IMPORTA LAS TIPACIONES REQUERIDAS DE SQLMODEL, JSON Y FECHAS
import json
from datetime import datetime
from typing import List, Dict, Optional
from sqlmodel import Session, text
from domain.models import Pedido, DetallePedido, Envio, get_ecuador_time
from infrastructure.repository import save_pedido, save_detalle, get_pedido_by_id, get_envio_by_pedido_id, save_envio

# PARSEA EL IDENTIFICADOR DEL FRONTEND "AG-XXXXXX" AL IDENTIFICADOR ENTERO DE BD
def parse_order_id(order_id: str) -> int:
    if order_id.startswith("AG-"):
        try:
            return int(order_id.replace("AG-", ""))
        except ValueError:
            raise ValueError("Formato de ID de pedido invalido.")
    try:
        return int(order_id)
    except ValueError:
        raise ValueError("Formato de ID de pedido invalido.")

# FORMATEA LA HORA Y FECHA SEGUN EL FORMATO ESPERADO
def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

# CREA Y REGISTRA UN PEDIDO COMPLETO CON SUS DETALLES EN LA BD
def create_order(session: Session, user_email: str, data: Dict) -> Dict:
    # BUSCA EL USUARIOID POR EL CORREO ELECTRONICO
    usr_query = text("SELECT UsuarioID FROM USUARIOS WHERE Email = :email")
    usr_res = session.execute(usr_query, {"email": user_email}).first()
    if not usr_res:
        raise ValueError("Usuario no registrado.")
    user_id = usr_res[0]

    # BUSCA LA SUCURSAL POR NOMBRE DE RESTAURANTE
    rest_name = data.get("restaurant", "UIDE Bakery")
    suc_query = text(
        "SELECT s.SucursalID FROM SUCURSALES s "
        "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
        "WHERE r.NombreRestaurante = :name"
    )
    suc_res = session.execute(suc_query, {"name": rest_name}).first()
    if not suc_res:
        raise ValueError("Sucursal no encontrada para el restaurante.")
    suc_id = suc_res[0]

    # MAPEA EL METODO DE LOGISTICA AL TIPOENTREGAID
    delivery_details = data.get("deliveryDetails", {})
    method = delivery_details.get("method", "delivery")
    tipo_entrega_id = 1 if method == "delivery" else 2

    # GUARDA LA DIRECCION DE ENTREGA EN DIRECCION_USUARIOS
    direccion_id = None
    if method == "delivery":
        faculty  = delivery_details.get("faculty", "")
        floor    = delivery_details.get("floor", "")
        classroom = delivery_details.get("classroom", "")
        notes    = delivery_details.get("notes", "")
        # CONSTRUYE LA DESCRIPCION COMPLETA DE LA DIRECCION
        descripcion = f"{faculty} | Piso: {floor} | Aula/Oficina: {classroom}"
        if notes:
            descripcion += f" | Indicaciones: {notes}"

        # OBTIENE EL SECTORID DEL SECTOR POR DEFECTO (UIDE)
        sector_query = text("SELECT TOP 1 SectorID FROM SECTORES")
        sector_res = session.execute(sector_query).first()
        sector_id = sector_res[0] if sector_res else 1

        # INSERTA LA NUEVA DIRECCION
        dir_query = text(
            "INSERT INTO DIRECCION_USUARIOS (UsuarioID, SectorID, Descripcion) "
            "OUTPUT INSERTED.DireccionUsuarioID "
            "VALUES (:uid, :sid, :desc)"
        )
        dir_res = session.execute(dir_query, {
            "uid": user_id,
            "sid": sector_id,
            "desc": descripcion
        }).first()
        session.commit()
        direccion_id = dir_res[0] if dir_res else None

    # CREA LA CABECERA DEL PEDIDO
    new_pedido = Pedido(
        UsuarioID=user_id,
        SucursalID=suc_id,
        DireccionUsuarioID=direccion_id,
        TipoEntregaID=tipo_entrega_id,
        EstadoPedidoID=1,  # RECIBIDO (EQUIVALE A 0 EN EL FRONTEND)
        Subtotal=data.get("subtotal", 0.0),
        CostoEnvio=data.get("deliveryFee", 0.0),
        MontoTotal=data.get("total", 0.0),
        FechaPedido=get_ecuador_time()
    )

    # ALMACENA LA CABECERA
    saved_pedido = save_pedido(session, new_pedido)
    order_db_id = saved_pedido.PedidoID

    # PROCESA Y GUARDA CADA DETALLE DE PLATILLO COMPRADO
    items_data = data.get("items", [])
    for item in items_data:
        # CONSULTA EL PRODUCTOID BUSCANDO POR EL NOMBRE DEL PRODUCTO EN LA SUCURSAL
        item_name = item.get("name")
        prod_query = text("SELECT ProductoID FROM PRODUCTOS WHERE NombreProducto = :name AND SucursalID = :sid")
        prod_res = session.execute(prod_query, {"name": item_name, "sid": suc_id}).first()
        
        if not prod_res:
            raise ValueError(f"Producto no encontrado: {item_name}")
        prod_id = prod_res[0]

        # CREA EL DETALLE DE COMPRA
        new_detail = DetallePedido(
            PedidoID=order_db_id,
            ProductoID=prod_id,
            Cantidad=item.get("quantity", 1),
            PrecioUnitario=item.get("price", 0.0),
            PrecioFinal=item.get("price", 0.0) * item.get("quantity", 1),
            Notas=item.get("notes")
        )
        save_detalle(session, new_detail)

    # REGISTRA EL COMPROBANTE DE PAGO SI EXISTE EN LA TABLA PAGOS
    transfer_receipt = data.get("transferReceipt")
    metodo_pago_id = 2 if transfer_receipt else 1
    pay_query = text(
        "INSERT INTO PAGOS (PedidoID, MetodoPagoID, Monto, EstadoPago, ComprobanteURL, FechaPago) "
        "VALUES (:pedido_id, :metodo_pago_id, :monto, :estado_pago, :comprobante_url, :fecha_pago)"
    )
    session.execute(pay_query, {
        "pedido_id": order_db_id,
        "metodo_pago_id": metodo_pago_id,
        "monto": saved_pedido.MontoTotal,
        "estado_pago": "Pendiente de Verificacion" if transfer_receipt else "Pendiente",
        "comprobante_url": transfer_receipt,
        "fecha_pago": get_ecuador_time()
    })
    session.commit()

    # OTORGA 10 PUNTOS AJIGO AL CLIENTE POR REALIZAR UN PEDIDO
    session.execute(
        text("UPDATE USUARIOS SET PuntosAJIGO = PuntosAJIGO + 10 WHERE UsuarioID = :uid"),
        {"uid": user_id}
    )
    session.commit()

    # LIMPIA EL CARRITO EN LA BASE DE DATOS (EL PEDIDO YA FUE CREADO)
    session.execute(
        text("DELETE FROM CARRITO_ITEMS WHERE CarritoID IN (SELECT CarritoID FROM CARRITOS WHERE UsuarioID = :uid)"),
        {"uid": user_id}
    )
    session.execute(
        text("DELETE FROM CARRITOS WHERE UsuarioID = :uid"),
        {"uid": user_id}
    )
    session.commit()

    # RETORNA EL PEDIDO CON FORMATO FRONTEND
    return {
        "id": f"AG-{order_db_id}",
        "items": items_data,
        "subtotal": saved_pedido.Subtotal,
        "deliveryFee": saved_pedido.CostoEnvio,
        "discount": data.get("discount", 0.0),
        "tax": data.get("tax", 0.0),
        "total": saved_pedido.MontoTotal,
        "coupon": data.get("coupon"),
        "deliveryDetails": delivery_details,
        "status": 0,
        "createdAt": format_time(saved_pedido.FechaPedido),
        "restaurant": rest_name,
        "transferReceipt": transfer_receipt,
        "pointsEarned": 10
    }

# OBTIENE EL HISTORIAL DE PEDIDOS SEGUN EL ROL Y EL USUARIO
# USA LA VISTA V_PEDIDOS_COMPLETO QUE CONSOLIDA PEDIDOS + USUARIO + RESTAURANTE + DIRECCION
def get_orders_list(session: Session, email: str, role: str, restaurant_admin_for: Optional[str] = None) -> List[Dict]:
    # LA VISTA V_PEDIDOS_COMPLETO INCLUYE: PedidoID, FechaPedido, Subtotal, CostoEnvio, MontoTotal,
    # UsuarioID, NombreUsuario, Email, SucursalID, DireccionSucursal, NombreRestaurante,
    # EstadoPedido (texto), TipoEntrega (texto), DireccionEntrega (texto de DIRECCION_USUARIOS)
    query_str = (
        "SELECT v.PedidoID, v.Subtotal, v.CostoEnvio, v.MontoTotal, v.FechaPedido, "
        "       v.EstadoPedido, v.TipoEntrega, v.NombreRestaurante, v.Email, "
        "       v.DireccionEntrega, "
        "       dr.NombreUsuario AS DriverName, dr.Telefono AS DriverPhone, dr.VehicleType AS DriverVehicle, "
        "       pg.ComprobanteURL, ep.EstadoPedidoID "
        "FROM V_PEDIDOS_COMPLETO v "
        "INNER JOIN ESTADOS_PEDIDO ep ON v.EstadoPedido = ep.EstadoSTR "
        "LEFT JOIN ENVIOS e  ON v.PedidoID = e.PedidoID "
        "LEFT JOIN USUARIOS dr ON e.UsuarioID = dr.UsuarioID "
        "LEFT JOIN PAGOS pg ON v.PedidoID = pg.PedidoID"
    )

    # APLICA FILTROS ACORDE AL ROL DE SESION
    params = {}
    if role == "admin" and restaurant_admin_for:
        query_str += " WHERE v.NombreRestaurante = :restaurantName"
        params["restaurantName"] = restaurant_admin_for
    elif role == "driver":
        # LOS REPARTIDORES VEN TODOS LOS PEDIDOS ACTIVOS EN COLA
        query_str += " WHERE ep.EstadoPedidoID IN (1, 2, 3)"
    else:
        # LOS CLIENTES VEN SOLO SUS PROPIOS PEDIDOS
        query_str += " WHERE v.Email = :email"
        params["email"] = email

    # ORDENA LOS PEDIDOS POR FECHA DESCENDENTE
    query_str += " ORDER BY v.FechaPedido DESC"

    orders_res = session.execute(text(query_str), params).fetchall()

    formatted_orders = []
    for row in orders_res:
        ped_id = row[0]

        # USA LA VISTA V_DETALLE_PEDIDO_PRODUCTOS QUE CONSOLIDA DETALLE + PRODUCTOS + CATEGORIAS
        details_query = text(
            "SELECT vd.Cantidad, vd.PrecioUnitario, vd.Notas, vd.NombreProducto, pr.BadgeText "
            "FROM V_DETALLE_PEDIDO_PRODUCTOS vd "
            "INNER JOIN PRODUCTOS pr ON vd.ProductoID = pr.ProductoID "
            "WHERE vd.PedidoID = :pid"
        )
        details_res = session.execute(details_query, {"pid": ped_id}).fetchall()

        items = []
        for det in details_res:
            items.append({
                "quantity": det[0],
                "price": det[1],
                "notes": det[2] or "",
                "name": det[3],
                "badgeText": det[4] or ""
            })

        # PARSEA LA DireccionEntrega QUE YA VIENE RESUELTA DESDE V_PEDIDOS_COMPLETO
        # FORMATO: "Facultad | Piso: X | Aula/Oficina: Y | Indicaciones: Z"
        is_delivery = (row[6] == "Delivery")  # TipoEntrega como texto desde la vista
        faculty_str   = "Campus UIDE"
        floor_str     = ""
        classroom_str = ""
        notes_str     = ""

        if is_delivery and row[9]:  # DireccionEntrega
            parts = [p.strip() for p in row[9].split("|")]
            faculty_str   = parts[0] if len(parts) > 0 else "Campus UIDE"
            floor_str     = parts[1].replace("Piso:", "").strip() if len(parts) > 1 else ""
            classroom_str = parts[2].replace("Aula/Oficina:", "").strip() if len(parts) > 2 else ""
            notes_str     = parts[3].replace("Indicaciones:", "").strip() if len(parts) > 3 else ""

        delivery_details = {
            "method": "delivery" if is_delivery else "pickup",
            "faculty": faculty_str,
            "floor": floor_str,
            "classroom": classroom_str,
            "notes": notes_str
        }

        # CONSTRUYE EL OBJETO DE PEDIDO PARA EL FRONTEND
        db_status_id = row[14]  # EstadoPedidoID numerico
        order_dict = {
            "id": f"AG-{ped_id}",
            "items": items,
            "subtotal": row[1],
            "deliveryFee": row[2],
            "discount": 0.0,
            "tax": 0.0,
            "total": row[3],
            "coupon": None,
            "deliveryDetails": delivery_details,
            "status": db_status_id - 1,  # AJUSTE 0-BASED PARA EL FRONTEND
            "createdAt": format_time(row[4]),
            "restaurant": row[7],
            "transferReceipt": row[13]
        }

        if row[10]:  # SI DRIVERNAME NO ES NULO
            order_dict["driverName"] = row[10]
            order_dict["driverVehicle"] = row[12] or "Motocicleta Honda (AJI-990)"
            order_dict["driverPhone"] = row[11] or "+593 98 765 4321"

        formatted_orders.append(order_dict)

    return formatted_orders

# ACTUALIZA EL ESTADO INTERNO DEL PEDIDO EN LA BASE DE DATOS
def update_order_status(session: Session, order_id: str, new_status: int) -> Dict:
    ped_id = parse_order_id(order_id)
    pedido = get_pedido_by_id(session, ped_id)
    if not pedido:
        raise ValueError("Pedido no encontrado.")

    # TRADUCE EL ESTADO 0-BASED AL ID BD (1-BASED)
    db_status_id = new_status + 1
    pedido.EstadoPedidoID = db_status_id

    # CUANDO EL RESTAURANTE EMPIEZA LA COCCION (STATUS 1 = "EN PREPARACION"),
    # SE VERIFICA EL PAGO AUTOMATICAMENTE
    if db_status_id == 2:
        session.execute(
            text("UPDATE PAGOS SET EstadoPago = 'Verificado' WHERE PedidoID = :pid"),
            {"pid": ped_id}
        )
    
    # SI EL PEDIDO FUE ENTREGADO, SE DAN 5 PUNTOS AJIGO AL REPARTIDOR
    if db_status_id == 4:
        envio = get_envio_by_pedido_id(session, ped_id)
        if envio:
            # OTORGA 5 PUNTOS AJIGO AL REPARTIDOR QUE COMPLETO LA ENTREGA
            session.execute(
                text("UPDATE USUARIOS SET PuntosAJIGO = PuntosAJIGO + 5 WHERE UsuarioID = :uid"),
                {"uid": envio.UsuarioID}
            )
            envio.EstadoID = 3  # ENTREGADO
            envio.FechaEntrega = get_ecuador_time()
            save_envio(session, envio)

    save_pedido(session, pedido)
    return {"id": order_id, "status": new_status}

# ASIGNA UN REPARTIDOR AL PEDIDO E INICIA EL HISTORIAL DE ENVIO
def assign_driver_to_order(session: Session, order_id: str, driver_name: str, driver_email: str) -> Dict:
    ped_id = parse_order_id(order_id)
    pedido = get_pedido_by_id(session, ped_id)
    if not pedido:
        raise ValueError("Pedido no encontrado.")

    # BUSCA AL REPARTIDOR EN LA TABLA DE USUARIOS
    drv_query = text("SELECT UsuarioID, Telefono, VehicleType FROM USUARIOS WHERE Email = :email")
    drv_res = session.execute(drv_query, {"email": driver_email}).first()
    if not drv_res:
        raise ValueError("Repartidor no registrado.")
    
    driver_id = drv_res[0]
    driver_phone = drv_res[1] or "+593 98 765 4321"
    driver_vehicle = drv_res[2] or "Motocicleta Honda (AJI-990)"

    # COMPRUEBA SI YA EXISTE UN ENVIO PARA ESTE PEDIDO
    envio = get_envio_by_pedido_id(session, ped_id)
    if not envio:
        envio = Envio(
            PedidoID=ped_id,
            UsuarioID=driver_id,
            EstadoID=1,  # ASIGNADO
            FechaInicio=get_ecuador_time()
        )
    else:
        envio.UsuarioID = driver_id
        envio.EstadoID = 1

    save_envio(session, envio)

    # ACTUALIZA EL ESTADO DEL PEDIDO A "LISTO / EN CAMINO" (STATUS 2 EN EL FRONTEND)
    pedido.EstadoPedidoID = 3
    save_pedido(session, pedido)

    return {
        "driverName": driver_name,
        "driverVehicle": driver_vehicle,
        "driverPhone": driver_phone
    }


# OBTIENE EL CARRITO PERSISTIDO DE UN USUARIO DESDE LA BASE DE DATOS
def get_user_cart(session: Session, email: str) -> List[Dict]:
    # 1. Busca el UsuarioID
    usr_res = session.execute(text("SELECT UsuarioID FROM USUARIOS WHERE Email = :email"), {"email": email}).first()
    if not usr_res:
        raise ValueError("Usuario no encontrado.")
    user_id = usr_res[0]

    # 2. Busca el CarritoID activo del usuario
    car_res = session.execute(text("SELECT CarritoID FROM CARRITOS WHERE UsuarioID = :uid"), {"uid": user_id}).first()
    if not car_res:
        return []
    car_id = car_res[0]

    # 3. Consulta los items en el carrito
    query = text(
        "SELECT ci.ItemID, ci.ProductoID, ci.Cantidad, ci.Notas, "
        "       p.NombreProducto, p.Precio, p.BadgeText, r.NombreRestaurante "
        "FROM CARRITO_ITEMS ci "
        "INNER JOIN PRODUCTOS p ON ci.ProductoID = p.ProductoID "
        "INNER JOIN SUCURSALES s ON p.SucursalID = s.SucursalID "
        "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
        "WHERE ci.CarritoID = :cid"
    )
    items_res = session.execute(query, {"cid": car_id}).fetchall()

    cart_items = []
    for row in items_res:
        size = ""
        extras = []
        notes = ""
        raw_notes = row[3]
        if raw_notes:
            try:
                parsed = json.loads(raw_notes)
                size = parsed.get("size", "")
                extras = parsed.get("extras", [])
                notes = parsed.get("notes", "")
            except Exception:
                notes = raw_notes

        cart_items.append({
            "id": f"dbitem-{row[0]}",
            "baseId": str(row[1]),
            "name": row[4],
            "price": row[5],
            "quantity": row[2],
            "size": size,
            "extras": extras,
            "notes": notes,
            "badgeText": row[6] or "",
            "restaurant": row[7]
        })
    return cart_items


# GUARDA / SINCRONIZA EL CARRITO COMPLETO DE UN USUARIO
def save_user_cart(session: Session, email: str, items: List) -> Dict:
    # 1. Busca el UsuarioID
    usr_res = session.execute(text("SELECT UsuarioID FROM USUARIOS WHERE Email = :email"), {"email": email}).first()
    if not usr_res:
        raise ValueError("Usuario no encontrado.")
    user_id = usr_res[0]

    # 2. Limpia el carrito viejo para evitar basura
    old_carts = session.execute(text("SELECT CarritoID FROM CARRITOS WHERE UsuarioID = :uid"), {"uid": user_id}).fetchall()
    for row in old_carts:
        session.execute(text("DELETE FROM CARRITO_ITEMS WHERE CarritoID = :cid"), {"cid": row[0]})
    session.execute(text("DELETE FROM CARRITOS WHERE UsuarioID = :uid"), {"uid": user_id})
    session.commit()

    if not items:
        return {"status": "success", "message": "Carrito vaciado en base de datos."}

    # 3. Obtiene la SucursalID del primer item en el carrito
    first_item = items[0]
    try:
        p_id_first = int(first_item.baseId)
    except (ValueError, TypeError):
        p_id_first = 1

    prod_res = session.execute(text("SELECT SucursalID FROM PRODUCTOS WHERE ProductoID = :pid"), {"pid": p_id_first}).first()
    suc_id = prod_res[0] if prod_res else 1

    # 4. Inserta cabecera de Carrito
    ins_res = session.execute(
        text("INSERT INTO CARRITOS (UsuarioID, SucursalID, FechaActualizacion) "
             "OUTPUT INSERTED.CarritoID "
             "VALUES (:uid, :sid, GETDATE())"),
        {"uid": user_id, "sid": suc_id}
    ).first()
    session.commit()

    if not ins_res:
        raise ValueError("No se pudo crear la cabecera del carrito.")
    new_car_id = ins_res[0]

    # 5. Inserta cada item del carrito serializando las opciones en 'Notas'
    for item in items:
        try:
            p_id = int(item.baseId)
        except (ValueError, TypeError):
            continue

        notas_dict = {
            "size": item.size or "",
            "extras": item.extras or [],
            "notes": item.notes or ""
        }
        serialized_notes = json.dumps(notas_dict)

        session.execute(
            text("INSERT INTO CARRITO_ITEMS (CarritoID, ProductoID, Cantidad, Notas) "
                 "VALUES (:cid, :pid, :qty, :notas)"),
            {
                "cid": new_car_id,
                "pid": p_id,
                "qty": item.quantity,
                "notas": serialized_notes
            }
        )
    session.commit()
    return {"status": "success", "message": "Carrito guardado exitosamente."}

