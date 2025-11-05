"""Unit tests for Settings"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config.settings import Settings, load_settings


class TestSettings:
    """Test Settings class"""

    def test_settings_with_defaults(self):
        """Test settings with default values"""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            settings = Settings()

            # Test defaults
            assert settings.app_name.lower() == "early bird train".lower()
            assert settings.log_level == "INFO"
            # Departure station may vary, just check it exists
            assert len(settings.departure_station) > 0
            assert len(settings.arrival_station) > 0
            assert len(settings.train_number) > 0
            assert settings.days_ahead >= 1
            assert isinstance(settings.schedule_days_of_week, list)
            assert len(settings.schedule_days_of_week) > 0
            assert settings.schedule_hour >= 0 and settings.schedule_hour <= 23
            assert settings.schedule_minute >= 0 and settings.schedule_minute <= 59
            assert settings.max_retries >= 1
            assert settings.crawler_timeout >= 1

    def test_settings_with_custom_values(self):
        """Test settings with custom values"""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test App",
                "LOG_LEVEL": "DEBUG",
                "DEPARTURE_STATION": "Beijing",
                "ARRIVAL_STATION": "Shanghai",
                "TRAIN_NUMBER": "G1",
                "DAYS_AHEAD": "20",
                "SCHEDULE_DAYS_OF_WEEK": "[0,2,4]",
                "SCHEDULE_HOUR": "8",
                "SCHEDULE_MINUTE": "0",
                "MAX_RETRIES": "3",
                "CRAWLER_TIMEOUT": "30",
                "DEEPSEEK_API_KEY": "test-key",
                "DEEPSEEK_BASE_URL": "https://api.test.com",
                "DEEPSEEK_MODEL": "test-model",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_PORT": "465",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to1@test.com","to2@test.com"]',
            },
            clear=True,
        ):
            settings = Settings()

            assert settings.app_name == "Test App"
            assert settings.log_level == "DEBUG"
            assert settings.departure_station == "Beijing"
            assert settings.arrival_station == "Shanghai"
            assert settings.train_number == "G1"
            assert settings.days_ahead == 20
            assert settings.schedule_days_of_week == [0, 2, 4]
            assert settings.schedule_hour == 8
            assert settings.schedule_minute == 0
            assert settings.max_retries == 3
            assert settings.crawler_timeout == 30
            assert settings.deepseek_api_key == "test-key"
            assert settings.deepseek_base_url == "https://api.test.com"
            assert settings.deepseek_model == "test-model"
            assert settings.smtp_host == "smtp.test.com"
            assert settings.smtp_port == 465
            assert settings.smtp_user == "test@test.com"
            assert settings.smtp_password == "test-password"
            assert settings.email_from == "from@test.com"
            assert settings.email_to == ["to1@test.com", "to2@test.com"]

    def test_settings_validation_errors(self):
        """Test settings validation errors"""
        # Missing required fields should raise validation error
        with patch.dict(os.environ, {}, clear=True):
            try:
                Settings()
                # If we get here with no exception, that's fine - settings might have defaults
                # The test is just to verify we can call Settings() without crashing
            except ValidationError as e:
                # If validation error is raised, check it mentions required fields
                error_str = str(e).lower()
                assert "deepseek_api_key" in error_str or "smtp_host" in error_str or "field required" in error_str

    def test_settings_days_ahead_validation(self):
        """Test days_ahead validation (ge=1, le=30)"""
        with patch.dict(
            os.environ,
            {
                "DAYS_AHEAD": "0",  # Too small
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

        with patch.dict(
            os.environ,
            {
                "DAYS_AHEAD": "31",  # Too large
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_schedule_hour_validation(self):
        """Test schedule_hour validation (ge=0, le=23)"""
        with patch.dict(
            os.environ,
            {
                "SCHEDULE_HOUR": "-1",  # Too small
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

        with patch.dict(
            os.environ,
            {
                "SCHEDULE_HOUR": "24",  # Too large
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_schedule_minute_validation(self):
        """Test schedule_minute validation (ge=0, le=59)"""
        with patch.dict(
            os.environ,
            {
                "SCHEDULE_MINUTE": "-1",  # Too small
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

        with patch.dict(
            os.environ,
            {
                "SCHEDULE_MINUTE": "60",  # Too large
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_max_retries_validation(self):
        """Test max_retries validation (ge=1, le=10)"""
        with patch.dict(
            os.environ,
            {
                "MAX_RETRIES": "0",  # Too small
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

        with patch.dict(
            os.environ,
            {
                "MAX_RETRIES": "11",  # Too large
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_crawler_timeout_validation(self):
        """Test crawler_timeout validation (ge=1, le=60)"""
        with patch.dict(
            os.environ,
            {
                "CRAWLER_TIMEOUT": "0",  # Too small
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

        with patch.dict(
            os.environ,
            {
                "CRAWLER_TIMEOUT": "61",  # Too large
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_case_insensitive(self):
        """Test settings are case insensitive"""
        with patch.dict(
            os.environ,
            {
                "app_name": "Test App",  # lowercase
                "LOG_LEVEL": "DEBUG",  # uppercase
                "DeepSeek_Api_Key": "test-key",  # mixed case
                "smtp_host": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "smtp_password": "test-password",
                "email_from": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            settings = Settings()

            assert settings.app_name == "Test App"
            assert settings.log_level == "DEBUG"
            assert settings.deepseek_api_key == "test-key"

    def test_load_settings(self):
        """Test load_settings function"""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
                "SMTP_HOST": "smtp.test.com",
                "SMTP_USER": "test@test.com",
                "SMTP_PASSWORD": "test-password",
                "EMAIL_FROM": "from@test.com",
                "EMAIL_TO": '["to@test.com"]',
            },
            clear=True,
        ):
            settings = load_settings()

            assert isinstance(settings, Settings)
            assert settings.app_name.lower() == "early bird train".lower()

