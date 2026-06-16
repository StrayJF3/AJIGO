# IMPORTA LAS DEPENDENCIAS DE FASTAPI Y LA BASE DE DATOS
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from infrastructure.database import get_session
from schemas.catalogo import RestaurantCreateRequest, RestaurantUpdateRequest, DishCreateRequest, DishUpdateRequest
from domain.service import (
    get_restaurants_list,
    create_restaurant,
    update_restaurant,
    get_dishes_list,
    add_dish,
    edit_dish,
    disable_dish
)

# INSTANCIA EL ENRUTADOR CON SU PREFIJO Y ETIQUETA
router = APIRouter(
    prefix="/catalogo",
    tags=["Catalogo"]
)

# RUTA PARA VERIFICAR LA SALUD DEL SERVICIO
@router.get("/health")
def health():
    return {"status": "ok"}

# RUTA PARA OBTENER TODOS LOS RESTAURANTES ACTIVOS
@router.get("/restaurants")
def get_restaurants(session: Session = Depends(get_session)):
    return get_restaurants_list(session)

# RUTA PARA CREAR UN NUEVO RESTAURANTE
@router.post("/restaurants")
def create_restaurant_route(req: RestaurantCreateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict()
        return create_restaurant(session, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )

# RUTA PARA ACTUALIZAR UN RESTAURANTE BUSCANDOLO POR SU SLUG
@router.put("/restaurants/{slug}")
def update_restaurant_route(slug: str, req: RestaurantUpdateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict(exclude_unset=True)
        return update_restaurant(session, slug, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )

# RUTA PARA OBTENER TODOS LOS PLATOS DE COMIDA ACTIVOS
@router.get("/dishes")
def get_dishes(session: Session = Depends(get_session)):
    return get_dishes_list(session)

# RUTA PARA CREAR UN NUEVO PLATO EN EL MENU
@router.post("/dishes")
def create_dish(req: DishCreateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict()
        return add_dish(session, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )

# RUTA PARA OBTENER TODOS LOS PRODUCTOS ACTIVOS
@router.get("/productos")
def get_productos(session: Session = Depends(get_session)):
    return get_dishes_list(session)

# RUTA PARA CREAR UN NUEVO PRODUCTO EN EL MENU
@router.post("/productos")
def create_producto(req: DishCreateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict()
        return add_dish(session, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )


# RUTA PARA ACTUALIZAR UN PLATO POR SU IDENTIFICADOR
@router.put("/dishes/{dish_id}")
def update_dish(dish_id: str, req: DishUpdateRequest, session: Session = Depends(get_session)):
    try:
        data = req.dict(exclude_unset=True)
        return edit_dish(session, dish_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )

# RUTA PARA DESACTIVAR UN PLATO (ELIMINACION LOGICA)
@router.delete("/dishes/{dish_id}")
def delete_dish(dish_id: str, session: Session = Depends(get_session)):
    try:
        disable_dish(session, dish_id)
        return {"status": "success", "message": "Plato desactivado con éxito."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error del servidor: {str(e)}"
        )
