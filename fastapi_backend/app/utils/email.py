import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv(override=True)


async def send_email(
    recipient: str,
    subject: str,
    body: str,
):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "2525"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

    print("SMTP HOST:", smtp_host)
    print("SMTP PORT:", smtp_port)
    print("SMTP USERNAME:", smtp_username)
    print("SMTP FROM:", smtp_from_email)
    print(
        "SMTP PASSWORD:",
        "CONFIGURED" if smtp_password else "MISSING",
    )

    if not smtp_host:
        raise ValueError("SMTP_HOST is not configured")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is not configured")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured")

    if not smtp_from_email:
        raise ValueError("SMTP_FROM_EMAIL is not configured")

    message = EmailMessage()
    message["From"] = smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    print("STEP 1: Connecting to Mailtrap...", flush=True)

    context = ssl.create_default_context()

    # Standard Python SMTP client.
    # Port 2525 uses STARTTLS.
    with smtplib.SMTP(
        smtp_host,
        smtp_port,
        timeout=30,
    ) as server:

        print(
            "STEP 2: SMTP CONNECTION SUCCESS",
            flush=True,
        )

        print(
            "STEP 3: Starting TLS...",
            flush=True,
        )

        server.starttls(context=context)

        print(
            "STEP 4: TLS SUCCESS",
            flush=True,
        )

        print(
            "STEP 5: Logging in...",
            flush=True,
        )

        server.login(
            smtp_username,
            smtp_password,
        )

        print(
            "STEP 6: LOGIN SUCCESS",
            flush=True,
        )

        print(
            "STEP 7: Sending email...",
            flush=True,
        )

        server.send_message(message)

        print(
            "STEP 8: EMAIL SENT SUCCESSFULLY",
            flush=True,
        )