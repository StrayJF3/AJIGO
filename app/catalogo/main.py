# IMPORTA LA LIBRERIA PRINCIPAL DE FASTAPI Y MIDDELWARE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# CREA LA INSTANCIA DEL SERVICIO DE CATALOGO
app = FastAPI(
    title="AJIGO Catalogo Service",
    version="1.0.0"
)

# APLICA EL MIDDLEWARE CORS PARA PERMITIR CONEXIONES DIRECTAS DESDE EL NAVEGADOR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VINCULA EL ENRUTADOR DE RUTAS
app.include_router(router)

from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from infrastructure.database import get_session
from schemas.catalogo import DishCreateRequest
from domain.service import get_dishes_list, add_dish

# RUTA DIRECTA (SIN PREFIJO /CATALOGO) PARA OBTENER TODOS LOS PRODUCTOS ACTIVOS
@app.get("/productos")
def get_productos_direct(session: Session = Depends(get_session)):
    return get_dishes_list(session)

# RUTA DIRECTA (SIN PREFIJO /CATALOGO) PARA CREAR UN NUEVO PRODUCTO EN EL MENU
@app.post("/productos")
def create_producto_direct(req: DishCreateRequest, session: Session = Depends(get_session)):
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

