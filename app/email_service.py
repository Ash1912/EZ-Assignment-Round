import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

def send_verification_email(email: str, verification_url: str):
    try:
        message = MIMEMultipart()
        message["From"] = SMTP_EMAIL
        message["To"] = email
        message["Subject"] = "Email Verification"
        body = f"Click the link to verify your email: {verification_url}"
        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
