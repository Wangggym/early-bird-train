"""Ticket monitoring service (Application Use Case)"""

from datetime import datetime, timedelta

from loguru import logger

from src.domain.interfaces import INotifier, ITicketAnalyzer, ITicketCrawler
from src.domain.models import TicketQuery


class TicketMonitorService:
    """车票监控服务（应用层）"""

    def __init__(
        self,
        crawler: ITicketCrawler,
        analyzer: ITicketAnalyzer,
        notifier: INotifier,
    ) -> None:
        """
        初始化服务（依赖注入）

        Args:
            crawler: 爬虫接口实现
            analyzer: 分析器接口实现
            notifier: 通知器接口实现
        """
        self._crawler = crawler
        self._analyzer = analyzer
        self._notifier = notifier

    def monitor_ticket(
        self,
        departure_station: str,
        arrival_station: str,
        train_number: str,
        days_ahead: int = 15,
    ) -> None:
        """
        监控车票（核心用例）

        Args:
            departure_station: 出发站
            arrival_station: 到达站
            train_number: 车次号
            days_ahead: 提前天数
        """
        logger.info(
            f"Starting ticket monitoring: {train_number}, "
            f"{departure_station} -> {arrival_station}, "
            f"{days_ahead} days ahead"
        )

        try:
            # 1. 计算目标日期（15天后的周一）
            target_date = self._calculate_target_monday(days_ahead)

            logger.info(f"Target date: {target_date}")

            # 2. 构建查询
            query = TicketQuery(
                departure_station=departure_station,
                arrival_station=arrival_station,
                departure_date=target_date,
                train_number=train_number,
            )

            # 3. 爬取车票数据
            result = self._crawler.fetch_tickets(query)

            # 4. AI分析
            analysis = self._analyzer.analyze(result)

            logger.info(f"Analysis complete: has_ticket={analysis.has_ticket}, has_seated={analysis.has_seated_ticket}")

            # 5. 发送通知
            self._notifier.send(analysis)

            logger.info("Ticket monitoring completed successfully")

        except Exception as e:
            logger.error(f"Ticket monitoring failed: {e}")
            # 这里可以添加失败通知
            raise

    def _calculate_target_monday(self, days_ahead: int) -> str:
        """
        计算目标周一日期

        Args:
            days_ahead: 提前天数

        Returns:
            日期字符串 (YYYY-MM-DD)
        """
        today = datetime.now().date()
        target = today + timedelta(days=days_ahead)

        # 找到下一个周一（0=Monday）
        days_until_monday = (0 - target.weekday()) % 7
        if days_until_monday == 0 and target == today:
            days_until_monday = 7  # 如果今天是周一，找下周一

        target_monday = target + timedelta(days=days_until_monday)

        return target_monday.strftime("%Y-%m-%d")
