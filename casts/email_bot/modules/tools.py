import os
import smtplib
from email.mime.text import MIMEText


def send_email_via_gmail(to: str, subject: str, body: str) -> str:
    """Gmail SMTP로 실제 이메일을 전송합니다."""
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = gmail_address
    msg["To"] = to
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_password)
        server.send_message(msg)

    return f"이메일 전송 완료: {to}"
