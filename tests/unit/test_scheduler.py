"""Unit tests for APSchedulerWrapper"""

from unittest.mock import Mock, patch

import pytest
from apscheduler.triggers.cron import CronTrigger

from src.infrastructure.scheduler import APSchedulerWrapper


class TestAPSchedulerWrapper:
    """测试调度器"""

    def test_schedule_weekly_job_single_day(self):
        """测试单日期调度"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        scheduler.schedule_weekly_job(
            day_of_week=0,  # 周一
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # 验证任务已添加
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1

        # 验证任务配置
        job = jobs[0]
        assert job.id == "weekly_job_0_15_30"
        assert isinstance(job.trigger, CronTrigger)

    def test_schedule_multiple_weekly_jobs(self):
        """测试多日期调度"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 调度周一、周三、周五
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 2, 4],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # 验证创建了3个任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 3

        # 验证任务ID
        job_ids = [job.id for job in jobs]
        assert "weekly_job_0_15_30" in job_ids
        assert "weekly_job_2_15_30" in job_ids
        assert "weekly_job_4_15_30" in job_ids

    def test_schedule_multiple_jobs_all_weekdays(self):
        """测试工作日全覆盖调度"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 调度周一到周五
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 1, 2, 3, 4],
            hour=9,
            minute=0,
            job_func=job_func,
        )

        # 验证创建了5个任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 5

    def test_schedule_with_different_times(self):
        """测试不同时间的调度"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 不同时间点
        test_cases = [
            (0, 0),    # 午夜
            (12, 0),   # 中午
            (15, 30),  # 下午3:30
            (23, 59),  # 深夜
        ]

        for hour, minute in test_cases:
            scheduler.schedule_weekly_job(
                day_of_week=0,
                hour=hour,
                minute=minute,
                job_func=job_func,
            )

        # 验证所有任务都已创建
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == len(test_cases)

    def test_schedule_weekend(self):
        """测试周末调度"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 调度周六和周日
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[5, 6],
            hour=20,
            minute=0,
            job_func=job_func,
        )

        # 验证创建了2个任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 2

        job_ids = [job.id for job in jobs]
        assert "weekly_job_5_20_0" in job_ids
        assert "weekly_job_6_20_0" in job_ids

    def test_multiple_calls_create_separate_jobs(self):
        """测试多次调用创建独立任务"""
        scheduler = APSchedulerWrapper()

        job_func1 = Mock()
        job_func2 = Mock()

        # 第一次调度
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 2],
            hour=9,
            minute=0,
            job_func=job_func1,
        )

        # 第二次调度（不同时间）
        scheduler.schedule_weekly_job(
            day_of_week=4,
            hour=17,
            minute=30,
            job_func=job_func2,
        )

        # 验证总共创建了3个任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 3

    def test_empty_days_list(self):
        """测试空日期列表"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 空列表
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # 不应该创建任何任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 0

    def test_single_day_in_list(self):
        """测试单日期列表（与单日期方法等价）"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # 使用列表传入单个日期
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # 应该只创建1个任务
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "weekly_job_0_15_30"


class TestSchedulerIntegration:
    """调度器集成测试"""

    def test_job_execution_mock(self):
        """测试任务执行（使用Mock）"""
        scheduler = APSchedulerWrapper()

        # 创建可追踪的函数
        executed = []

        def test_job():
            executed.append(True)

        scheduler.schedule_weekly_job(
            day_of_week=0,
            hour=15,
            minute=30,
            job_func=test_job,
        )

        # 获取任务并手动触发
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1

        # 手动调用函数（模拟调度器触发）
        test_job()
        assert len(executed) == 1

    def test_cron_trigger_configuration(self):
        """测试CronTrigger配置"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        scheduler.schedule_weekly_job(
            day_of_week=3,  # 周四
            hour=10,
            minute=15,
            job_func=job_func,
        )

        jobs = scheduler._scheduler.get_jobs()
        job = jobs[0]
        trigger = job.trigger

        # 验证触发器类型
        assert isinstance(trigger, CronTrigger)

        # 验证触发器字段
        assert trigger.fields[4].expressions[0].first == 3  # day_of_week
        assert trigger.fields[5].expressions[0].first == 10  # hour
        assert trigger.fields[6].expressions[0].first == 15  # minute

