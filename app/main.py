from fastapi import FastAPI
from app.config import settings

# 1. Creación de la instancia principal de FastAPI
app = FastAPI(
    title="API Farmacia Quirúrgica",
    description="Sistema de gestión, entrega y trazabilidad de insumos médicos en quirófano",
    version="1.0.0"
)

# 2. Ruta principal (Endpoint de prueba de vida / Health Check)
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a la API de Farmacia Quirúrgica",
        "estado": "Servidor en línea"
    }