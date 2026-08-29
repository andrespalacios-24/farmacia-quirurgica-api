import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("farmacia-quirurgica")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validacion_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error de validación en los datos enviados.",
                "errores": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def error_generico_handler(request: Request, exc: Exception):
        logger.exception("Error no controlado: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor."},
        )