from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    engine: str
    decolecta_api_key: str
    decolecta_base_url: str
    db_path: str

    insightface_model: str = "buffalo_l"
    insightface_det_size: tuple[int, int] = (640, 640)

    match_threshold: float = 0.35
    max_embeddings_per_person: int = 10


settings = Settings()
