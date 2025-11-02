"""Unit tests for APSchedulerWrapper"""

from unittest.mock import Mock, patch

import pytest
from apscheduler.triggers.cron import CronTrigger

from src.infrastructure.scheduler import APSchedulerWrapper


class TestAPSchedulerWrapper:
    """Test scheduler"""

    def test_schedule_weekly_job_single_day(self):
        """Test single date scheduling"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        scheduler.schedule_weekly_job(
            day_of_week=0,  # Monday
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # Verify job has been added
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1

        # Verify job configuration
        job = jobs[0]
        assert job.id == "weekly_job_0_15_30"
        assert isinstance(job.trigger, CronTrigger)

    def test_schedule_multiple_weekly_jobs(self):
        """Test multiple date scheduling"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Schedule Monday, Wednesday, Friday
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 2, 4],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # Verify 3 jobs were created
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 3

        # Verify job IDs
        job_ids = [job.id for job in jobs]
        assert "weekly_job_0_15_30" in job_ids
        assert "weekly_job_2_15_30" in job_ids
        assert "weekly_job_4_15_30" in job_ids

    def test_schedule_multiple_jobs_all_weekdays(self):
        """Test full weekday coverage scheduling"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Schedule Monday to Friday
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 1, 2, 3, 4],
            hour=9,
            minute=0,
            job_func=job_func,
        )

        # Verify 5 jobs were created
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 5

    def test_schedule_with_different_times(self):
        """Test scheduling with different times"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Different time points
        test_cases = [
            (0, 0),    # Midnight
            (12, 0),   # Noon
            (15, 30),  # 3:30 PM
            (23, 59),  # Late night
        ]

        for hour, minute in test_cases:
            scheduler.schedule_weekly_job(
                day_of_week=0,
                hour=hour,
                minute=minute,
                job_func=job_func,
            )

        # Verify all jobs were created
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == len(test_cases)

    def test_schedule_weekend(self):
        """Test weekend scheduling"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Schedule Saturday and Sunday
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[5, 6],
            hour=20,
            minute=0,
            job_func=job_func,
        )

        # Verify 2 jobs were created
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 2

        job_ids = [job.id for job in jobs]
        assert "weekly_job_5_20_0" in job_ids
        assert "weekly_job_6_20_0" in job_ids

    def test_multiple_calls_create_separate_jobs(self):
        """Test multiple calls create separate jobs"""
        scheduler = APSchedulerWrapper()

        job_func1 = Mock()
        job_func2 = Mock()

        # First scheduling
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0, 2],
            hour=9,
            minute=0,
            job_func=job_func1,
        )

        # Second scheduling (different time)
        scheduler.schedule_weekly_job(
            day_of_week=4,
            hour=17,
            minute=30,
            job_func=job_func2,
        )

        # Verify 3 jobs were created in total
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 3

    def test_empty_days_list(self):
        """Test empty days list"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Empty list
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # Should not create any jobs
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 0

    def test_single_day_in_list(self):
        """Test single day in list (equivalent to single day method)"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        # Pass single date using list
        scheduler.schedule_multiple_weekly_jobs(
            days_of_week=[0],
            hour=15,
            minute=30,
            job_func=job_func,
        )

        # Should only create 1 job
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "weekly_job_0_15_30"


class TestSchedulerIntegration:
    """Scheduler integration tests"""

    def test_job_execution_mock(self):
        """Test job execution (using Mock)"""
        scheduler = APSchedulerWrapper()

        # Create traceable function
        executed = []

        def test_job():
            executed.append(True)

        scheduler.schedule_weekly_job(
            day_of_week=0,
            hour=15,
            minute=30,
            job_func=test_job,
        )

        # Get job and manually trigger
        jobs = scheduler._scheduler.get_jobs()
        assert len(jobs) == 1

        # Manually call function (simulate scheduler trigger)
        test_job()
        assert len(executed) == 1

    def test_cron_trigger_configuration(self):
        """Test CronTrigger configuration"""
        scheduler = APSchedulerWrapper()

        job_func = Mock()

        scheduler.schedule_weekly_job(
            day_of_week=3,  # Thursday
            hour=10,
            minute=15,
            job_func=job_func,
        )

        jobs = scheduler._scheduler.get_jobs()
        job = jobs[0]
        trigger = job.trigger

        # Verify trigger type
        assert isinstance(trigger, CronTrigger)

        # Verify trigger fields
        assert trigger.fields[4].expressions[0].first == 3  # day_of_week
        assert trigger.fields[5].expressions[0].first == 10  # hour
        assert trigger.fields[6].expressions[0].first == 15  # minute

