"""Unit tests for EmailNotifier"""

from unittest.mock import Mock, patch

import pytest

from src.domain.exceptions import NotifierException
from src.infrastructure.notifier import EmailNotifier
from tests.fixtures.mock_data import mock_analysis


class TestEmailNotifier:
    """测试邮件通知器"""

    def test_notifier_initialization(self):
        """测试通知器初始化"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password",
            from_addr="test@gmail.com",
            to_addrs=["recipient@example.com"],
        )

        assert notifier._smtp_host == "smtp.gmail.com"
        assert notifier._smtp_port == 587
        assert notifier._smtp_user == "test@gmail.com"
        assert notifier._from_addr == "test@gmail.com"
        assert notifier._to_addrs == ["recipient@example.com"]

    @patch("smtplib.SMTP")
    def test_send_notification_success(self, mock_smtp):
        """测试成功发送通知"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password",
            from_addr="test@gmail.com",
            to_addrs=["recipient@example.com"],
        )

        analysis = mock_analysis(has_ticket=True)
        notifier.send(analysis)

        # 验证SMTP调用
        assert mock_server.starttls.call_count == 1
        assert mock_server.login.call_count == 1
        assert mock_server.sendmail.call_count == 1

    @patch("smtplib.SMTP")
    def test_send_notification_multiple_recipients(self, mock_smtp):
        """测试多个收件人"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password",
            from_addr="test@gmail.com",
            to_addrs=["user1@example.com", "user2@example.com", "user3@example.com"],
        )

        analysis = mock_analysis(has_ticket=True)
        notifier.send(analysis)

        assert mock_server.sendmail.call_count == 1

    @patch("smtplib.SMTP")
    def test_send_notification_smtp_error(self, mock_smtp):
        """测试SMTP错误"""
        mock_server = Mock()
        mock_server.starttls.side_effect = Exception("SMTP Error")
        mock_smtp.return_value = mock_server

        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password",
            from_addr="test@gmail.com",
            to_addrs=["recipient@example.com"],
        )

        analysis = mock_analysis(has_ticket=True)

        with pytest.raises(NotifierException) as exc_info:
            notifier.send(analysis)
        
        assert "Failed to send notification" in str(exc_info.value)

    @patch("smtplib.SMTP")
    def test_send_with_no_tickets(self, mock_smtp):
        """测试无票通知"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password",
            from_addr="test@gmail.com",
            to_addrs=["recipient@example.com"],
        )

        analysis = mock_analysis(has_ticket=False)
        notifier.send(analysis)

        assert mock_server.sendmail.call_count == 1

    def test_different_smtp_ports(self):
        """测试不同SMTP端口"""
        ports = [25, 465, 587, 2525]

        for port in ports:
            notifier = EmailNotifier(
                smtp_host="smtp.gmail.com",
                smtp_port=port,
                smtp_user="test@gmail.com",
                smtp_password="password",
                from_addr="test@gmail.com",
                to_addrs=["recipient@example.com"],
            )
            assert notifier._smtp_port == port


class TestEmailNotifierConfiguration:
    """测试邮件配置"""

    def test_gmail_configuration(self):
        """测试Gmail配置"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="app-password",
            from_addr="test@gmail.com",
            to_addrs=["recipient@example.com"],
        )

        assert notifier._smtp_host == "smtp.gmail.com"
        assert notifier._smtp_port == 587

    def test_qq_mail_configuration(self):
        """测试QQ邮箱配置"""
        notifier = EmailNotifier(
            smtp_host="smtp.qq.com",
            smtp_port=587,
            smtp_user="test@qq.com",
            smtp_password="auth-code",
            from_addr="test@qq.com",
            to_addrs=["recipient@example.com"],
        )

        assert notifier._smtp_host == "smtp.qq.com"

    def test_163_mail_configuration(self):
        """测试163邮箱配置"""
        notifier = EmailNotifier(
            smtp_host="smtp.163.com",
            smtp_port=465,
            smtp_user="test@163.com",
            smtp_password="auth-code",
            from_addr="test@163.com",
            to_addrs=["recipient@example.com"],
        )

        assert notifier._smtp_host == "smtp.163.com"
        assert notifier._smtp_port == 465

