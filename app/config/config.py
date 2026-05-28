from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application 
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="DEBUG")

    # Database Configuration (Required fields have no defaults to enforce strict safety)
    POSTGRES_USERNAME: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB_NAME: str = Field(...)
    SQL_LOG: bool = Field(default=False)

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Dynamically compiles the async SQLAlchemy database connection string 
        return f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB_NAME}"

    # JWT Security Configuration
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)

    # Email Service (Brevo) Configuration
    EMAIL_REQUEST_TIMEOUT_SECONDS: int = Field(default=30)
    EMAIL_MAX_RETRIES: int = Field(default=3)
    EMAIL_RETRY_BACKOFF_SECONDS: float = Field(default=1.0)
    BREVO_API_KEY: str = Field(default="")
    BREVO_FROM_EMAIL: str = Field(default="noreply@example.com")
    BREVO_FROM_NAME: str = Field(default="Application")
    BREVO_REPLY_TO_EMAIL: str = Field(default="")
    BREVO_REPLY_TO_NAME: str = Field(default="")
    OTP_EXPIRE_MINUTES: int = Field(default=15)

    # AI Provider Configuration
    AI_PROVIDER: str = Field(default="gemini")
    AI_MODEL: str = Field(default="gemini-2.5-flash")
    GEMINI_API_KEY: str = Field(default="")
    AI_API_URL: str = Field(default="https://generativelanguage.googleapis.com/v1beta/models")
    AI_REQUEST_TIMEOUT: int = Field(default=180)

    # Instructs Pydantic to natively map variables from your active .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Instantiates a single application-wide configuration context singleton
settings = Settings()