from fastapi import FastAPI
from app.config import settings
from app.routers import pacientes, procedimientos
from app.routers import insumos
from app.routers import auth
from app.routers import usuarios

# 1. Creación de la instancia principal de FastAPI
app = FastAPI(
    title="API Farmacia Quirúrgica",
    description="Sistema de gestión, entrega y trazabilidad de insumos médicos en quirófano",
    version="1.0.0"
    )

app.include_router(pacientes.router)
app.include_router(procedimientos.router) 
app.include_router(insumos.router)
app.include_router(auth.router)
app.include_router(usuarios.router)

# 2. Ruta principal (Endpoint de prueba de vida / Health Check)
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a la API de Farmacia Quirúrgica",
        "estado": "Servidor en línea"
    }