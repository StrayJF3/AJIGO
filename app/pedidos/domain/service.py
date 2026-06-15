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
    method = data.get("deliveryDetails", {}).get("method", "delivery")
    tipo_entrega_id = 1 if method == "delivery" else 2

    # CREA LA CABECERA DEL PEDIDO
    new_pedido = Pedido(
        UsuarioID=user_id,
        SucursalID=suc_id,
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
        "deliveryDetails": data.get("deliveryDetails"),
        "status": 0,
        "createdAt": format_time(saved_pedido.FechaPedido),
        "restaurant": rest_name,
        "transferReceipt": transfer_receipt
    }

# OBTIENE EL HISTORIAL DE PEDIDOS SEGUN EL ROL Y EL USUARIO
def get_orders_list(session: Session, email: str, role: str, restaurant_admin_for: Optional[str] = None) -> List[Dict]:
    # CONSTRUYE LA CONSULTA BASE DE LOS PEDIDOS
    query_str = (
        "SELECT p.PedidoID, p.Subtotal, p.CostoEnvio, p.MontoTotal, p.FechaPedido, p.EstadoPedidoID, p.TipoEntregaID, "
        "       r.NombreRestaurante, u.Email, "
        "       dr.NombreUsuario AS DriverName, dr.Telefono AS DriverPhone, dr.VehicleType AS DriverVehicle, "
        "       pg.ComprobanteURL "
        "FROM PEDIDOS p "
        "INNER JOIN USUARIOS u ON p.UsuarioID = u.UsuarioID "
        "INNER JOIN SUCURSALES s ON p.SucursalID = s.SucursalID "
        "INNER JOIN RESTAURANTES r ON s.RestauranteID = r.RestauranteID "
        "LEFT JOIN ENVIOS e ON p.PedidoID = e.PedidoID "
        "LEFT JOIN USUARIOS dr ON e.UsuarioID = dr.UsuarioID "
        "LEFT JOIN PAGOS pg ON p.PedidoID = pg.PedidoID"
    )
    
    # APLICA FILTROS ACORDE AL ROL DE SESION
    params = {}
    if role == "admin" and restaurant_admin_for:
        query_str += " WHERE r.NombreRestaurante = :restaurantName"
        params["restaurantName"] = restaurant_admin_for
    elif role == "driver":
        # LOS REPARTIDORES VEN TODOS LOS PEDIDOS ACTIVOS EN COLA
        query_str += " WHERE p.EstadoPedidoID IN (1, 2, 3)"
    else:
        # LOS CLIENTES VEN SOLO SUS PROPIOS PEDIDOS
        query_str += " WHERE u.Email = :email"
        params["email"] = email

    # ORDENA LOS PEDIDOS POR FECHA DESCENDENTE
    query_str += " ORDER BY p.FechaPedido DESC"
    
    orders_res = session.execute(text(query_str), params).fetchall()
    
    formatted_orders = []
    for row in orders_res:
        ped_id = row[0]
        
        # CONSULTA LOS DETALLES PARA CADA PEDIDO
        details_query = text(
            "SELECT dp.Cantidad, dp.PrecioUnitario, dp.Notas, pr.NombreProducto, pr.BadgeText "
            "FROM DETALLE_PEDIDO dp "
            "INNER JOIN PRODUCTOS pr ON dp.ProductoID = pr.ProductoID "
            "WHERE dp.PedidoID = :pid"
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

        # RECUPERA DETALLES DE DIRECCION DE LA SUCURSAL O LOGISTICA
        # SIMULA DETALLES DE ENTREGA SI ES LOGISTICA DELIVERY
        method = "delivery" if row[6] == 1 else "pickup"
        delivery_details = {
            "method": method,
            "faculty": "Campus UIDE",
            "floor": "",
            "classroom": "",
            "notes": ""
        }

        # RETORNA EL MODELADO FRONTEND CON LOS CAMPOS DE REPARTIDOR SI ESTA ASIGNADO
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
            "status": row[5] - 1,  # AJUSTE PARA ENCAJAR CON ESTADO 0-BASED EN FRONTEND
            "createdAt": format_time(row[4]),
            "restaurant": row[7],
            "transferReceipt": row[12]
        }

        if row[9]:  # SI DRIVERNAME NO ES NULO
            order_dict["driverName"] = row[9]
            order_dict["driverVehicle"] = row[11] or "Motocicleta Honda (AJI-990)"
            order_dict["driverPhone"] = row[10] or "+593 98 765 4321"

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
    
    # SI EL PEDIDO FUE ENTREGADO, SE ACTUALIZAN LOS PUNTOS AL CLIENTE (15 PUNTOS POR PEDIDO)
    if db_status_id == 4:
        user_update_query = text("UPDATE USUARIOS SET PuntosAJIGO = PuntosAJIGO + 15 WHERE UsuarioID = :uid")
        session.execute(user_update_query, {"uid": pedido.UsuarioID})
        
        # SI HAY UN ENVIO ACTIVO, SE LE COLOCA FECHA DE ENTREGA
        envio = get_envio_by_pedido_id(session, ped_id)
        if envio:
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
