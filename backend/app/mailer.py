"""Envío de emails por SMTP.

Sin SMTP configurado no se envía nada ni se escribe el mensaje en el log: el cuerpo lleva enlaces
de un solo uso (restablecer la contraseña) y cualquiera con acceso a los logs podría usarlos.
Los emails se enmascaran en el log (dato personal).
"""

import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.config import get_settings

logger = logging.getLogger("pld.mailer")


def mask_email(email: str) -> str:
    """ana.lopez@example.com -> a***@example.com"""
    user, _, domain = email.partition("@")
    return f"{user[:1]}***@{domain}" if domain else "***"


def send_email(to: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        logger.warning("SMTP no configurado: no se envía «%s» a %s", subject, mask_email(to))
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            # Contexto por defecto: comprueba el certificado y el nombre del servidor (sin él,
            # starttls cifra pero acepta cualquier certificado y permite un ataque intermedio)
            smtp.starttls(context=ssl.create_default_context())
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        # Se ejecuta en segundo plano: el error se registra y no se muestra al usuario
        logger.exception("No se pudo enviar el email a %s", mask_email(to))
