from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    mongodb_url: str = Field(..., alias="MONGODB_URL")
    database_name: str = Field("employee_management", alias="DATABASE_NAME")
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(90, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: str = Field("", alias="CORS_ORIGINS")
    seed_admin_email: str = Field(..., alias="SEED_ADMIN_EMAIL")
    seed_admin_password: str = Field(..., alias="SEED_ADMIN_PASSWORD")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()