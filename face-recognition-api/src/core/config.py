from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Face Recognition API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Modelo de InsightFace: buffalo_l = SCRFD + ArcFace (max precision)
    insightface_model: str = "buffalo_l"
    insightface_ctx_id: int = 0  # 0=GPU, -1=CPU

    # FAISS
    faiss_index_path: Path = Path("data/faces.index")
    faiss_metadata_path: Path = Path("data/faces.json")
    faiss_threshold: float = 0.65  # Similitud coseno minima para considerar match
    embedding_dim: int = 512

    # Deteccion
    det_thresh: float = 0.5
    det_size: tuple[int, int] = (640, 640)

    class Config:
        env_file = ".env"


settings = Settings()
