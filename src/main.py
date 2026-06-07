from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.app.identification.interfaces.rest.dependencies import init_database
from src.app.identification.interfaces.rest.transform.IdentificationRouter import (
    router as identification_router,
)
from src.app.shared.exceptions import ConflictError, DomainError, NotFoundError, ValidationError


def create_app() -> FastAPI:
    app = FastAPI(title="Face Recognition API", version="0.1.0")
    app.include_router(identification_router)

    @app.on_event("startup")
    async def _init_database() -> None:
        await init_database()

    @app.exception_handler(ValidationError)
    async def _validation_error_handler(_request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def _request_validation_error_handler(_request, _exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": "Invalid request payload"})

    @app.exception_handler(NotFoundError)
    async def _not_found_error_handler(_request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def _conflict_error_handler(_request, exc: ConflictError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def _domain_error_handler(_request, exc: DomainError):
        return JSONResponse(status_code=400, content={"detail": "Invalid request"})

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(_request, _exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
