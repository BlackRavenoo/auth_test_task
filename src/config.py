from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/test_db"

    redis_url: str = "redis://localhost:6379"

    jwt_secret_key: str = "some-secret-key-some-secret-key-"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 14
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()