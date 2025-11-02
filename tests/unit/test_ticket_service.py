"""Unit tests for TicketMonitorService"""

import time
from unittest.mock import Mock, patch

import pytest

from src.application.ticket_service import TicketMonitorService
from src.domain.exceptions import DomainException
from tests.fixtures.mock_data import mock_query_result


class TestTicketMonitorService:
    """Test ticket monitoring service"""

    def test_monitor_ticket_success(self, mock_crawler, mock_analyzer, mock_notifier):
        """Test successful monitoring scenario"""
        service = TicketMonitorService(
            crawler=mock_crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        # Execute monitoring
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Verify calls
        assert mock_crawler.fetch_tickets.call_count == 1
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_with_retry_success(self, mock_crawler_with_retry, mock_analyzer, mock_notifier):
        """Test retry mechanism - succeeds on 3rd attempt"""
        service = TicketMonitorService(
            crawler=mock_crawler_with_retry,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        # Execute monitoring
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Verify 3 retries occurred
        assert mock_crawler_with_retry.fetch_tickets.call_count == 3
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_all_retries_no_tickets(self, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """Test scenario where all retries return no tickets"""
        service = TicketMonitorService(
            crawler=mock_crawler_no_tickets,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=3,
        )

        # Execute monitoring
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Verify 3 retries occurred (maximum count)
        assert mock_crawler_no_tickets.fetch_tickets.call_count == 3
        # Even without tickets, should continue to analyze and notify
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_crawler_failure(self, mock_crawler_failure, mock_analyzer, mock_notifier):
        """Test crawler failure scenario"""
        service = TicketMonitorService(
            crawler=mock_crawler_failure,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=3,
        )

        # Should raise exception
        with pytest.raises(DomainException) as exc_info:
            service.monitor_ticket(
                departure_station="大邑",
                arrival_station="成都南",
                train_number="C3380",
                days_ahead=15,
            )

        assert "Failed to fetch tickets after 3 attempts" in str(exc_info.value)
        # Verify 3 retries occurred
        assert mock_crawler_failure.fetch_tickets.call_count == 3
        # After failure, should not call analyzer and notifier
        assert mock_analyzer.analyze.call_count == 0
        assert mock_notifier.send.call_count == 0

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_fibonacci_backoff_timing(self, mock_sleep, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """Test Fibonacci backoff timing"""
        service = TicketMonitorService(
            crawler=mock_crawler_no_tickets,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Verify Fibonacci sequence: 1, 1, 2, 3 (4 waits total, since 5th is last attempt and doesn't need wait)
        expected_waits = [1, 1, 2, 3]
        actual_waits = [call.args[0] for call in mock_sleep.call_args_list]
        assert actual_waits == expected_waits

    def test_calculate_target_date(self, mock_crawler, mock_analyzer, mock_notifier):
        """Test target date calculation"""
        service = TicketMonitorService(
            crawler=mock_crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
        )

        # Test calculation for day 15
        target_date = service._calculate_target_date(days_ahead=15)

        # Verify return format
        assert isinstance(target_date, str)
        assert len(target_date) == 10  # YYYY-MM-DD
        assert target_date.count("-") == 2

    def test_max_retries_configuration(self, mock_crawler, mock_analyzer, mock_notifier):
        """Test max_retries configuration"""
        # Test different retry counts
        for max_retries in [1, 3, 5, 10]:
            service = TicketMonitorService(
                crawler=mock_crawler,
                analyzer=mock_analyzer,
                notifier=mock_notifier,
                max_retries=max_retries,
            )
            assert service._max_retries == max_retries


class TestFetchWithRetry:
    """Dedicated tests for retry mechanism"""

    @patch("time.sleep")
    def test_retry_with_incremental_backoff(self, mock_sleep, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """Test incremental backoff"""
        service = TicketMonitorService(
            crawler=mock_crawler_no_tickets,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=6,
        )

        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Fibonacci sequence: 1, 1, 2, 3, 5 (6th is last attempt, no wait)
        expected_waits = [1, 1, 2, 3, 5]
        actual_waits = [call.args[0] for call in mock_sleep.call_args_list]
        assert actual_waits == expected_waits

    def test_retry_stops_on_success(self, mock_analyzer, mock_notifier):
        """Test retry stops immediately on success"""
        crawler = Mock()
        # 2nd attempt succeeds
        crawler.fetch_tickets.side_effect = [
            mock_query_result(has_tickets=False),
            mock_query_result(has_tickets=True),
        ]

        service = TicketMonitorService(
            crawler=crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Should only call 2 times, should not continue retrying
        assert crawler.fetch_tickets.call_count == 2

    @patch("time.sleep")
    def test_retry_with_exception(self, mock_sleep, mock_analyzer, mock_notifier):
        """Test retry behavior on exceptions"""
        crawler = Mock()
        # First 2 attempts raise exceptions, 3rd succeeds
        crawler.fetch_tickets.side_effect = [
            Exception("Timeout"),
            Exception("Connection error"),
            mock_query_result(has_tickets=True),
        ]

        service = TicketMonitorService(
            crawler=crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # Should retry 3 times
        assert crawler.fetch_tickets.call_count == 3
        # Verify wait times: 1 second, 1 second
        assert mock_sleep.call_count == 2

