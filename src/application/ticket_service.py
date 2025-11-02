"""Ticket monitoring service (Application Use Case)"""

import time
from datetime import datetime, timedelta

from loguru import logger

from src.domain.exceptions import DomainException
from src.domain.interfaces import INotifier, ITicketAnalyzer, ITicketCrawler
from src.domain.models import TicketQuery


class TicketMonitorService:
    """Ticket monitoring service (Application layer)"""

    def __init__(
        self,
        crawler: ITicketCrawler,
        analyzer: ITicketAnalyzer,
        notifier: INotifier,
        max_retries: int = 5,
    ) -> None:
        """
        Initialize service (dependency injection)

        Args:
            crawler: Crawler interface implementation
            analyzer: Analyzer interface implementation
            notifier: Notifier interface implementation
            max_retries: Maximum retry attempts (default: 5)
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
        Monitor tickets (core use case) - Supports Fibonacci backoff retry

        Args:
            departure_station: Departure station
            arrival_station: Arrival station
            train_number: Train number
            days_ahead: Days ahead to query
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
            # 1. Calculate target date
            target_date = self._calculate_target_date(days_ahead)

            logger.info(f"Target date: {target_date}")

            # 2. Build query
            query = TicketQuery(
                departure_station=departure_station,
                arrival_station=arrival_station,
                departure_date=target_date,
                train_number=train_number,
            )

            # 3. Fetch ticket data with retry
            result = self._fetch_with_retry(query)

            # 4. AI analysis
            analysis = self._analyzer.analyze(result)

            logger.info(f"Analysis complete: has_ticket={analysis.has_ticket}, has_seated={analysis.has_seated_ticket}")

            # 5. Send notification (only when tickets are available)
            if analysis.has_ticket:
                logger.info("Found tickets! Sending notification...")
                self._notifier.send(analysis)
                logger.info("Notification sent successfully")
            else:
                logger.info("No tickets available, skipping notification")

            logger.info("Ticket monitoring completed successfully")

        except Exception as e:
            logger.error(f"Ticket monitoring failed: {e}")
            # Can add failure notification here
            raise

    def _fetch_with_retry(self, query: TicketQuery):
        """
        Retry fetching ticket data with Fibonacci backoff strategy

        Args:
            query: Ticket query object

        Returns:
            Ticket query result

        Raises:
            DomainException: Raised after all retries fail
        """
        fib_a, fib_b = 1, 1  # Fibonacci sequence initial values

        for attempt in range(1, self._max_retries + 1):
            try:
                logger.info(f"Fetching tickets (attempt {attempt}/{self._max_retries})...")
                result = self._crawler.fetch_tickets(query)

                # Check if trains found
                if result.trains:
                    logger.info(f"Successfully fetched {len(result.trains)} train(s)")
                    return result
                else:
                    logger.warning(f"No trains found (attempt {attempt}/{self._max_retries})")

                    # Use Fibonacci backoff if not last attempt
                    if attempt < self._max_retries:
                        wait_time = fib_a
                        logger.info(f"Waiting {wait_time}s before retry (Fibonacci backoff)...")
                        time.sleep(wait_time)

                        # Update Fibonacci sequence
                        fib_a, fib_b = fib_b, fib_a + fib_b

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")

                # Use Fibonacci backoff if not last attempt
                if attempt < self._max_retries:
                    wait_time = fib_a
                    logger.info(f"Waiting {wait_time}s before retry (Fibonacci backoff)...")
                    time.sleep(wait_time)

                    # Update Fibonacci sequence
                    fib_a, fib_b = fib_b, fib_a + fib_b
                else:
                    # Last attempt failed, raise exception
                    raise DomainException(f"Failed to fetch tickets after {self._max_retries} attempts") from e

        # All attempts found no tickets, return empty result
        logger.warning(f"No tickets found after {self._max_retries} attempts")
        return result

    def _calculate_target_date(self, days_ahead: int) -> str:
        """
        Calculate target date

        Args:
            days_ahead: Days ahead (Nth day from today, today is day 1)

        Returns:
            Date string (YYYY-MM-DD)
        """
        today = datetime.now().date()
        # days_ahead means "the Nth day", so actually today + (N-1) days
        # Example: today is day 1, day 15 = today + 14 days
        target = today + timedelta(days=days_ahead - 1)

        logger.info(f"Calculated target (day {days_ahead}): {target.strftime('%Y-%m-%d (%A)')}")

        return target.strftime("%Y-%m-%d")
