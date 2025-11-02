"""Unit tests for TicketMonitorService"""

import time
from unittest.mock import Mock, patch

import pytest

from src.application.ticket_service import TicketMonitorService
from src.domain.exceptions import DomainException
from tests.fixtures.mock_data import mock_query_result


class TestTicketMonitorService:
    """测试票务监控服务"""

    def test_monitor_ticket_success(self, mock_crawler, mock_analyzer, mock_notifier):
        """测试成功监控场景"""
        service = TicketMonitorService(
            crawler=mock_crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        # 执行监控
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # 验证调用
        assert mock_crawler.fetch_tickets.call_count == 1
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_with_retry_success(self, mock_crawler_with_retry, mock_analyzer, mock_notifier):
        """测试重试机制 - 第3次成功"""
        service = TicketMonitorService(
            crawler=mock_crawler_with_retry,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=5,
        )

        # 执行监控
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # 验证重试了3次
        assert mock_crawler_with_retry.fetch_tickets.call_count == 3
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_all_retries_no_tickets(self, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """测试所有重试都无票的场景"""
        service = TicketMonitorService(
            crawler=mock_crawler_no_tickets,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=3,
        )

        # 执行监控
        service.monitor_ticket(
            departure_station="大邑",
            arrival_station="成都南",
            train_number="C3380",
            days_ahead=15,
        )

        # 验证重试了3次（最大次数）
        assert mock_crawler_no_tickets.fetch_tickets.call_count == 3
        # 即使无票，也应该继续分析和通知
        assert mock_analyzer.analyze.call_count == 1
        assert mock_notifier.send.call_count == 1

    def test_monitor_ticket_crawler_failure(self, mock_crawler_failure, mock_analyzer, mock_notifier):
        """测试爬虫失败场景"""
        service = TicketMonitorService(
            crawler=mock_crawler_failure,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
            max_retries=3,
        )

        # 应该抛出异常
        with pytest.raises(DomainException) as exc_info:
            service.monitor_ticket(
                departure_station="大邑",
                arrival_station="成都南",
                train_number="C3380",
                days_ahead=15,
            )

        assert "Failed to fetch tickets after 3 attempts" in str(exc_info.value)
        # 验证重试了3次
        assert mock_crawler_failure.fetch_tickets.call_count == 3
        # 失败后不应该调用分析和通知
        assert mock_analyzer.analyze.call_count == 0
        assert mock_notifier.send.call_count == 0

    @patch("time.sleep")  # Mock sleep 以加速测试
    def test_fibonacci_backoff_timing(self, mock_sleep, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """测试斐波那契退避时间"""
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

        # 验证斐波那契数列: 1, 1, 2, 3 (共4次等待，因为第5次是最后一次不需要等待)
        expected_waits = [1, 1, 2, 3]
        actual_waits = [call.args[0] for call in mock_sleep.call_args_list]
        assert actual_waits == expected_waits

    def test_calculate_target_date(self, mock_crawler, mock_analyzer, mock_notifier):
        """测试目标日期计算"""
        service = TicketMonitorService(
            crawler=mock_crawler,
            analyzer=mock_analyzer,
            notifier=mock_notifier,
        )

        # 测试计算第15天
        target_date = service._calculate_target_date(days_ahead=15)

        # 验证返回格式
        assert isinstance(target_date, str)
        assert len(target_date) == 10  # YYYY-MM-DD
        assert target_date.count("-") == 2

    def test_max_retries_configuration(self, mock_crawler, mock_analyzer, mock_notifier):
        """测试max_retries配置"""
        # 测试不同的重试次数
        for max_retries in [1, 3, 5, 10]:
            service = TicketMonitorService(
                crawler=mock_crawler,
                analyzer=mock_analyzer,
                notifier=mock_notifier,
                max_retries=max_retries,
            )
            assert service._max_retries == max_retries


class TestFetchWithRetry:
    """专门测试重试机制"""

    @patch("time.sleep")
    def test_retry_with_incremental_backoff(self, mock_sleep, mock_crawler_no_tickets, mock_analyzer, mock_notifier):
        """测试增量退避"""
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

        # 斐波那契数列: 1, 1, 2, 3, 5 (第6次是最后一次，不等待)
        expected_waits = [1, 1, 2, 3, 5]
        actual_waits = [call.args[0] for call in mock_sleep.call_args_list]
        assert actual_waits == expected_waits

    def test_retry_stops_on_success(self, mock_analyzer, mock_notifier):
        """测试成功后立即停止重试"""
        crawler = Mock()
        # 第2次成功
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

        # 只应该调用2次，不应该继续重试
        assert crawler.fetch_tickets.call_count == 2

    @patch("time.sleep")
    def test_retry_with_exception(self, mock_sleep, mock_analyzer, mock_notifier):
        """测试异常时的重试行为"""
        crawler = Mock()
        # 前2次异常，第3次成功
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

        # 应该重试3次
        assert crawler.fetch_tickets.call_count == 3
        # 验证等待时间: 1秒, 1秒
        assert mock_sleep.call_count == 2

