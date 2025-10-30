"""Domain models with strong typing using Pydantic"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SeatType(str, Enum):
    """座位类型枚举"""

    SECOND_CLASS = "二等座"
    FIRST_CLASS = "一等座"
    NO_SEAT = "无座"
    BUSINESS_CLASS = "商务座"


class SeatInfo(BaseModel):
    """座位信息模型"""

    model_config = ConfigDict(frozen=True)

    seat_type: SeatType = Field(description="座位类型")
    price: int = Field(ge=0, description="价格（元）")
    inventory: int = Field(ge=0, description="余票数量，99表示充足")
    bookable: bool = Field(description="是否可预订")

    @property
    def is_available(self) -> bool:
        """是否有票可订"""
        return self.bookable and self.inventory > 0

    @property
    def inventory_display(self) -> str:
        """余票显示文本"""
        return "充足" if self.inventory >= 99 else f"{self.inventory}张"


class TrainInfo(BaseModel):
    """车次信息模型"""

    model_config = ConfigDict(frozen=True)

    train_number: str = Field(description="车次号", pattern=r"^[A-Z]\d+$")
    departure_station: str = Field(description="出发站")
    arrival_station: str = Field(description="到达站")
    departure_time: str = Field(description="发车时间", pattern=r"^\d{2}:\d{2}$")
    arrival_time: str = Field(description="到达时间", pattern=r"^\d{2}:\d{2}$")
    duration: str = Field(description="运行时长")
    start_price: int = Field(ge=0, description="起步价（元）")
    seats: list[SeatInfo] = Field(description="座位信息列表")

    @property
    def has_second_class_seat(self) -> bool:
        """是否有二等座"""
        return any(seat.seat_type == SeatType.SECOND_CLASS and seat.is_available for seat in self.seats)

    @property
    def has_seated_ticket(self) -> bool:
        """是否有坐票（非无座）"""
        return any(seat.seat_type != SeatType.NO_SEAT and seat.is_available for seat in self.seats)

    def get_seat_by_type(self, seat_type: SeatType) -> SeatInfo | None:
        """根据类型获取座位信息"""
        return next((seat for seat in self.seats if seat.seat_type == seat_type), None)


class TicketQuery(BaseModel):
    """车票查询请求模型"""

    departure_station: str = Field(description="出发站")
    arrival_station: str = Field(description="到达站")
    departure_date: str = Field(description="出发日期", pattern=r"^\d{4}-\d{2}-\d{2}$")
    train_number: str | None = Field(None, description="指定车次号")


class TicketQueryResult(BaseModel):
    """车票查询结果模型"""

    model_config = ConfigDict(frozen=True)

    query: TicketQuery = Field(description="查询条件")
    trains: list[TrainInfo] = Field(description="查询到的车次列表")
    query_time: datetime = Field(default_factory=datetime.now, description="查询时间")

    @property
    def found_trains(self) -> bool:
        """是否找到车次"""
        return len(self.trains) > 0


class AnalysisResult(BaseModel):
    """AI分析结果模型"""

    has_ticket: bool = Field(description="是否有票")
    has_seated_ticket: bool = Field(description="是否有坐票")
    summary: str = Field(description="分析总结")
    recommendation: str = Field(description="购票建议")
    raw_data: TicketQueryResult = Field(description="原始查询数据")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="分析时间")
