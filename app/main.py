from fastapi import FastAPI
from app.api.router import api_router
from app.core.exceptions import register_exception_handlers

# 1. Main FastAPI instance creation
app = FastAPI(
    title="Surgical Pharmacy API",
    description="System for managing, delivering and tracking medical supplies in the operating room",
    version="1.0.0"
)

register_exception_handlers(app) 
app.include_router(api_router)

# 2. Main route (Health Check Endpoint)
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Surgical Pharmacy API",
        "status": "Server online"
    }