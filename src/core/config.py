from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Keep settings minimal. When you add real model adapters (ONNX/PyTorch),
    put model paths and thresholds here.
    """

    model_config = SettingsConfigDict(env_prefix="FR_", extra="ignore")

    match_threshold: float = 0.35


settings = Settings()

