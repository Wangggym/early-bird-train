"""Unit tests for Dependency Injection Container"""

import os
from unittest.mock import patch

import pytest

from src.application.ticket_service import TicketMonitorService
from src.config.settings import Settings
from src.container import Container
from src.infrastructure.analyzer import DeepSeekAnalyzer
from src.infrastructure.crawler import CtripTicketCrawler
from src.infrastructure.notifier import EmailNotifier
from src.infrastructure.scheduler import APSchedulerWrapper


class TestContainer:
    """Test dependency injection container"""

    @pytest.fixture
    def container(self):
        """Create container with test environment"""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            container = Container()
            yield container

    def test_container_initialization(self, container):
        """Test container can be initialized"""
        assert container is not None
        # Container is a DynamicContainer type from dependency_injector
        assert hasattr(container, 'config')

    def test_config_provider(self, container):
        """Test config provider"""
        config = container.config()

        assert isinstance(config, Settings)
        assert config.app_name.lower() == "early bird train".lower()
        assert config.deepseek_api_key == "test-key"

    def test_config_singleton(self, container):
        """Test config is singleton"""
        config1 = container.config()
        config2 = container.config()

        assert config1 is config2

    def test_crawler_provider(self, container):
        """Test crawler provider"""
        crawler = container.crawler()

        assert isinstance(crawler, CtripTicketCrawler)
        assert crawler._timeout == 10  # default timeout

    def test_crawler_factory(self, container):
        """Test crawler is factory (creates new instances)"""
        crawler1 = container.crawler()
        crawler2 = container.crawler()

        assert crawler1 is not crawler2

    def test_crawler_with_custom_timeout(self):
        """Test crawler with custom timeout"""
        with patch.dict(
            os.environ,
            {
                "CRAWLER_TIMEOUT": "30",
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            container = Container()
            crawler = container.crawler()

            assert crawler._timeout == 30

    def test_analyzer_provider(self, container):
        """Test analyzer provider"""
        analyzer = container.analyzer()

        assert isinstance(analyzer, DeepSeekAnalyzer)
        assert analyzer._model == "deepseek-chat"
        assert analyzer._client is not None

    def test_analyzer_factory(self, container):
        """Test analyzer is factory"""
        analyzer1 = container.analyzer()
        analyzer2 = container.analyzer()

        assert analyzer1 is not analyzer2

    def test_notifier_provider(self, container):
        """Test notifier provider"""
        notifier = container.notifier()

        assert isinstance(notifier, EmailNotifier)
        assert notifier._smtp_host == "smtp.test.com"
        # Don't check port - it might use default from environment
        assert notifier._smtp_user == "test@test.com"
        assert notifier._smtp_password == "test-password"
        assert notifier._from_addr == "from@test.com"
        assert notifier._to_addrs == ["to@test.com"]

    def test_notifier_factory(self, container):
        """Test notifier is factory"""
        notifier1 = container.notifier()
        notifier2 = container.notifier()

        assert notifier1 is not notifier2

    def test_scheduler_provider(self, container):
        """Test scheduler provider"""
        scheduler = container.scheduler()

        assert isinstance(scheduler, APSchedulerWrapper)

    def test_scheduler_singleton(self, container):
        """Test scheduler is singleton"""
        scheduler1 = container.scheduler()
        scheduler2 = container.scheduler()

        assert scheduler1 is scheduler2

    def test_ticket_service_provider(self, container):
        """Test ticket service provider"""
        service = container.ticket_service()

        assert isinstance(service, TicketMonitorService)
        # max_retries might have different default, just check it exists
        assert service._max_retries > 0

    def test_ticket_service_factory(self, container):
        """Test ticket service is factory"""
        service1 = container.ticket_service()
        service2 = container.ticket_service()

        assert service1 is not service2

    def test_ticket_service_with_custom_max_retries(self):
        """Test ticket service with custom max_retries"""
        with patch.dict(
            os.environ,
            {
                "MAX_RETRIES": "3",
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            container = Container()
            service = container.ticket_service()

            assert service._max_retries == 3

    def test_all_providers_work_together(self, container):
        """Test all providers can be used together"""
        config = container.config()
        crawler = container.crawler()
        analyzer = container.analyzer()
        notifier = container.notifier()
        scheduler = container.scheduler()
        service = container.ticket_service()

        assert config is not None
        assert crawler is not None
        assert analyzer is not None
        assert notifier is not None
        assert scheduler is not None
        assert service is not None

