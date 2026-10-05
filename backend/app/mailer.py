"""Envío de emails por SMTP.

Sin SMTP configurado no se envía nada ni se escribe el mensaje en el log: el cuerpo lleva enlaces
de un solo uso (restablecer la contraseña) y cualquiera con acceso a los logs podría usarlos.
Los emails se enmascaran en el log (dato personal).

Puerto 587 (u otro): STARTTLS. Puerto 465: TLS desde el primer byte (SMTPS).

Para comprobar la configuración antes de desplegar, envía un email de prueba:

    python -m app.mailer tu-direccion@example.com
"""

import logging
import smtplib
import ssl
import sys
from email.message import EmailMessage

from app.config import get_settings

logger = logging.getLogger("pld.mailer")

SMTPS_PORT = 465


def mask_email(email: str) -> str:
    """ana.lopez@example.com -> a***@example.com"""
    user, _, domain = email.partition("@")
    return f"{user[:1]}***@{domain}" if domain else "***"


def send_email(to: str, subject: str, body: str) -> None:
    if not get_settings().smtp_host:
        logger.warning("SMTP no configurado: no se envía «%s» a %s", subject, mask_email(to))
        return
    try:
        _deliver(to, subject, body)
    except (OSError, smtplib.SMTPException):
        # Se ejecuta en segundo plano: el error se registra y no se muestra al usuario
        logger.exception("No se pudo enviar el email a %s", mask_email(to))


def _deliver(to: str, subject: str, body: str) -> None:
    """Envía el mensaje; los errores de conexión o del servidor se propagan."""
    settings = get_settings()
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    # Contexto por defecto: comprueba el certificado y el nombre del servidor (sin él, TLS
    # cifra pero acepta cualquier certificado y permite un ataque intermedio)
    context = ssl.create_default_context()
    if settings.smtp_port == SMTPS_PORT:
        server = smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, timeout=15, context=context
        )
    else:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
    with server as smtp:
        if settings.smtp_port != SMTPS_PORT:
            smtp.starttls(context=context)
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(message)


def main(argv: list[str]) -> int:
    """Email de prueba con la configuración SMTP actual. Muestra el error si falla."""
    if len(argv) != 1:
        print("Uso: python -m app.mailer destinatario@example.com")
        return 2
    settings = get_settings()
    if not settings.smtp_host:
        print("SMTP_HOST no está configurado: no se puede enviar nada.")
        return 1
    try:
        _deliver(
            argv[0],
            "Prueba de email del Python Learning Dashboard",
            "Si lees esto, la configuración SMTP funciona y los emails de recuperación "
            "de contraseña llegarán.",
        )
    except (OSError, smtplib.SMTPException) as error:
        print(f"No se pudo enviar ({settings.smtp_host}:{settings.smtp_port}): {error}")
        return 1
    print(f"Email de prueba enviado a {mask_email(argv[0])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
