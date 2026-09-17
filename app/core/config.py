from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    test_database_url: str
    redis_url: str
    test_redis_url: str
    inventory_cache_ttl_seconds: int = 30
    # 5173: Vite dev server. 8080: the containerized frontend (nginx, Stage 5 Dockerfile).
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]


settings = Settings()
