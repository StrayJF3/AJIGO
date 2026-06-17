# IMPORTA LAS DEPENDENCIAS DE FASTAPI Y LA BASE DE DATOS
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional, List
from sqlmodel import Session, text
from infrastructure.s3_service import subir_comprobante
from infrastructure.database import get_session
from schemas.pedidos import OrderCreateRequest, StatusUpdateRequest, DriverAssignRequest
from domain.service import create_order, get_orders_list, update_order_status, assign_driver_to_order

# INSTANCIA EL ENRUTADOR DE RUTAS
router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

# RUTA PARA VERIFICAR LA SALUD DEL SERVICIO
@router.get("/health")
def health():
    return {"status": "ok"}

# RUTA PARA SUBIR UN COMPROBANTE AL S3 SIN ASOCIARLO AUN A UN PEDIDO
# EL FRONTEND SUBE PRIMERO LA IMAGEN Y LUEGO INCLUYE LA URL EN EL JSON DEL PEDIDO
@router.post("/comprobante/subir")
async def subir_comprobante_previo(archivo: UploadFile = File(...)):
    tipos_permitidos = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imagenes (JPG, PNG) o PDF"
        )
    try:
        url = await subir_comprobante(archivo)
        return {"url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el comprobante: {str(e)}"
        )

# RUTA PARA OBTENER EL HISTORIAL DE PEDIDOS FILTRADO POR PARAMETROS
@router.get("")
def get_orders(
    email: str,
    role: str,
    restaurantAdminFor: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        return get_orders_list(session, email, role, restaurantAdminFor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los pedidos: {str(e)}"
        )

# RUTA PARA REGISTRAR UN NUEVO PEDIDO
@router.post("")
def create_new_order_route(req: OrderCreateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict()
        user_email = req.userEmail
        return create_order(session, user_email, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # CAPTURA EXCEPCIONES GENERADAS POR LOS TRIGGERS (EJ. STOCK INSUFICIENTE)
        detail_msg = str(e)
        if "Stock insuficiente" in detail_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente para uno o mas productos del pedido."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el pedido: {detail_msg}"
        )

# RUTA PARA ACTUALIZAR EL ESTADO DE UN PEDIDO EXISTENTE
@router.put("/{order_id}/status")
def update_status_route(order_id: str, req: StatusUpdateRequest, session: Session = Depends(get_session)):
    try:
        return update_order_status(session, order_id, req.status)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado: {str(e)}"
        )

# RUTA PARA ASIGNAR UN REPARTIDOR A UN PEDIDO
@router.put("/{order_id}/driver")
def assign_driver_route(order_id: str, req: DriverAssignRequest, session: Session = Depends(get_session)):
    try:
        return assign_driver_to_order(session, order_id, req.driverName, req.driverEmail)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar repartidor: {str(e)}"
        )

# RUTA PARA OBTENER EL HISTORIAL DE ESTADOS DE UN PEDIDO
# USA LA VISTA V_HISTORIAL_ESTADOS QUE CONSOLIDA HISTORIAL + ESTADOS + USUARIO
# LOS DATOS SON GENERADOS AUTOMATICAMENTE POR EL TRIGGER TRG_PEDIDOS_HISTORIAL
@router.get("/{order_id}/historial")
def get_order_historial(order_id: str, session: Session = Depends(get_session)):
    try:
        # PARSEA AG-X A ENTERO
        ped_id = int(order_id.replace("AG-", "")) if order_id.startswith("AG-") else int(order_id)
        result = session.execute(
            text(
                "SELECT vh.HistorialID, vh.FechaCambio, vh.Estado, vh.NombreUsuario, vh.Email "
                "FROM V_HISTORIAL_ESTADOS vh "
                "WHERE vh.PedidoID = :pid "
                "ORDER BY vh.FechaCambio ASC"
            ),
            {"pid": ped_id}
        ).fetchall()

        historial = [
            {
                "historialId": row[0],
                "fecha": row[1].strftime("%Y-%m-%d %H:%M") if row[1] else None,
                "estado": row[2],
                "usuario": row[3],
                "email": row[4]
            }
            for row in result
        ]
        return {"pedidoId": order_id, "historial": historial}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


# RUTA PARA SUBIR EL COMPROBANTE DE PAGO AL S3 Y GUARDAR LA URL EN LA BD
@router.post("/{pedido_id}/comprobante")
async def subir_comprobante_pago(
    pedido_id: int,
    archivo: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # VALIDA QUE EL ARCHIVO SEA IMAGEN O PDF
    tipos_permitidos = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imagenes (JPG, PNG) o PDF"
        )

    try:
        # SUBE EL ARCHIVO AL BUCKET S3 Y OBTIENE LA URL PUBLICA
        url = await subir_comprobante(archivo)

        # GUARDA LA URL DEL COMPROBANTE EN LA TABLA PAGOS
        session.execute(
            text("UPDATE PAGOS SET ComprobanteURL = :url WHERE PedidoID = :id"),
            {"url": url, "id": pedido_id}
        )
        session.commit()

        return {
            "mensaje": "Comprobante subido exitosamente",
            "url": url,
            "pedido_id": pedido_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el comprobante: {str(e)}"
        )