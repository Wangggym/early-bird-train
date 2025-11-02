"""Domain models with strong typing using Pydantic"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SeatType(str, Enum):
    """Seat type enumeration"""

    SECOND_CLASS = "二等座"
    FIRST_CLASS = "一等座"
    NO_SEAT = "无座"
    BUSINESS_CLASS = "商务座"


class SeatInfo(BaseModel):
    """Seat information model"""

    model_config = ConfigDict(frozen=True)

    seat_type: SeatType = Field(description="Seat type")
    price: int = Field(ge=0, description="Price (yuan)")
    inventory: int = Field(ge=0, description="Ticket inventory, 99 means sufficient")
    bookable: bool = Field(description="Whether bookable")

    @property
    def is_available(self) -> bool:
        """Whether tickets are available"""
        return self.bookable and self.inventory > 0

    @property
    def inventory_display(self) -> str:
        """Inventory display text"""
        return "Sufficient" if self.inventory >= 99 else f"{self.inventory} tickets"


class TrainInfo(BaseModel):
    """Train information model"""

    model_config = ConfigDict(frozen=True)

    train_number: str = Field(description="Train number", pattern=r"^[A-Z]\d+$")
    departure_station: str = Field(description="Departure station")
    arrival_station: str = Field(description="Arrival station")
    departure_time: str = Field(description="Departure time", pattern=r"^\d{2}:\d{2}$")
    arrival_time: str = Field(description="Arrival time", pattern=r"^\d{2}:\d{2}$")
    duration: str = Field(description="Duration")
    start_price: int = Field(ge=0, description="Starting price (yuan)")
    seats: list[SeatInfo] = Field(description="Seat information list")

    @property
    def has_second_class_seat(self) -> bool:
        """Whether second class seats are available"""
        return any(seat.seat_type == SeatType.SECOND_CLASS and seat.is_available for seat in self.seats)

    @property
    def has_seated_ticket(self) -> bool:
        """Whether seated tickets are available (excluding no-seat)"""
        return any(seat.seat_type != SeatType.NO_SEAT and seat.is_available for seat in self.seats)

    def get_seat_by_type(self, seat_type: SeatType) -> SeatInfo | None:
        """Get seat information by type"""
        return next((seat for seat in self.seats if seat.seat_type == seat_type), None)


class TicketQuery(BaseModel):
    """Ticket query request model"""

    departure_station: str = Field(description="Departure station")
    arrival_station: str = Field(description="Arrival station")
    departure_date: str = Field(description="Departure date", pattern=r"^\d{4}-\d{2}-\d{2}$")
    train_number: str | None = Field(None, description="Specified train number")


class TicketQueryResult(BaseModel):
    """Ticket query result model"""

    model_config = ConfigDict(frozen=True)

    query: TicketQuery = Field(description="Query conditions")
    trains: list[TrainInfo] = Field(description="Found train list")
    query_time: datetime = Field(default_factory=datetime.now, description="Query time")

    @property
    def found_trains(self) -> bool:
        """Whether trains were found"""
        return len(self.trains) > 0


class AnalysisResult(BaseModel):
    """AI analysis result model"""

    has_ticket: bool = Field(description="Whether tickets are available")
    has_seated_ticket: bool = Field(description="Whether seated tickets are available")
    summary: str = Field(description="Analysis summary")
    recommendation: str = Field(description="Booking recommendation")
    raw_data: TicketQueryResult = Field(description="Raw query data")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis time")
