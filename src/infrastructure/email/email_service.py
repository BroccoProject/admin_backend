import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)

async def send_email(to: str, subject: str, body: str) -> None:
    """Sends a plain text email asynchronously (fire and forget)."""
    def _send():
        try:
            if not settings.SMTP_HOST or not settings.SMTP_USER:
                logger.warning("SMTP not configured. Skipping email send.")
                return

            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_USER
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to}")
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")

    # Run the blocking SMTP call in a thread pool so it doesn't block the event loop
    loop = asyncio.get_running_loop()
    # Using run_in_executor directly instead of awaiting it makes it fire-and-forget
    loop.run_in_executor(None, _send)

def build_approval_request_email(requester_email: str, message: str | None, approve_url: str) -> tuple[str, str]:
    subject = "New Admin Panel Access Request"
    body = f"A new access request has been submitted for the admin panel.\n\n"
    body += f"Requester: {requester_email}\n"
    if message:
        body += f"Message: {message}\n"
    body += f"\nClick the link below to approve this request:\n{approve_url}\n"
    return subject, body

def build_approval_confirmation_email(requester_email: str) -> tuple[str, str]:
    subject = "Admin Panel Access Approved"
    body = f"Hello {requester_email},\n\nYour request for access to the admin panel has been approved.\n"
    body += f"You can now log in using your Google account at:\n{settings.FRONTEND_URL}\n"
    return subject, body
