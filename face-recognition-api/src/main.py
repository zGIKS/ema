from fastapi import FastAPI
from src.api.routes import router
from src.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API de reconocimiento facial con InsightFace + FAISS",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
    )
