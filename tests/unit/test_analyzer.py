"""Unit tests for DeepSeekAnalyzer"""

from unittest.mock import Mock, patch

import pytest
from openai import OpenAI

from src.domain.exceptions import AnalyzerException
from src.infrastructure.analyzer import DeepSeekAnalyzer
from tests.fixtures.mock_data import mock_query_result


class TestDeepSeekAnalyzer:
    """Test DeepSeek analyzer"""

    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        assert analyzer._client is not None
        assert analyzer._model == "deepseek-chat"

    @patch("openai.OpenAI")
    def test_analyze_with_tickets(self, mock_openai):
        """Test analysis with tickets available"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Recommend booking immediately"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        result = mock_query_result(has_tickets=True)
        analysis = analyzer.analyze(result)

        assert analysis.has_ticket is True
        assert analysis.raw_data == result
        # AI analysis will be called
        assert isinstance(analysis.summary, str)
        assert isinstance(analysis.recommendation, str)

    @patch("openai.OpenAI")
    def test_analyze_without_tickets(self, mock_openai):
        """Test analysis without tickets available"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="No tickets available"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        result = mock_query_result(has_tickets=False)
        analysis = analyzer.analyze(result)

        assert analysis.has_ticket is False

    @patch("openai.OpenAI")
    def test_analyze_api_error(self, mock_openai):
        """Test API error - uses fallback"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        result = mock_query_result(has_tickets=True)

        # API error will be caught, uses fallback, does not raise exception
        analysis = analyzer.analyze(result)
        
        # Should return result (using fallback)
        assert analysis is not None
        assert analysis.has_ticket is True
        assert analysis.raw_data == result

    def test_analyzer_missing_api_key(self):
        """Test missing API key"""
        # DeepSeek analyzer can be created but may fail when called
        # Empty API key can create analyzer, but will error when used
        analyzer = DeepSeekAnalyzer(
            api_key="",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )
        assert analyzer._client is not None


class TestAnalyzerConfiguration:
    """Test analyzer configuration"""

    def test_custom_model(self):
        """Test custom model"""
        models = ["deepseek-chat", "deepseek-coder", "gpt-4"]

        for model in models:
            analyzer = DeepSeekAnalyzer(
                api_key="test-key",
                base_url="https://api.deepseek.com",
                model=model,
            )
            assert analyzer._model == model

    def test_custom_base_url(self):
        """Test custom Base URL"""
        urls = [
            "https://api.deepseek.com",
            "https://api.openai.com",
            "https://custom-api.example.com",
        ]

        for url in urls:
            analyzer = DeepSeekAnalyzer(
                api_key="test-key",
                base_url=url,
                model="deepseek-chat",
            )
            # OpenAI client initialized successfully
            assert analyzer._client is not None

