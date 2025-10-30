"""Email notifier implementation"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.domain.exceptions import NotifierException
from src.domain.interfaces import INotifier
from src.domain.models import AnalysisResult


class EmailNotifier(INotifier):
    """邮件通知器实现"""

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
        初始化邮件通知器

        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP服务器端口
            smtp_user: SMTP用户名
            smtp_password: SMTP密码
            from_addr: 发件人邮箱
            to_addrs: 收件人邮箱列表
        """
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_addr = from_addr
        self._to_addrs = to_addrs

    def send(self, analysis: AnalysisResult) -> None:
        """发送邮件通知"""
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
        """构建邮件主题"""
        query = analysis.raw_data.query
        status = "✅ 有票" if analysis.has_ticket else "❌ 无票"

        return f"【火车票监控】{query.train_number} {status} - {query.departure_date}"

    def _build_body(self, analysis: AnalysisResult) -> str:
        """构建邮件正文"""
        train = analysis.raw_data.trains[0] if analysis.raw_data.trains else None

        # HTML格式邮件
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
            <h2>🚄 火车票监控通知</h2>
            <p>查询时间：{analysis.analyzed_at.strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="content">
            <h3>📊 分析结果</h3>
            <p><strong>{analysis.summary}</strong></p>

            <h3>💡 购票建议</h3>
            <p>{analysis.recommendation}</p>
        </div>
"""

        if train:
            seats_html = ""
            for seat in train.seats:
                status_class = "available" if seat.is_available else "unavailable"
                status_text = "✅ 可预订" if seat.bookable else "❌ 不可订"

                seats_html += f"""
                <div class="seat-info {status_class}">
                    <strong>{seat.seat_type.value}</strong><br>
                    价格：¥{seat.price} | 余票：{seat.inventory_display} | {status_text}
                </div>
"""

            html += f"""
        <div class="content">
            <h3>🎫 车次详情</h3>
            <p>
                <strong>车次：</strong>{train.train_number}<br>
                <strong>线路：</strong>{train.departure_station} → {train.arrival_station}<br>
                <strong>发车：</strong>{train.departure_time}<br>
                <strong>到达：</strong>{train.arrival_time}<br>
                <strong>运行时长：</strong>{train.duration}
            </p>

            <h3>💺 座位信息</h3>
            {seats_html}
        </div>
"""

        html += """
        <div class="footer">
            <p>Early Bird Train 自动监控系统</p>
            <p>此邮件由系统自动发送，请勿回复</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _send_email(self, subject: str, body: str) -> None:
        """发送邮件"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)

        # 添加HTML正文
        html_part = MIMEText(body, "html", "utf-8")
        msg.attach(html_part)

        # 发送邮件 - 使用简单方式避免quit时的SSL错误
        server = None
        try:
            if self._smtp_port == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port, timeout=30)
            else:
                # STARTTLS连接
                server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30)
                server.starttls()

            # 登录并发送
            server.login(self._smtp_user, self._smtp_password)
            server.sendmail(self._from_addr, self._to_addrs, msg.as_string())

            # 尝试正常关闭，如果失败也不影响（邮件已发送）
            try:
                server.quit()
            except Exception:
                pass  # 忽略quit时的错误

        finally:
            # 确保连接关闭
            if server:
                try:
                    server.close()
                except Exception:
                    pass
