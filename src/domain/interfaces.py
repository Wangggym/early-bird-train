"""Domain interfaces (Abstract Base Classes)"""

from abc import ABC, abstractmethod
from typing import Protocol

from src.domain.models import AnalysisResult, TicketQuery, TicketQueryResult


class ITicketCrawler(ABC):
    """车票爬虫接口"""

    @abstractmethod
    def fetch_tickets(self, query: TicketQuery) -> TicketQueryResult:
        """
        获取车票信息

        Args:
            query: 查询条件

        Returns:
            查询结果

        Raises:
            CrawlerException: 爬取失败时抛出
        """
        pass


class ITicketAnalyzer(ABC):
    """车票分析器接口"""

    @abstractmethod
    def analyze(self, result: TicketQueryResult) -> AnalysisResult:
        """
        分析车票数据

        Args:
            result: 查询结果

        Returns:
            分析结果

        Raises:
            AnalyzerException: 分析失败时抛出
        """
        pass


class INotifier(ABC):
    """通知器接口"""

    @abstractmethod
    def send(self, analysis: AnalysisResult) -> None:
        """
        发送通知

        Args:
            analysis: 分析结果

        Raises:
            NotifierException: 发送失败时抛出
        """
        pass


class IScheduler(Protocol):
    """调度器接口（使用Protocol实现结构化类型）"""

    def schedule_weekly_job(
        self,
        day_of_week: int,
        hour: int,
        minute: int,
        job_func: callable,
    ) -> None:
        """
        安排每周定时任务

        Args:
            day_of_week: 星期几（0=Monday, 6=Sunday）
            hour: 小时
            minute: 分钟
            job_func: 要执行的任务函数
        """
        ...

    def start(self) -> None:
        """启动调度器"""
        ...

    def shutdown(self) -> None:
        """关闭调度器"""
        ...
