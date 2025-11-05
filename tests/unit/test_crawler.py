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


class TestCrawlerParsing:
    """Test crawler parsing methods"""

    def test_parse_trains_with_valid_json(self):
        """Test _parse_trains with valid __NEXT_DATA__"""
        crawler = CtripTicketCrawler()

        html = """
        <html>
            <head>
                <script id="__NEXT_DATA__" type="application/json">
                {
                    "props": {
                        "pageProps": {
                            "trainInfoList": [
                                {
                                    "trainNumber": "C3380",
                                    "departureStationName": "Dayi",
                                    "arrivalStationName": "Chengdu South",
                                    "departureTime": "08:00",
                                    "arrivalTime": "09:00",
                                    "duration": "01:00",
                                    "startPrice": 15,
                                    "seatItemInfoList": [
                                        {
                                            "seatName": "二等座",
                                            "seatPrice": 15,
                                            "seatInventory": 99,
                                            "seatBookable": true
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
                </script>
            </head>
        </html>
        """

        trains = crawler._parse_trains(html)

        assert len(trains) == 1
        assert trains[0].train_number == "C3380"
        assert trains[0].departure_station == "Dayi"
        assert trains[0].arrival_station == "Chengdu South"
        assert trains[0].departure_time == "08:00"
        assert trains[0].arrival_time == "09:00"
        assert trains[0].duration == "01:00"
        assert trains[0].start_price == 15
        assert len(trains[0].seats) == 1

    def test_parse_trains_with_invalid_json(self):
        """Test _parse_trains with invalid JSON"""
        crawler = CtripTicketCrawler()

        html = """
        <html>
            <head>
                <script id="__NEXT_DATA__" type="application/json">
                {invalid json}
                </script>
            </head>
        </html>
        """

        trains = crawler._parse_trains(html)

        assert trains == []

    def test_parse_trains_without_next_data(self):
        """Test _parse_trains without __NEXT_DATA__"""
        crawler = CtripTicketCrawler()

        html = """
        <html>
            <head></head>
            <body></body>
        </html>
        """

        trains = crawler._parse_trains(html)

        assert trains == []

    def test_find_train_list_with_trainInfoList(self):
        """Test _find_train_list finds trainInfoList"""
        crawler = CtripTicketCrawler()

        data = {
            "props": {
                "pageProps": {
                    "trainInfoList": [{"trainNumber": "C3380"}]
                }
            }
        }

        result = crawler._find_train_list(data)

        assert result is not None
        assert len(result) == 1
        assert result[0]["trainNumber"] == "C3380"

    def test_find_train_list_with_trainList(self):
        """Test _find_train_list finds trainList"""
        crawler = CtripTicketCrawler()

        data = {
            "props": {
                "pageProps": {
                    "trainList": [{"trainNumber": "G1"}]
                }
            }
        }

        result = crawler._find_train_list(data)

        assert result is not None
        assert len(result) == 1
        assert result[0]["trainNumber"] == "G1"

    def test_find_train_list_not_found(self):
        """Test _find_train_list returns None when not found"""
        crawler = CtripTicketCrawler()

        data = {
            "props": {
                "pageProps": {
                    "someOtherKey": []
                }
            }
        }

        result = crawler._find_train_list(data)

        assert result is None

    def test_find_train_list_max_depth(self):
        """Test _find_train_list respects max depth"""
        crawler = CtripTicketCrawler()

        # Create deeply nested structure
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "level6": {
                                    "level7": {
                                        "level8": {
                                            "level9": {
                                                "level10": {
                                                    "level11": {
                                                        "trainInfoList": [{"trainNumber": "C3380"}]
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        result = crawler._find_train_list(data)

        # Should return None due to max depth limit
        assert result is None

    def test_find_train_list_with_list_input(self):
        """Test _find_train_list with list as input"""
        crawler = CtripTicketCrawler()

        data = [
            {"someKey": "someValue"},
            {"trainInfoList": [{"trainNumber": "C3380"}]}
        ]

        result = crawler._find_train_list(data)

        assert result is not None
        assert len(result) == 1
        assert result[0]["trainNumber"] == "C3380"

    def test_parse_train(self):
        """Test _parse_train"""
        crawler = CtripTicketCrawler()

        train_data = {
            "trainNumber": "C3380",
            "departureStationName": "Dayi",
            "arrivalStationName": "Chengdu South",
            "departureTime": "08:00",
            "arrivalTime": "09:00",
            "duration": "01:00",
            "startPrice": 15,
            "seatItemInfoList": [
                {
                    "seatName": "二等座",
                    "seatPrice": 15,
                    "seatInventory": 99,
                    "seatBookable": True
                },
                {
                    "seatName": "一等座",
                    "seatPrice": 25,
                    "seatInventory": 50,
                    "seatBookable": True
                }
            ]
        }

        train = crawler._parse_train(train_data)

        assert train.train_number == "C3380"
        assert train.departure_station == "Dayi"
        assert train.arrival_station == "Chengdu South"
        assert train.departure_time == "08:00"
        assert train.arrival_time == "09:00"
        assert train.duration == "01:00"
        assert train.start_price == 15
        assert len(train.seats) == 2

    def test_parse_seat_second_class(self):
        """Test _parse_seat for second class"""
        crawler = CtripTicketCrawler()

        seat_data = {
            "seatName": "二等座",
            "seatPrice": 15,
            "seatInventory": 99,
            "seatBookable": True
        }

        seat = crawler._parse_seat(seat_data)

        assert seat.seat_type.value == "二等座"
        assert seat.price == 15
        assert seat.inventory == 99
        assert seat.bookable is True

    def test_parse_seat_first_class(self):
        """Test _parse_seat for first class"""
        crawler = CtripTicketCrawler()

        seat_data = {
            "seatName": "一等座",
            "seatPrice": 25,
            "seatInventory": 50,
            "seatBookable": True
        }

        seat = crawler._parse_seat(seat_data)

        assert seat.seat_type.value == "一等座"
        assert seat.price == 25

    def test_parse_seat_business_class(self):
        """Test _parse_seat for business class"""
        crawler = CtripTicketCrawler()

        seat_data = {
            "seatName": "商务座",
            "seatPrice": 50,
            "seatInventory": 10,
            "seatBookable": True
        }

        seat = crawler._parse_seat(seat_data)

        assert seat.seat_type.value == "商务座"
        assert seat.price == 50

    def test_parse_seat_no_seat(self):
        """Test _parse_seat for no seat"""
        crawler = CtripTicketCrawler()

        seat_data = {
            "seatName": "无座",
            "seatPrice": 10,
            "seatInventory": 99,
            "seatBookable": True
        }

        seat = crawler._parse_seat(seat_data)

        assert seat.seat_type.value == "无座"
        assert seat.price == 10

    def test_parse_seat_unknown_type(self):
        """Test _parse_seat with unknown seat type defaults to second class"""
        crawler = CtripTicketCrawler()

        seat_data = {
            "seatName": "特等座",
            "seatPrice": 100,
            "seatInventory": 5,
            "seatBookable": True
        }

        seat = crawler._parse_seat(seat_data)

        # Should default to second class
        assert seat.seat_type.value == "二等座"
        assert seat.price == 100

    @patch("requests.Session.get")
    def test_fetch_html_with_params(self, mock_get):
        """Test _fetch_html builds correct URL parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler()
        query = mock_ticket_query()
        query.departure_station = "Beijing"
        query.arrival_station = "Shanghai"
        query.departure_date = "2025-12-01"

        html = crawler._fetch_html(query)

        # Verify the call was made
        assert mock_get.called
        call_args = mock_get.call_args

        # Check params
        params = call_args.kwargs.get("params")
        assert params is not None
        assert params["dStation"] == "Beijing"
        assert params["aStation"] == "Shanghai"
        assert params["dDate"] == "2025-12-01"

    @patch("requests.Session.get")
    def test_fetch_html_timeout(self, mock_get):
        """Test _fetch_html uses correct timeout"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        crawler = CtripTicketCrawler(timeout=30)
        query = mock_ticket_query()

        crawler._fetch_html(query)

        call_args = mock_get.call_args
        assert call_args.kwargs.get("timeout") == 30

