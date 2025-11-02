"""Pytest configuration and fixtures"""

from unittest.mock import Mock

import pytest

from src.domain.interfaces import INotifier, ITicketAnalyzer, ITicketCrawler
from tests.fixtures.mock_data import mock_analysis, mock_query_result


@pytest.fixture
def mock_crawler() -> Mock:
    """创建模拟爬虫"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.return_value = mock_query_result(has_tickets=True)
    return crawler


@pytest.fixture
def mock_crawler_no_tickets() -> Mock:
    """创建模拟爬虫（无票）"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.return_value = mock_query_result(has_tickets=False)
    return crawler


@pytest.fixture
def mock_crawler_with_retry() -> Mock:
    """创建模拟爬虫（需要重试）"""
    crawler = Mock(spec=ITicketCrawler)
    # 前2次无票，第3次有票
    crawler.fetch_tickets.side_effect = [
        mock_query_result(has_tickets=False),
        mock_query_result(has_tickets=False),
        mock_query_result(has_tickets=True),
    ]
    return crawler


@pytest.fixture
def mock_crawler_failure() -> Mock:
    """创建模拟爬虫（总是失败）"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.side_effect = Exception("Network error")
    return crawler


@pytest.fixture
def mock_analyzer() -> Mock:
    """创建模拟分析器"""
    analyzer = Mock(spec=ITicketAnalyzer)
    analyzer.analyze.return_value = mock_analysis(has_ticket=True)
    return analyzer


@pytest.fixture
def mock_notifier() -> Mock:
    """创建模拟通知器"""
    notifier = Mock(spec=INotifier)
    notifier.send.return_value = None
    return notifier


@pytest.fixture
def mock_scheduler() -> Mock:
    """创建模拟调度器"""
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = Mock(spec=BlockingScheduler)
    return scheduler

