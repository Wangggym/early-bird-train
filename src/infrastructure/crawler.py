"""Ctrip ticket crawler implementation"""

import requests
from bs4 import BeautifulSoup
from loguru import logger

from src.domain.exceptions import CrawlerException
from src.domain.interfaces import ITicketCrawler
from src.domain.models import SeatInfo, SeatType, TicketQuery, TicketQueryResult, TrainInfo


class CtripTicketCrawler(ITicketCrawler):
    """Ctrip train ticket crawler implementation"""

    BASE_URL = "https://trains.ctrip.com/webapp/train/list"

    def __init__(self, timeout: int = 10) -> None:
        """
        Initialize crawler

        Args:
            timeout: Request timeout in seconds
        """
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.ctrip.com/",
            }
        )

    def fetch_tickets(self, query: TicketQuery) -> TicketQueryResult:
        """Fetch ticket information"""
        logger.info(f"Fetching tickets: {query.departure_station} -> {query.arrival_station} on {query.departure_date}")

        try:
            html_content = self._fetch_html(query)
            trains = self._parse_trains(html_content)

            # If train number is specified, only return that train
            if query.train_number:
                trains = [t for t in trains if t.train_number == query.train_number]

            logger.info(f"Found {len(trains)} trains")

            return TicketQueryResult(
                query=query,
                trains=trains,
            )

        except Exception as e:
            logger.error(f"Crawler failed: {e}")
            raise CrawlerException(f"Failed to fetch tickets: {e}") from e

    def _fetch_html(self, query: TicketQuery) -> str:
        """Fetch HTML page"""
        params = {
            "ticketType": "0",
            "dStation": query.departure_station,
            "aStation": query.arrival_station,
            "dDate": query.departure_date,
            "rDate": "",
            "trainsType": "gaotie-dongche",
            "hubCityName": "",
            "highSpeedOnly": "1",
        }

        # Build complete URL for logging
        from urllib.parse import urlencode

        full_url = f"{self.BASE_URL}?{urlencode(params)}"
        logger.info(f"Fetching URL: {full_url}")

        response = self._session.get(
            self.BASE_URL,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        return response.text

    def _parse_trains(self, html: str) -> list[TrainInfo]:
        """Parse train list"""
        import json

        soup = BeautifulSoup(html, "lxml")

        # Find script tag with id="__NEXT_DATA__"
        next_data_script = soup.find("script", id="__NEXT_DATA__", type="application/json")

        if next_data_script and next_data_script.string:
            try:
                data = json.loads(next_data_script.string)
                # Find trainList
                train_list = self._find_train_list(data)
                if train_list:
                    return [self._parse_train(train_data) for train_data in train_list]
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse __NEXT_DATA__: {e}")

        return []

    def _find_train_list(self, obj: any, depth: int = 0) -> list | None:
        """Recursively find trainInfoList or trainList"""
        if depth > 10:  # Prevent recursion too deep
            return None

        if isinstance(obj, dict):
            # Find trainInfoList or trainList keys
            if "trainInfoList" in obj and isinstance(obj["trainInfoList"], list):
                return obj["trainInfoList"]
            if "trainList" in obj and isinstance(obj["trainList"], list):
                return obj["trainList"]

            # Recursive search
            for value in obj.values():
                result = self._find_train_list(value, depth + 1)
                if result:
                    return result

        elif isinstance(obj, list):
            for item in obj:
                result = self._find_train_list(item, depth + 1)
                if result:
                    return result

        return None

    def _parse_train(self, data: dict) -> TrainInfo:
        """Parse single train data"""
        seats = [self._parse_seat(seat_data) for seat_data in data.get("seatItemInfoList", [])]

        return TrainInfo(
            train_number=data["trainNumber"],
            departure_station=data["departureStationName"],
            arrival_station=data["arrivalStationName"],
            departure_time=data["departureTime"],
            arrival_time=data["arrivalTime"],
            duration=data["duration"],
            start_price=data["startPrice"],
            seats=seats,
        )

    def _parse_seat(self, data: dict) -> SeatInfo:
        """Parse seat information"""
        seat_name = data["seatName"]

        # Map seat types
        seat_type_map = {
            "二等座": SeatType.SECOND_CLASS,
            "一等座": SeatType.FIRST_CLASS,
            "无座": SeatType.NO_SEAT,
            "商务座": SeatType.BUSINESS_CLASS,
        }
        seat_type = seat_type_map.get(seat_name, SeatType.SECOND_CLASS)

        return SeatInfo(
            seat_type=seat_type,
            price=data["seatPrice"],
            inventory=data["seatInventory"],
            bookable=data["seatBookable"],
        )
