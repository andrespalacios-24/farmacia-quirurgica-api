from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.exceptions import register_exception_handlers

# 1. Main FastAPI instance creation
app = FastAPI(
    title="Surgical Pharmacy API",
    description="System for managing, delivering and tracking medical supplies in the operating room",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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