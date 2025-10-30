"""DeepSeek AI analyzer implementation"""

from loguru import logger
from openai import OpenAI

from src.domain.exceptions import AnalyzerException
from src.domain.interfaces import ITicketAnalyzer
from src.domain.models import AnalysisResult, SeatType, TicketQueryResult


class DeepSeekAnalyzer(ITicketAnalyzer):
    """DeepSeek AI分析器实现"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ) -> None:
        """
        初始化分析器

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def analyze(self, result: TicketQueryResult) -> AnalysisResult:
        """分析车票数据"""
        logger.info(f"Analyzing ticket data for {result.query.train_number}")

        try:
            # 快速判断（不需要AI）
            has_ticket, has_seated = self._quick_check(result)

            # 如果没有找到车次，直接返回
            if not result.found_trains:
                return AnalysisResult(
                    has_ticket=False,
                    has_seated_ticket=False,
                    summary="❌ 未找到指定车次",
                    recommendation="请检查车次号是否正确，或稍后再试。",
                    raw_data=result,
                )

            # 使用AI生成详细分析
            summary, recommendation = self._generate_ai_analysis(result)

            return AnalysisResult(
                has_ticket=has_ticket,
                has_seated_ticket=has_seated,
                summary=summary,
                recommendation=recommendation,
                raw_data=result,
            )

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AnalyzerException(f"Failed to analyze tickets: {e}") from e

    def _quick_check(self, result: TicketQueryResult) -> tuple[bool, bool]:
        """快速检查是否有票和坐票"""
        if not result.found_trains:
            return False, False

        train = result.trains[0]  # 只关注第一个（指定车次）

        has_ticket = train.has_second_class_seat
        has_seated = train.has_seated_ticket

        return has_ticket, has_seated

    def _generate_ai_analysis(self, result: TicketQueryResult) -> tuple[str, str]:
        """使用AI生成分析和建议"""
        train = result.trains[0]

        # 构建提示词
        prompt = self._build_prompt(train)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个火车票购票助手，帮助用户分析余票情况并给出购票建议。"
                        "请用简洁、清晰的语言回答，使用emoji让信息更直观。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            content = response.choices[0].message.content or ""

            # 简单分割summary和recommendation
            parts = content.split("\n\n", 1)
            summary = parts[0].strip()
            recommendation = parts[1].strip() if len(parts) > 1 else "建议尽快购票。"

            return summary, recommendation

        except Exception as e:
            logger.warning(f"AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(train)

    def _build_prompt(self, train) -> str:
        """构建AI提示词"""
        seat_info = "\n".join(
            [
                f"- {seat.seat_type.value}: ¥{seat.price}, "
                f"余票{seat.inventory_display}, "
                f"{'可预订' if seat.bookable else '不可预订'}"
                for seat in train.seats
            ]
        )

        return f"""
请分析以下车次的余票情况：

车次：{train.train_number}
线路：{train.departure_station} ({train.departure_time}) → {train.arrival_station} ({train.arrival_time})
运行时长：{train.duration}

座位情况：
{seat_info}

请分两段回答：
1. 第一段：总结余票情况（是否有票，哪种座位可订）
2. 第二段：给出购票建议

用简短的文字回答，使用emoji。
""".strip()

    def _fallback_analysis(self, train) -> tuple[str, str]:
        """降级分析（当AI调用失败时）"""
        second_class = train.get_seat_by_type(SeatType.SECOND_CLASS)

        if second_class and second_class.is_available:
            summary = (
                f"✅ {train.train_number} 有票！\n二等座：¥{second_class.price}，余票{second_class.inventory_display}"
            )
            recommendation = "建议尽快购买二等座车票。"
        else:
            summary = f"❌ {train.train_number} 当前无二等座车票"
            recommendation = "建议等待放票或考虑其他车次。"

        return summary, recommendation
