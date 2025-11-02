"""Email notifier implementation"""

import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.domain.exceptions import NotifierException
from src.domain.interfaces import INotifier
from src.domain.models import AnalysisResult


class EmailNotifier(INotifier):
    """Email notifier implementation"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_addr: str,
        to_addrs: list[str],
    ) -> None:
        """
        Initialize email notifier

        Args:
            smtp_host: SMTP server address
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_addr: Sender email address
            to_addrs: Recipient email list
        """
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_addr = from_addr
        self._to_addrs = to_addrs

    def send(self, analysis: AnalysisResult) -> None:
        """Send email notification"""
        logger.info(f"Sending email notification to {', '.join(self._to_addrs)}")

        try:
            subject = self._build_subject(analysis)
            plain_text, html_body = self._build_body(analysis)

            self._send_email(subject, plain_text, html_body)

            logger.info("Email sent successfully")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise NotifierException(f"Failed to send notification: {e}") from e

    def _format_relative_date(self, date_str: str) -> str:
        """Format date as relative time (today, tomorrow, weekday)"""
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = (target_date - today).days
            
            weekday_names_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

            if delta < 0:
                # Past date
                return f"{target_date.month}/{target_date.day}"
            elif delta == 0:
                return "今天"
            elif delta == 1:
                return "明天"
            elif delta == 2:
                return "后天"
            elif 3 <= delta <= 6:
                # This week
                weekday_cn = weekday_names_cn[target_date.weekday()]
                return weekday_cn
            elif 7 <= delta <= 13:
                # Next week
                weekday_cn = weekday_names_cn[target_date.weekday()]
                return f"下{weekday_cn}"
            elif 14 <= delta <= 20:
                # Week after next
                weekday_cn = weekday_names_cn[target_date.weekday()]
                return f"下下{weekday_cn}"
            else:
                # Far future - show month/day
                return f"{target_date.month}/{target_date.day}"
        except (ValueError, AttributeError):
            return date_str

    def _format_duration(self, duration_str: str) -> str:
        """Format duration string to remove '0时' prefix"""
        # Remove '0时' or '0h' prefix
        # Match patterns like "0时22分" or "0h22m"
        duration = duration_str.strip()
        duration = re.sub(r"^0时", "", duration)  # Remove 0时
        duration = re.sub(r"^0h", "", duration)  # Remove 0h
        return duration.strip()

    def _build_subject(self, analysis: AnalysisResult) -> str:
        """Build email subject optimized for Huawei Band display - ALL info must be here"""
        query = analysis.raw_data.query
        train = analysis.raw_data.trains[0] if analysis.raw_data.trains else None

        if analysis.has_ticket and train:
            # Format date as relative time
            date_str = self._format_relative_date(query.departure_date)

            # Format duration
            duration_str = self._format_duration(train.duration)

            # Seat abbreviation mapping (Chinese to abbreviation)
            seat_abbr_map = {
                "商务座": "BC",
                "一等座": "FC",
                "二等座": "SC",
                "软卧": "SS",
                "硬卧": "HS",
                "硬座": "HT",
                "无座": "NS",
            }

            # Get lowest price and its seat type from available seats
            min_price = None
            min_seat_type = None
            for seat in train.seats:
                if seat.is_available and seat.bookable:
                    if min_price is None or seat.price < min_price:
                        min_price = seat.price
                        min_seat_type = seat.seat_type.value

            # Format: ✅ C3380 崇州-成都南 Tmr 7:23 22分 SC¥14
            price_str = ""
            if min_price and min_seat_type:
                seat_abbr = seat_abbr_map.get(min_seat_type, min_seat_type[:2])
                price_str = f" {seat_abbr}¥{min_price}"

            return f"✅ {query.train_number} {train.departure_station}-{train.arrival_station} {date_str} {train.departure_time} {duration_str}{price_str}"
        else:
            # Format date for no ticket case using relative time
            date_str = self._format_relative_date(query.departure_date)

            return f"❌ {query.train_number} {date_str} No Tkt"

    def _build_body(self, analysis: AnalysisResult) -> tuple[str, str]:
        """Build email body - returns (plain_text, html)"""
        train = analysis.raw_data.trains[0] if analysis.raw_data.trains else None
        query = analysis.raw_data.query

        # Plain text version for Apple Watch and email preview
        plain_text = self._build_plain_text(analysis, train, query)

        # HTML email format
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; border-radius: 5px; }}
        .header.no-ticket {{ background: #f44336; }}
        .content {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .seat-info {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #2196F3; }}
        .available {{ border-left-color: #4CAF50; }}
        .unavailable {{ border-left-color: #ccc; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header {"no-ticket" if not analysis.has_ticket else ""}">
            <h2>🚄 Train Ticket Monitor Notification</h2>
            <p>Query Time: {analysis.analyzed_at.strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="content">
            <h3>📊 Analysis Results</h3>
            <p><strong>{analysis.summary}</strong></p>

            <h3>💡 Booking Recommendations</h3>
            <p>{analysis.recommendation}</p>
        </div>
"""

        if train:
            seats_html = ""
            for seat in train.seats:
                status_class = "available" if seat.is_available else "unavailable"
                status_text = "✅ Bookable" if seat.bookable else "❌ Not Bookable"

                seats_html += f"""
                <div class="seat-info {status_class}">
                    <strong>{seat.seat_type.value}</strong><br>
                    Price: ¥{seat.price} | Available: {seat.inventory_display} | {status_text}
                </div>
"""

            html += f"""
        <div class="content">
            <h3>🎫 Train Details</h3>
            <p>
                <strong>Train Number:</strong> {train.train_number}<br>
                <strong>Route:</strong> {train.departure_station} → {train.arrival_station}<br>
                <strong>Departure:</strong> {train.departure_time}<br>
                <strong>Arrival:</strong> {train.arrival_time}<br>
                <strong>Duration:</strong> {train.duration}
            </p>

            <h3>💺 Seat Information</h3>
            {seats_html}
        </div>
"""

        html += """
        <div class="footer">
            <p>Early Bird Train Automatic Monitoring System</p>
            <p>This email is automatically sent by the system, please do not reply</p>
        </div>
    </div>
</body>
</html>
"""

        return plain_text, html

    def _build_plain_text(self, analysis: AnalysisResult, train, query) -> str:
        """Build plain text summary optimized for Huawei Band 10 display"""
        lines = []

        # Seat abbreviation mapping (Chinese to abbreviation)
        seat_abbr_map = {
            "商务座": "BC",
            "一等座": "FC",
            "二等座": "SC",
            "软卧": "SS",
            "硬卧": "HS",
            "硬座": "HT",
            "无座": "NS",
        }

        if analysis.has_ticket and train:
            lines.append("✅ TKT AVAIL")
            lines.append(f"{train.train_number}")
            lines.append(f"{train.departure_station} → {train.arrival_station}")
            lines.append(f"Dep: {train.departure_time}")
            lines.append(f"Arr: {train.arrival_time}")
            lines.append(f"Dur: {train.duration}")
            lines.append("")

            # Available seats with abbreviations
            lines.append("Seats:")
            for seat in train.seats:
                if seat.is_available and seat.bookable:
                    seat_abbr = seat_abbr_map.get(seat.seat_type.value, seat.seat_type.value)
                    lines.append(f"{seat_abbr}: ¥{seat.price} ({seat.inventory_display})")

            lines.append("")
            lines.append(f"💡 {analysis.recommendation}")
        else:
            lines.append("❌ NO TKT")
            lines.append(f"{query.train_number}")
            lines.append(f"{query.departure_date}")
            lines.append(f"{query.from_station} → {query.to_station}")
            lines.append("")
            lines.append(f"{analysis.summary}")

        lines.append("")
        lines.append(f"Chk: {analysis.analyzed_at.strftime('%m-%d %H:%M')}")

        return "\n".join(lines)

    def _send_email(self, subject: str, plain_text: str, html_body: str) -> None:
        """Send email with both plain text and HTML"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)

        # Add plain text part (for Apple Watch and email preview)
        text_part = MIMEText(plain_text, "plain", "utf-8")
        msg.attach(text_part)

        # Add HTML part (for full email clients)
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)

        # Send email - use simple method to avoid SSL errors on quit
        server = None
        try:
            if self._smtp_port == 465:
                # SSL connection
                server = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port, timeout=30)
            else:
                # STARTTLS connection
                server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30)
                server.starttls()

            # Login and send
            server.login(self._smtp_user, self._smtp_password)
            server.sendmail(self._from_addr, self._to_addrs, msg.as_string())

            # Try to close normally, failure doesn't matter (email already sent)
            try:
                server.quit()
            except Exception:
                pass  # Ignore errors on quit

        finally:
            # Ensure connection is closed
            if server:
                try:
                    server.close()
                except Exception:
                    pass
