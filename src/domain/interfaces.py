"""Domain interfaces (Abstract Base Classes)"""

from abc import ABC, abstractmethod
from typing import Protocol

from src.domain.models import AnalysisResult, TicketQuery, TicketQueryResult


class ITicketCrawler(ABC):
    """Ticket crawler interface"""

    @abstractmethod
    def fetch_tickets(self, query: TicketQuery) -> TicketQueryResult:
        """
        Fetch ticket information

        Args:
            query: Query conditions

        Returns:
            Query result

        Raises:
            CrawlerException: Raised when crawling fails
        """
        pass


class ITicketAnalyzer(ABC):
    """Ticket analyzer interface"""

    @abstractmethod
    def analyze(self, result: TicketQueryResult) -> AnalysisResult:
        """
        Analyze ticket data

        Args:
            result: Query result

        Returns:
            Analysis result

        Raises:
            AnalyzerException: Raised when analysis fails
        """
        pass


class INotifier(ABC):
    """Notifier interface"""

    @abstractmethod
    def send(self, analysis: AnalysisResult) -> None:
        """
        Send notification

        Args:
            analysis: Analysis result

        Raises:
            NotifierException: Raised when sending fails
        """
        pass


class IScheduler(Protocol):
    """Scheduler interface (using Protocol for structural typing)"""

    def schedule_weekly_job(
        self,
        day_of_week: int,
        hour: int,
        minute: int,
        job_func: callable,
    ) -> None:
        """
        Schedule weekly job

        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour
            minute: Minute
            job_func: Job function to execute
        """
        ...

    def start(self) -> None:
        """Start scheduler"""
        ...

    def shutdown(self) -> None:
        """Shutdown scheduler"""
        ...
