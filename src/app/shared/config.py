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
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_cloud_name: str
    db_url: str
    jwt_secret: str

    insightface_model: str = "buffalo_l"
    insightface_det_size: tuple[int, int] = (640, 640)

    match_threshold: float = 0.35
    max_embeddings_per_person: int = 10


settings = Settings()
