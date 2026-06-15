# IMPORTA LAS DEPENDENCIAS DE FASTAPI Y LA BASE DE DATOS
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional, List
from sqlmodel import Session
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



@router.post("/pedidos/{pedido_id}/comprobante")
async def subir_comprobante_pago(
    pedido_id: int,
    archivo: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Sube el comprobante de pago al S3 y guarda el enlace en la BD.
    """
    # Validar que sea imagen o PDF
    tipos_permitidos = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes (JPG, PNG) o PDF"
        )

    # Subir a S3
    url = await subir_comprobante(archivo)

    # Guardar URL en la BD — ajusta según tu modelo de pagos
    session.execute(
        "UPDATE pagos SET comprobante_url = :url WHERE pedido_id = :id",
        {"url": url, "id": pedido_id}
    )
    session.commit()

    return {
        "mensaje": "Comprobante subido exitosamente",
        "url": url,
        "pedido_id": pedido_id
    }