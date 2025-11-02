"""Mock data for tests"""

from datetime import datetime

from src.domain.models import (
    AnalysisResult,
    SeatInfo,
    SeatType,
    TicketQuery,
    TicketQueryResult,
    TrainInfo,
)


def mock_ticket_query() -> TicketQuery:
    """创建模拟票务查询"""
    return TicketQuery(
        departure_station="大邑",
        arrival_station="成都南",
        departure_date="2024-11-17",
        train_number="C3380",
    )


def mock_seat_info(available: bool = True) -> list[SeatInfo]:
    """创建模拟座位信息"""
    return [
        SeatInfo(
            seat_type=SeatType.SECOND_CLASS,
            price=15,
            inventory=99 if available else 0,
            bookable=available,
        ),
        SeatInfo(
            seat_type=SeatType.FIRST_CLASS,
            price=23,
            inventory=50 if available else 0,
            bookable=available,
        ),
    ]


def mock_trains(has_tickets: bool = True) -> list[TrainInfo]:
    """创建模拟车次列表"""
    if not has_tickets:
        return []
    
    return [
        TrainInfo(
            train_number="C3380",
            departure_station="大邑",
            arrival_station="成都南",
            departure_time="08:30",
            arrival_time="09:05",
            duration="35分",
            start_price=15,
            seats=mock_seat_info(available=True),
        ),
    ]


def mock_query_result(has_tickets: bool = True) -> TicketQueryResult:
    """创建模拟查询结果"""
    return TicketQueryResult(
        query=mock_ticket_query(),
        trains=mock_trains(has_tickets),
        query_time=datetime(2024, 11, 2, 15, 30, 0),
    )


def mock_analysis(has_ticket: bool = True) -> AnalysisResult:
    """创建模拟分析结果"""
    return AnalysisResult(
        raw_data=mock_query_result(has_ticket),
        has_ticket=has_ticket,
        has_seated_ticket=has_ticket,
        recommendation="建议立即购票" if has_ticket else "暂无余票",
        summary="分析结果示例",
        analyzed_at=datetime(2024, 11, 2, 15, 30, 0),
    )

