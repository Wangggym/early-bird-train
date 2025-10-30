"""Dependency Injection Container"""

from dependency_injector import containers, providers

from src.application.ticket_service import TicketMonitorService
from src.config.settings import Settings
from src.infrastructure.analyzer import DeepSeekAnalyzer
from src.infrastructure.crawler import CtripTicketCrawler
from src.infrastructure.notifier import EmailNotifier
from src.infrastructure.scheduler import APSchedulerWrapper


class Container(containers.DeclarativeContainer):
    """依赖注入容器"""

    # === 配置 ===
    config = providers.Singleton(Settings)

    # === 基础设施层 ===
    crawler = providers.Factory(
        CtripTicketCrawler,
        timeout=config.provided.crawler_timeout,
    )

    analyzer = providers.Factory(
        DeepSeekAnalyzer,
        api_key=config.provided.deepseek_api_key,
        base_url=config.provided.deepseek_base_url,
        model=config.provided.deepseek_model,
    )

    notifier = providers.Factory(
        EmailNotifier,
        smtp_host=config.provided.smtp_host,
        smtp_port=config.provided.smtp_port,
        smtp_user=config.provided.smtp_user,
        smtp_password=config.provided.smtp_password,
        from_addr=config.provided.email_from,
        to_addrs=config.provided.email_to,
    )

    scheduler = providers.Singleton(APSchedulerWrapper)

    # === 应用层 ===
    ticket_service = providers.Factory(
        TicketMonitorService,
        crawler=crawler,
        analyzer=analyzer,
        notifier=notifier,
    )
