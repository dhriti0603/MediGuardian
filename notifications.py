import smtplib
from email.message import EmailMessage
from config import EMAIL_ENABLED, SENDER_EMAIL, APP_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(to_email, subject, body):
    if not EMAIL_ENABLED:
        print("Email disabled in config.py")
        return False

    if not to_email:
        return False

    if SENDER_EMAIL == "your_email@gmail.com" or APP_PASSWORD == "your_gmail_app_password":
        print("Email credentials not configured.")
        return False

    try:
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print("Email error:", e)
        return False
