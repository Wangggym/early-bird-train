"""Unit tests for CtripTicketCrawler"""

from unittest.mock import Mock, patch

import pytest
import requests

from src.domain.exceptions import CrawlerException
from src.infrastructure.crawler import CtripTicketCrawler
from tests.fixtures.mock_data import mock_ticket_query


class TestCtripTicketCrawler:
    """Test Ctrip ticket crawler"""

    def test_crawler_initialization(self):
        """Test crawler initialization"""
        crawler = CtripTicketCrawler(timeout=15)

        assert crawler._timeout == 15
        assert crawler._session is not None
        assert "User-Agent" in crawler._session.headers

    def test_crawler_default_timeout(self):
        """Test default timeout"""
        crawler = CtripTicketCrawler()

        assert crawler._timeout == 10

    @patch("requests.Session.get")
    def test_fetch_tickets_success(self, mock_get):
        """Test successful ticket fetching (using Mock)"""
        # Mock HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="train-list">
                    <div class="train-item">C3380</div>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        result = crawler.fetch_tickets(query)

        assert result.query == query
        assert mock_get.called

    @patch("requests.Session.get")
    def test_fetch_tickets_network_error(self, mock_get):
        """Test network error"""
        mock_get.side_effect = requests.RequestException("Network error")

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        with pytest.raises(CrawlerException) as exc_info:
            crawler.fetch_tickets(query)

        assert "Failed to fetch" in str(exc_info.value)

    @patch("requests.Session.get")
    def test_fetch_tickets_timeout(self, mock_get):
        """Test timeout"""
        mock_get.side_effect = requests.Timeout("Timeout")

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        with pytest.raises(CrawlerException):
            crawler.fetch_tickets(query)

    @patch("requests.Session.get")
    def test_fetch_tickets_http_error(self, mock_get):
        """Test HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("Not found")
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        with pytest.raises(CrawlerException):
            crawler.fetch_tickets(query)

    def test_session_headers(self):
        """Test Session headers configuration"""
        crawler = CtripTicketCrawler()

        headers = crawler._session.headers

        assert "User-Agent" in headers
        assert "Mozilla" in headers["User-Agent"]
        assert "Accept" in headers
        assert "Accept-Language" in headers
        assert headers["Referer"] == "https://www.ctrip.com/"

    @patch("requests.Session.get")
    def test_filter_by_train_number(self, mock_get):
        """Test filtering by train number"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()
        query.train_number = "C3380"

        result = crawler.fetch_tickets(query)

        # Verify query parameters
        assert result.query.train_number == "C3380"


class TestCrawlerErrorHandling:
    """Test error handling"""

    @patch("requests.Session.get")
    def test_connection_error(self, mock_get):
        """Test connection error"""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        with pytest.raises(CrawlerException) as exc_info:
            crawler.fetch_tickets(query)

        assert "Failed to fetch" in str(exc_info.value)

    @patch("requests.Session.get")
    def test_invalid_response(self, mock_get):
        """Test invalid response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""  # Empty response
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()

        # Should return empty result instead of crashing
        result = crawler.fetch_tickets(query)
        assert result.query == query


class TestCrawlerConfiguration:
    """Test crawler configuration"""

    def test_custom_timeout(self):
        """Test custom timeout"""
        timeouts = [5, 10, 30, 60]

        for timeout in timeouts:
            crawler = CtripTicketCrawler(timeout=timeout)
            assert crawler._timeout == timeout

    def test_base_url_configuration(self):
        """Test base URL configuration"""
        crawler = CtripTicketCrawler()

        assert hasattr(crawler, "BASE_URL")
        assert "ctrip.com" in crawler.BASE_URL

