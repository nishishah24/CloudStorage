from pathlib import Path
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Cloud File Storage Service"

    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "postgres"
    postgres_port: int = 5432
    postgres_host: str = "127.0.0.1"
    custom_database_url: str = ""

    secret_key: str = "default_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    storage_path: str = "storage"
    firebase_storage_bucket: str = ""
    firebase_credentials_path: str = ""
    firebase_credentials_json: str = ""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @computed_field
    @property
    def database_url(self) -> str:
        if self.custom_database_url:
            return self.custom_database_url
        encoded_password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{self.postgres_user}:"
            f"{encoded_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )


settings = Settings()