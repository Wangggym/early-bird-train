#!/usr/bin/env python3
"""Main entry point for Early Bird Train"""

import sys
from pathlib import Path

from loguru import logger

from src.container import Container
from src.domain.exceptions import DomainException


def setup_logging(log_level: str) -> None:
    """配置日志"""
    logger.remove()  # 移除默认handler

    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # 文件输出
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
    )


def run_once(container: Container) -> None:
    """运行一次监控任务（用于测试）"""
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
    """启动定时调度器"""
    logger.info("Starting scheduled monitoring...")

    config = container.config()
    scheduler = container.scheduler()

    # 创建定时任务
    def job():
        try:
            run_once(container)
        except DomainException as e:
            logger.error(f"Monitoring job failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in monitoring job: {e}")

    # 安排多个每周定时任务
    scheduler.schedule_multiple_weekly_jobs(
        days_of_week=config.schedule_days_of_week,
        hour=config.schedule_hour,
        minute=config.schedule_minute,
        job_func=job,
    )

    # 格式化日期名称
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_names_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    scheduled_days = ", ".join([day_names_cn[d] for d in config.schedule_days_of_week])

    logger.info(
        f"Scheduled to run on {scheduled_days} "
        f"at {config.schedule_hour:02d}:{config.schedule_minute:02d} "
        f"(max_retries={config.max_retries})"
    )

    # 启动调度器（阻塞运行）
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received shutdown signal")
        scheduler.shutdown()


def main() -> int:
    """主函数"""
    try:
        # 创建容器
        container = Container()
        config = container.config()

        # 配置日志
        setup_logging(config.log_level)

        logger.info(f"Starting {config.app_name}...")
        logger.info(f"Monitoring: {config.train_number} ({config.departure_station} -> {config.arrival_station})")

        # 根据命令行参数决定运行模式
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
