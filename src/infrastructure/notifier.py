"""Email notifier implementation"""

import smtplib
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
            body = self._build_body(analysis)

            self._send_email(subject, body)

            logger.info("Email sent successfully")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise NotifierException(f"Failed to send notification: {e}") from e

    def _build_subject(self, analysis: AnalysisResult) -> str:
        """Build email subject"""
        query = analysis.raw_data.query
        status = "✅ Tickets Available" if analysis.has_ticket else "❌ No Tickets"

        return f"[Train Ticket Monitor] {query.train_number} {status} - {query.departure_date}"

    def _build_body(self, analysis: AnalysisResult) -> str:
        """Build email body"""
        train = analysis.raw_data.trains[0] if analysis.raw_data.trains else None

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

        return html

    def _send_email(self, subject: str, body: str) -> None:
        """Send email"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)

        # Add HTML body
        html_part = MIMEText(body, "html", "utf-8")
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
