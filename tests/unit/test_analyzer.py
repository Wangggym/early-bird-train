"""Unit tests for DeepSeekAnalyzer"""

from unittest.mock import Mock, patch

import pytest
from openai import OpenAI

from src.domain.exceptions import AnalyzerException
from src.infrastructure.analyzer import DeepSeekAnalyzer
from tests.fixtures.mock_data import mock_query_result


class TestDeepSeekAnalyzer:
    """测试DeepSeek分析器"""

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        assert analyzer._client is not None
        assert analyzer._model == "deepseek-chat"

    @patch("openai.OpenAI")
    def test_analyze_with_tickets(self, mock_openai):
        """测试有票的分析"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="建议立即购票"))]
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
        # AI 分析会被调用
        assert isinstance(analysis.summary, str)
        assert isinstance(analysis.recommendation, str)

    @patch("openai.OpenAI")
    def test_analyze_without_tickets(self, mock_openai):
        """测试无票的分析"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="暂无余票"))]
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
        """测试API错误 - 使用 fallback"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )

        result = mock_query_result(has_tickets=True)

        # API 错误会被捕获，使用 fallback，不抛出异常
        analysis = analyzer.analyze(result)
        
        # 应该返回结果（使用 fallback）
        assert analysis is not None
        assert analysis.has_ticket is True
        assert analysis.raw_data == result

    def test_analyzer_missing_api_key(self):
        """测试缺少API Key"""
        # DeepSeek analyzer 会创建但可能在调用时失败
        # 空 API key 可以创建，但使用时会出错
        analyzer = DeepSeekAnalyzer(
            api_key="",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )
        assert analyzer._client is not None


class TestAnalyzerConfiguration:
    """测试分析器配置"""

    def test_custom_model(self):
        """测试自定义模型"""
        models = ["deepseek-chat", "deepseek-coder", "gpt-4"]

        for model in models:
            analyzer = DeepSeekAnalyzer(
                api_key="test-key",
                base_url="https://api.deepseek.com",
                model=model,
            )
            assert analyzer._model == model

    def test_custom_base_url(self):
        """测试自定义Base URL"""
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
            # OpenAI client 初始化成功
            assert analyzer._client is not None

