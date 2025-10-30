"""APScheduler implementation"""

from collections.abc import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class APSchedulerWrapper:
    """APScheduler包装器，实现IScheduler接口"""

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
        安排每周定时任务

        Args:
            day_of_week: 星期几（0=Monday, 6=Sunday）
            hour: 小时
            minute: 分钟
            job_func: 要执行的任务函数
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

    def start(self) -> None:
        """启动调度器"""
        logger.info("Starting scheduler...")
        self._scheduler.start()

    def shutdown(self) -> None:
        """关闭调度器"""
        logger.info("Shutting down scheduler...")
        self._scheduler.shutdown()
