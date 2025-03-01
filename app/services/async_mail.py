import asyncio
import os
from email.message import EmailMessage

from aiosmtplib import send
from fastapi import FastAPI
from premailer import transform

from .. import utils

app = FastAPI()

# Email Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("EMAIL_USER")
SMTP_PASSWORD = os.environ.get("EMAIL_PASSWORD")


async def send_email_async(email, subject, body, text="Hello"):
    """Asynchronous function to send an email using aiosmtplib."""
    message = EmailMessage()
    message["From"] = "Auctioneer API <don't reply>"
    message["To"] = email
    message["Subject"] = subject
    html_content = transform(body)
    message.set_content(text)
    message.add_alternative(html_content, subtype="html")

    await send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
    utils.pretty_print(
        "....",
        f"Sent email to: {email}",
    )


def send_email_sync(email, subject, body, text="Hello"):
    """Asynchronous function to send an email using aiosmtplib."""
    asyncio.run(send_email_async(email, subject, body, text))
