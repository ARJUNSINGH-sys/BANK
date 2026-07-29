import os
import random
import smtplib
from email.message import EmailMessage


def otp(receiver_email, sender_email="hometiffinsevices@gmail.com", sender_password=None):
    """Send a one-time password (OTP) to the receiver email."""
    if sender_password is None:
        sender_password = os.getenv("EMAIL_OTP_PASSWORD")

    if not sender_password:
        raise ValueError(
            "Sender password is required. Set EMAIL_OTP_PASSWORD or pass sender_password."
        )

    otp_code = random.randint(100000, 999999)
    message = EmailMessage()
    message["Subject"] = "Your OTP Code"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.set_content(
        f"Your one-time password is: {otp_code}\n\n"
        "If you did not request this code, please ignore this email."
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            "SMTP authentication failed. Check your Gmail app password and account settings."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to send OTP email: {exc}") from exc

    return otp_code


if __name__ == "__main__":
    recipient = "kamini.singh51@gmail.com"
    sender_password = os.getenv("EMAIL_OTP_PASSWORD")
    print(f"Sending OTP to {recipient}...")
    try:
        code = otp(recipient, sender_password=sender_password)
        print("OTP sent successfully:", code)
    except Exception as error:
        print("Error sending OTP:", error)
