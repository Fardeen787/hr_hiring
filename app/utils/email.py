from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import logging

from app.config import settings

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(email_to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")
        raise

async def send_verification_email(email: str, name: str, token: str):
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    body = f"""
    <html>
        <body>
            <h2>Welcome {name}!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
            <a href="{verification_url}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
                Verify Email
            </a>
            <p>Or copy this link: {verification_url}</p>
            <p>This link will expire in 24 hours.</p>
        </body>
    </html>
    """
    
    await send_email(email, "Verify Your Email", body)

async def send_password_reset_email(email: str, name: str, token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    body = f"""
    <html>
        <body>
            <h2>Hello {name},</h2>
            <p>You requested to reset your password. Click the link below to proceed:</p>
            <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">
                Reset Password
            </a>
            <p>Or copy this link: {reset_url}</p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    await send_email(email, "Password Reset Request", body)
