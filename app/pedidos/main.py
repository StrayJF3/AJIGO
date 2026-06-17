# IMPORTA LA LIBRERIA PRINCIPAL DE FASTAPI Y MIDDELWARE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# CREA LA INSTANCIA DEL SERVICIO DE PEDIDOS
app = FastAPI(
    title="AJIGO Pedidos Service",
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
