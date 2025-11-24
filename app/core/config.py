from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Project settings
    PROJECT_NAME: str = "Smart Stock"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Plataforma de inteligência preditiva para e-commerce."

    # AWS Settings (placeholders)
    AWS_ACCESS_KEY_ID: str = "YOUR_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY: str = "YOUR_AWS_SECRET_ACCESS_KEY"
    AWS_SESSION_TOKEN: str = "" # Optional: for temporary credentials
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "smart-stock-data-bucket"

    # Database Settings (placeholders for local docker)
    DATABASE_URL: str = "postgresql://user:password@db:5432/smart-stock"

settings = Settings()
