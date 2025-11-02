#!/usr/bin/env python3
"""Main entry point for Early Bird Train"""

import sys
from pathlib import Path

from loguru import logger

from src.container import Container
from src.domain.exceptions import DomainException


def setup_logging(log_level: str) -> None:
    """Configure logging"""
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File output
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="00:00",  # Rotate at midnight daily
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
    )


def run_once(container: Container) -> None:
    """Run monitoring task once (for testing)"""
    logger.info("Running ticket monitoring once...")

    config = container.config()
    service = container.ticket_service()

    service.monitor_ticket(
        departure_station=config.departure_station,
        arrival_station=config.arrival_station,
        train_number=config.train_number,
        days_ahead=config.days_ahead,
    )


def run_scheduler(container: Container) -> None:
    """Start scheduled task scheduler"""
    logger.info("Starting scheduled monitoring...")

    config = container.config()
    scheduler = container.scheduler()

    # Create scheduled job
    def job():
        try:
            run_once(container)
        except DomainException as e:
            logger.error(f"Monitoring job failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in monitoring job: {e}")

    # Schedule multiple weekly jobs
    scheduler.schedule_multiple_weekly_jobs(
        days_of_week=config.schedule_days_of_week,
        hour=config.schedule_hour,
        minute=config.schedule_minute,
        job_func=job,
    )

    # Format day names
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    scheduled_days = ", ".join([day_names[d] for d in config.schedule_days_of_week])

    logger.info(
        f"Scheduled to run on {scheduled_days} "
        f"at {config.schedule_hour:02d}:{config.schedule_minute:02d} "
        f"(max_retries={config.max_retries})"
    )

    # Start scheduler (blocking)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received shutdown signal")
        scheduler.shutdown()


def main() -> int:
    """Main entry point"""
    try:
        # Create container
        container = Container()
        config = container.config()

        # Configure logging
        setup_logging(config.log_level)

        logger.info(f"Starting {config.app_name}...")
        logger.info(f"Monitoring: {config.train_number} ({config.departure_station} -> {config.arrival_station})")

        # Determine running mode based on command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            run_once(container)
        else:
            run_scheduler(container)

        return 0

    except DomainException as e:
        logger.error(f"Application error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
