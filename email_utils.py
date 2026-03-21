import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def generate_verify_code() -> str:
    """6자리 인증 코드 생성"""
    return str(random.randint(100000, 999999))


def send_verify_email(to_email: str, code: str) -> bool:
    """인증 코드 이메일 발송"""
    msg = MIMEMultipart()
    msg["From"] = f"바람난 도시 <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = "[바람난 도시] 이메일 인증 코드"

    body = f"""
    <div style="font-family: sans-serif; max-width: 400px; margin: 0 auto; padding: 20px;">
        <div style="background: #5BA89E; text-align: center; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
            <img src="https://windycity.co.kr/uploads/windycity_logo.png" alt="바람난 도시" style="height: 48px;" />
        </div>
        <p>아래 인증 코드를 입력해 주세요.</p>
        <div style="background: #5BA89E; color: #fff; font-size: 32px; font-weight: bold;
                    letter-spacing: 8px; text-align: center; padding: 20px; border-radius: 8px;">
            {code}
        </div>
        <p style="color: #888; font-size: 13px; margin-top: 16px;">
            이 코드는 10분간 유효합니다.
        </p>
    </div>
    """
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False

def send_email(to_email: str, subject: str, body: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False