"""Envío de emails por SMTP. Sin SMTP configurado, el mensaje se escribe en el log."""

import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings

logger = logging.getLogger("pld.mailer")


def send_email(to: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        # Modo desarrollo: permite probar la recuperación sin servidor de correo
        logger.warning("SMTP no configurado. Email para %s:\n%s\n%s", to, subject, body)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        # Se ejecuta en segundo plano: el error se registra y no se muestra al usuario
        logger.exception("No se pudo enviar el email a %s", to)
