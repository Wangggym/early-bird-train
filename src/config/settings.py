"""Application settings using Pydantic Settings"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置（强类型）"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === 应用配置 ===
    app_name: str = Field(default="Early Bird Train", description="应用名称")
    log_level: str = Field(default="INFO", description="日志级别")

    # === 监控配置 ===
    departure_station: str = Field(default="大邑", description="出发站")
    arrival_station: str = Field(default="成都南", description="到达站")
    train_number: str = Field(default="C3380", description="车次号")
    days_ahead: int = Field(default=15, ge=1, le=30, description="提前天数")

    # === 调度配置 ===
    schedule_day_of_week: int = Field(default=0, ge=0, le=6, description="调度日期（0=周一）")
    schedule_hour: int = Field(default=15, ge=0, le=23, description="调度小时")
    schedule_minute: int = Field(default=30, ge=0, le=59, description="调度分钟")

    # === DeepSeek配置 ===
    deepseek_api_key: str = Field(..., description="DeepSeek API密钥")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", description="DeepSeek API地址")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek模型")

    # === 邮件配置 ===
    smtp_host: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(default=587, description="SMTP端口")
    smtp_user: str = Field(..., description="SMTP用户名")
    smtp_password: str = Field(..., description="SMTP密码")
    email_from: str = Field(..., description="发件人邮箱")
    email_to: list[str] = Field(..., description="收件人邮箱列表")

    # === 爬虫配置 ===
    crawler_timeout: int = Field(default=10, ge=1, le=60, description="爬虫超时时间（秒）")


def load_settings() -> Settings:
    """加载配置"""
    return Settings()  # type: ignore
