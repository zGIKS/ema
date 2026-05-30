from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Keep settings minimal. When you add real model adapters (ONNX/PyTorch),
    put model paths and thresholds here.
    """

    model_config = SettingsConfigDict(env_prefix="FR_", extra="ignore")

    # Which engine implementation to use.
    # - auto: use InsightFace if installed, else fallback to stub
    # - stub: deterministic fake embeddings (dev only)
    # - insightface: real detection + embedding via InsightFace (recommended)
    engine: str = "auto"

    # InsightFace config (only used when engine=insightface/auto and deps installed).
    insightface_model: str = "buffalo_l"
    insightface_det_size: tuple[int, int] = (640, 640)

    # Cosine similarity threshold in [-1, 1].
    # Typical values for ArcFace-like embeddings are around 0.3-0.6 depending on your data.
    match_threshold: float = 0.35

    # Persistence (MVP): store embeddings in a local SQLite file.
    # For a single-server setup this is usually enough.
    db_path: str = "./data/fr.sqlite3"
    max_embeddings_per_person: int = 10


settings = Settings()
