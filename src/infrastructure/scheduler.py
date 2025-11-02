"""APScheduler implementation"""

from collections.abc import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class APSchedulerWrapper:
    """APScheduler wrapper, implements IScheduler interface"""

    def __init__(self) -> None:
        self._scheduler = BlockingScheduler()

    def schedule_weekly_job(
        self,
        day_of_week: int,
        hour: int,
        minute: int,
        job_func: Callable,
    ) -> None:
        """
        Schedule weekly job

        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour
            minute: Minute
            job_func: Job function to execute
        """
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
        )

        self._scheduler.add_job(
            job_func,
            trigger=trigger,
            id=f"weekly_job_{day_of_week}_{hour}_{minute}",
        )

        logger.info(f"Scheduled weekly job: day_of_week={day_of_week}, time={hour:02d}:{minute:02d}")

    def schedule_multiple_weekly_jobs(
        self,
        days_of_week: list[int],
        hour: int,
        minute: int,
        job_func: Callable,
    ) -> None:
        """
        Schedule multiple weekly jobs

        Args:
            days_of_week: List of days of week (0=Monday, 6=Sunday)
            hour: Hour
            minute: Minute
            job_func: Job function to execute
        """
        for day in days_of_week:
            self.schedule_weekly_job(
                day_of_week=day,
                hour=hour,
                minute=minute,
                job_func=job_func,
            )

        logger.info(f"Scheduled {len(days_of_week)} weekly job(s): days={days_of_week}, time={hour:02d}:{minute:02d}")

    def start(self) -> None:
        """Start scheduler"""
        logger.info("Starting scheduler...")
        self._scheduler.start()

    def shutdown(self) -> None:
        """Shutdown scheduler"""
        logger.info("Shutting down scheduler...")
        self._scheduler.shutdown()
