from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FR_", extra="ignore")

    engine: str

    insightface_model: str = "buffalo_l"
    insightface_det_size: tuple[int, int] = (640, 640)

    match_threshold: float = 0.35

    db_path: str = "./data/fr.sqlite3"
    max_embeddings_per_person: int = 10


settings = Settings()
