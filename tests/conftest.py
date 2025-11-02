"""Pytest configuration and fixtures"""

from unittest.mock import Mock

import pytest

from src.domain.interfaces import INotifier, ITicketAnalyzer, ITicketCrawler
from tests.fixtures.mock_data import mock_analysis, mock_query_result


@pytest.fixture
def mock_crawler() -> Mock:
    """Create mock crawler"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.return_value = mock_query_result(has_tickets=True)
    return crawler


@pytest.fixture
def mock_crawler_no_tickets() -> Mock:
    """Create mock crawler (no tickets)"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.return_value = mock_query_result(has_tickets=False)
    return crawler


@pytest.fixture
def mock_crawler_with_retry() -> Mock:
    """Create mock crawler (requires retry)"""
    crawler = Mock(spec=ITicketCrawler)
    # First 2 attempts return no tickets, 3rd attempt returns tickets
    crawler.fetch_tickets.side_effect = [
        mock_query_result(has_tickets=False),
        mock_query_result(has_tickets=False),
        mock_query_result(has_tickets=True),
    ]
    return crawler


@pytest.fixture
def mock_crawler_failure() -> Mock:
    """Create mock crawler (always fails)"""
    crawler = Mock(spec=ITicketCrawler)
    crawler.fetch_tickets.side_effect = Exception("Network error")
    return crawler


@pytest.fixture
def mock_analyzer() -> Mock:
    """Create mock analyzer"""
    analyzer = Mock(spec=ITicketAnalyzer)
    analyzer.analyze.return_value = mock_analysis(has_ticket=True)
    return analyzer


@pytest.fixture
def mock_notifier() -> Mock:
    """Create mock notifier"""
    notifier = Mock(spec=INotifier)
    notifier.send.return_value = None
    return notifier


@pytest.fixture
def mock_scheduler() -> Mock:
    """Create mock scheduler"""
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = Mock(spec=BlockingScheduler)
    return scheduler

