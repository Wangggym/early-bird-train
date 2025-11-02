"""Application settings using Pydantic Settings"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings (strongly typed)"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === Application Configuration ===
    app_name: str = Field(default="Early Bird Train", description="Application name")
    log_level: str = Field(default="INFO", description="Log level")

    # === Monitoring Configuration ===
    departure_station: str = Field(default="大邑", description="Departure station")
    arrival_station: str = Field(default="成都南", description="Arrival station")
    train_number: str = Field(default="C3380", description="Train number")
    days_ahead: int = Field(default=15, ge=1, le=30, description="Days ahead to query")

    # === Schedule Configuration ===
    schedule_days_of_week: list[int] = Field(
        default=[0], description="Schedule days list (0=Monday, multiple days separated by comma)"
    )
    schedule_hour: int = Field(default=15, ge=0, le=23, description="Schedule hour")
    schedule_minute: int = Field(default=30, ge=0, le=59, description="Schedule minute")
    max_retries: int = Field(default=5, ge=1, le=10, description="Retry count (Fibonacci backoff)")

    # === DeepSeek Configuration ===
    deepseek_api_key: str = Field(..., description="DeepSeek API key")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", description="DeepSeek API URL")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek model")

    # === Email Configuration ===
    smtp_host: str = Field(..., description="SMTP server address")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")
    email_from: str = Field(..., description="Sender email address")
    email_to: list[str] = Field(..., description="Recipient email list")

    # === Crawler Configuration ===
    crawler_timeout: int = Field(default=10, ge=1, le=60, description="Crawler timeout (seconds)")


def load_settings() -> Settings:
    """Load settings"""
    return Settings()  # type: ignore
