import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.domain_exceptions import DomainException
from app.core.i18n import i18n, get_locale_from_header

logger = logging.getLogger("farmacia-quirurgica")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        locale = get_locale_from_header(request.headers.get("accept-language"))
        translated_msg = i18n.translate(exc.key, locale, **exc.kwargs)
        logger.warning(f"Domain exception: {translated_msg}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": translated_msg},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        locale = get_locale_from_header(request.headers.get("accept-language"))
        translated_msg = i18n.translate("errors.validation", locale)
        return JSONResponse(
            status_code=422,
            content={
                "detail": translated_msg,
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        locale = get_locale_from_header(request.headers.get("accept-language"))
        translated_msg = i18n.translate("errors.internal", locale)
        return JSONResponse(
            status_code=500,
            content={"detail": translated_msg},
        )