"""DeepSeek AI analyzer implementation"""

from loguru import logger
from openai import OpenAI

from src.domain.exceptions import AnalyzerException
from src.domain.interfaces import ITicketAnalyzer
from src.domain.models import AnalysisResult, SeatType, TicketQueryResult


class DeepSeekAnalyzer(ITicketAnalyzer):
    """DeepSeek AI analyzer implementation"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ) -> None:
        """
        Initialize analyzer

        Args:
            api_key: DeepSeek API key
            base_url: API base URL
            model: Model name
        """
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def analyze(self, result: TicketQueryResult) -> AnalysisResult:
        """Analyze ticket data"""
        logger.info(f"Analyzing ticket data for {result.query.train_number}")

        try:
            # Quick check (no AI needed)
            has_ticket, has_seated = self._quick_check(result)

            # If no trains found, return directly
            if not result.found_trains:
                return AnalysisResult(
                    has_ticket=False,
                    has_seated_ticket=False,
                    summary="❌ Train not found",
                    recommendation="Please check if the train number is correct, or try again later.",
                    raw_data=result,
                )

            # Generate detailed analysis using AI
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
        """Quick check if tickets and seated tickets are available"""
        if not result.found_trains:
            return False, False

        train = result.trains[0]  # Only focus on the first one (specified train)

        has_ticket = train.has_second_class_seat
        has_seated = train.has_seated_ticket

        return has_ticket, has_seated

    def _generate_ai_analysis(self, result: TicketQueryResult) -> tuple[str, str]:
        """Generate analysis and recommendations using AI"""
        train = result.trains[0]

        # Build prompt
        prompt = self._build_prompt(train)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a train ticket booking assistant, helping users analyze ticket availability and provide booking suggestions. "
                        "Please answer in concise and clear language, using emojis to make information more intuitive.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            content = response.choices[0].message.content or ""

            # Simple split of summary and recommendation
            parts = content.split("\n\n", 1)
            summary = parts[0].strip()
            recommendation = parts[1].strip() if len(parts) > 1 else "Recommend booking as soon as possible."

            return summary, recommendation

        except Exception as e:
            logger.warning(f"AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(train)

    def _build_prompt(self, train) -> str:
        """Build AI prompt"""
        seat_info = "\n".join(
            [
                f"- {seat.seat_type.value}: ¥{seat.price}, "
                f"Available: {seat.inventory_display}, "
                f"{'Bookable' if seat.bookable else 'Not bookable'}"
                for seat in train.seats
            ]
        )

        return f"""
Please analyze the ticket availability for the following train:

Train Number: {train.train_number}
Route: {train.departure_station} ({train.departure_time}) → {train.arrival_station} ({train.arrival_time})
Duration: {train.duration}

Seat Information:
{seat_info}

Please answer in two parts:
1. First part: Summarize ticket availability (whether tickets are available, which seats can be booked)
2. Second part: Provide booking recommendations

Answer briefly using emojis.
""".strip()

    def _fallback_analysis(self, train) -> tuple[str, str]:
        """Fallback analysis (when AI call fails)"""
        second_class = train.get_seat_by_type(SeatType.SECOND_CLASS)

        if second_class and second_class.is_available:
            summary = f"✅ {train.train_number} has tickets!\nSecond Class: ¥{second_class.price}, Available: {second_class.inventory_display}"
            recommendation = "Recommend booking second class tickets as soon as possible."
        else:
            summary = f"❌ {train.train_number} currently has no second class tickets"
            recommendation = "Recommend waiting for ticket release or considering other trains."

        return summary, recommendation
