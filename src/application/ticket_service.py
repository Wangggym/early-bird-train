"""Ticket monitoring service (Application Use Case)"""

import time
from datetime import datetime, timedelta

from loguru import logger

from src.domain.exceptions import DomainException
from src.domain.interfaces import INotifier, ITicketAnalyzer, ITicketCrawler
from src.domain.models import TicketQuery


class TicketMonitorService:
    """车票监控服务（应用层）"""

    def __init__(
        self,
        crawler: ITicketCrawler,
        analyzer: ITicketAnalyzer,
        notifier: INotifier,
        max_retries: int = 5,
    ) -> None:
        """
        初始化服务（依赖注入）

        Args:
            crawler: 爬虫接口实现
            analyzer: 分析器接口实现
            notifier: 通知器接口实现
            max_retries: 最大重试次数（默认5次）
        """
        self._crawler = crawler
        self._analyzer = analyzer
        self._notifier = notifier
        self._max_retries = max_retries

    def monitor_ticket(
        self,
        departure_station: str,
        arrival_station: str,
        train_number: str,
        days_ahead: int = 15,
    ) -> None:
        """
        监控车票（核心用例）- 支持斐波那契退避重试

        Args:
            departure_station: 出发站
            arrival_station: 到达站
            train_number: 车次号
            days_ahead: 提前天数
        """
        from datetime import datetime
        
        today = datetime.now().date()
        logger.info(
            f"Starting ticket monitoring: {train_number}, "
            f"{departure_station} -> {arrival_station}, "
            f"{days_ahead} days ahead"
        )
        logger.info(f"Today: {today.strftime('%Y-%m-%d (%A)')}")

        try:
            # 1. 计算目标日期
            target_date = self._calculate_target_date(days_ahead)

            logger.info(f"Target date: {target_date}")

            # 2. 构建查询
            query = TicketQuery(
                departure_station=departure_station,
                arrival_station=arrival_station,
                departure_date=target_date,
                train_number=train_number,
            )

            # 3. 带重试的爬取车票数据
            result = self._fetch_with_retry(query)

            # 4. AI分析
            analysis = self._analyzer.analyze(result)

            logger.info(f"Analysis complete: has_ticket={analysis.has_ticket}, has_seated={analysis.has_seated_ticket}")

            # 5. 发送通知（仅在有票时）
            if analysis.has_ticket:
                logger.info("Found tickets! Sending notification...")
                self._notifier.send(analysis)
                logger.info("Notification sent successfully")
            else:
                logger.info("No tickets available, skipping notification")

            logger.info("Ticket monitoring completed successfully")

        except Exception as e:
            logger.error(f"Ticket monitoring failed: {e}")
            # 这里可以添加失败通知
            raise

    def _fetch_with_retry(self, query: TicketQuery):
        """
        使用斐波那契退避策略重试抓取票务数据

        Args:
            query: 票务查询对象

        Returns:
            票务查询结果

        Raises:
            DomainException: 所有重试失败后抛出
        """
        fib_a, fib_b = 1, 1  # 斐波那契数列初始值

        for attempt in range(1, self._max_retries + 1):
            try:
                logger.info(f"Fetching tickets (attempt {attempt}/{self._max_retries})...")
                result = self._crawler.fetch_tickets(query)

                # 检查是否有车次
                if result.trains:
                    logger.info(f"Successfully fetched {len(result.trains)} train(s)")
                    return result
                else:
                    logger.warning(f"No trains found (attempt {attempt}/{self._max_retries})")

                    # 如果不是最后一次尝试，使用斐波那契退避
                    if attempt < self._max_retries:
                        wait_time = fib_a
                        logger.info(f"Waiting {wait_time}s before retry (Fibonacci backoff)...")
                        time.sleep(wait_time)

                        # 更新斐波那契数列
                        fib_a, fib_b = fib_b, fib_a + fib_b

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")

                # 如果不是最后一次尝试，使用斐波那契退避
                if attempt < self._max_retries:
                    wait_time = fib_a
                    logger.info(f"Waiting {wait_time}s before retry (Fibonacci backoff)...")
                    time.sleep(wait_time)

                    # 更新斐波那契数列
                    fib_a, fib_b = fib_b, fib_a + fib_b
                else:
                    # 最后一次尝试失败，抛出异常
                    raise DomainException(f"Failed to fetch tickets after {self._max_retries} attempts") from e

        # 所有尝试都没有找到票，返回空结果
        logger.warning(f"No tickets found after {self._max_retries} attempts")
        return result

    def _calculate_target_date(self, days_ahead: int) -> str:
        """
        计算目标日期

        Args:
            days_ahead: 提前天数（从今天算起的第N天，今天算第1天）

        Returns:
            日期字符串 (YYYY-MM-DD)
        """
        today = datetime.now().date()
        # days_ahead表示"第N天"，所以实际是今天 + (N-1)天
        # 例如：今天是第1天，第15天 = 今天 + 14天
        target = today + timedelta(days=days_ahead - 1)
        
        logger.info(f"Calculated target (day {days_ahead}): {target.strftime('%Y-%m-%d (%A)')}")
        
        return target.strftime("%Y-%m-%d")
