import yagmail  # Or smtplib, emails, etc.
from fastapi import APIRouter, BackgroundTasks

from ..config import EMAIL_PASSWORD, EMAIL_USER

router = APIRouter(
    prefix="/email",
    tags=["E-Mail"],
)

# TODO: integrate html template
# TODO: use celery with redis for background tasks
# TODO: Use Mailtrap for testing

# Initialize yagmail outside of the request handler for efficiency
try:
    yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD)
except Exception as e:
    print(
        f"Error initializing yagmail: {e}"
    )  # Handle appropriately in production


def send_email_sync(
    to: str, subject: str, body: str
):  # Synchronous email function
    try:
        yag.send(to=to, subject=subject, contents=body)
        print(f"Email sent successfully to {to}")  # Add logging
    except Exception as e:
        print(f"Error sending email to {to}: {e}")  # Add logging


@router.post("/send-email")
async def send_email_endpoint(
    to: str, subject: str, body: str, background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        send_email_sync, to, subject, body
    )  # Add to background tasks
    return {
        "message": "Email sending initiated in the background"
    }  # Return immediately
