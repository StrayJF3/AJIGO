# IMPORTA FASTAPI Y EL INYECTOR DE MIDDLEWARE CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# CREA LA INSTANCIA DE LA APLICACION
app = FastAPI(
    title="AJIGO Auth Service",
    version="1.0.0"
)

# REGISTRA EL MIDDLEWARE DE CORS PARA PERMITIR CONEXIONES DIRECTAS DESDE EL FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENLAZA LAS RUTAS DEFINIDAS
app.include_router(router)