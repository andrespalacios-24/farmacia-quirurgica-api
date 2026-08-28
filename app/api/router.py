from fastapi import APIRouter
from app.routers import auth, usuarios, pacientes, procedimientos, insumos

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(pacientes.router)
api_router.include_router(procedimientos.router)
api_router.include_router(insumos.router)