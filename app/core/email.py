# app/core/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
import random

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

def send_verification_email(email: str, code: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = email
    msg["Subject"] = "Подтверждение email — Meeting AI"

    body = f"Ваш код подтверждения: {code}\n\nКод действителен 10 минут."
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Ошибка отправки email на {email}: {e}")
        raise