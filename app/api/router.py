from fastapi import APIRouter
from app.routers import auth, users, patients, procedures, supplies

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patients.router)
api_router.include_router(procedures.router)
api_router.include_router(supplies.router)