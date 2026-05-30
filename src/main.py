from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.routes import router as api_router
from src.core.exceptions import DomainError, NotFoundError, ValidationError


def create_app() -> FastAPI:
    app = FastAPI(title="Face Recognition API", version="0.1.0")
    app.include_router(api_router)

    @app.exception_handler(ValidationError)
    async def _validation_error_handler(_request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(NotFoundError)
    async def _not_found_error_handler(_request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def _domain_error_handler(_request, exc: DomainError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app


app = create_app()
