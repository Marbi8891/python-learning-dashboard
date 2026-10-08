"""Envío de emails: por la API HTTPS de Brevo o por SMTP.

- Con `BREVO_API_KEY`, el email sale por HTTPS (puerto 443). Es la opción para el plan gratuito
  de Render, que bloquea la salida a los puertos SMTP (25, 465 y 587) desde 2025.
- Si no, con `SMTP_HOST`, por SMTP. Puerto 587 (u otro): STARTTLS. Puerto 465: TLS directo (SMTPS).

En los dos casos el remitente es `SMTP_FROM` (en Brevo, una dirección verificada en su panel).

Sin ninguno de los dos no se envía nada ni se escribe el mensaje en el log: el cuerpo lleva enlaces
de un solo uso (restablecer la contraseña) y cualquiera con acceso a los logs podría usarlos.
Los emails se enmascaran en el log (dato personal).

Para comprobar la configuración antes de desplegar, envía un email de prueba:

    python -m app.mailer tu-direccion@example.com
"""

import json
import logging
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from email.message import EmailMessage
from email.utils import parseaddr

from app.config import get_settings

logger = logging.getLogger("pld.mailer")

SMTPS_PORT = 465
BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def mask_email(email: str) -> str:
    """ana.lopez@example.com -> a***@example.com"""
    user, _, domain = email.partition("@")
    return f"{user[:1]}***@{domain}" if domain else "***"


def email_enabled() -> bool:
    settings = get_settings()
    return bool(settings.brevo_api_key or settings.smtp_host)


def send_email(to: str, subject: str, body: str) -> None:
    if not email_enabled():
        logger.warning("Email no configurado: no se envía «%s» a %s", subject, mask_email(to))
        return
    try:
        _deliver(to, subject, body)
    except (OSError, smtplib.SMTPException):
        # Se ejecuta en segundo plano: el error se registra y no se muestra al usuario
        logger.exception("No se pudo enviar el email a %s", mask_email(to))


def _deliver(to: str, subject: str, body: str) -> None:
    """Envía el mensaje; los errores de conexión o del servidor se propagan."""
    if get_settings().brevo_api_key:
        _deliver_brevo(to, subject, body)
    else:
        _deliver_smtp(to, subject, body)


def _deliver_brevo(to: str, subject: str, body: str) -> None:
    settings = get_settings()
    name, address = parseaddr(settings.smtp_from)
    payload = {
        "sender": {"name": name or "Python Learning Dashboard", "email": address},
        "to": [{"email": to}],
        "subject": subject,
        "textContent": body,
    }
    request = urllib.request.Request(
        BREVO_URL,
        data=json.dumps(payload).encode(),
        headers={
            "api-key": settings.brevo_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    # urlopen comprueba el certificado; un 4xx/5xx lanza HTTPError (subclase de OSError)
    with urllib.request.urlopen(request, timeout=15, context=ssl.create_default_context()):
        pass


def _deliver_smtp(to: str, subject: str, body: str) -> None:
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
    """Email de prueba con la configuración actual. Muestra el error si falla."""
    if len(argv) != 1:
        print("Uso: python -m app.mailer destinatario@example.com")
        return 2
    settings = get_settings()
    if not email_enabled():
        print("Ni BREVO_API_KEY ni SMTP_HOST están configurados: no se puede enviar nada.")
        return 1
    via = "Brevo" if settings.brevo_api_key else f"{settings.smtp_host}:{settings.smtp_port}"
    try:
        _deliver(
            argv[0],
            "Prueba de email del Python Learning Dashboard",
            "Si lees esto, el envío de emails funciona y los emails de recuperación "
            "de contraseña llegarán.",
        )
    except urllib.error.HTTPError as error:
        # Brevo explica el motivo en el cuerpo (clave incorrecta, remitente sin verificar…)
        print(f"No se pudo enviar ({via}): {error} {error.read().decode(errors='replace')}")
        return 1
    except (OSError, smtplib.SMTPException) as error:
        print(f"No se pudo enviar ({via}): {error}")
        return 1
    print(f"Email de prueba enviado a {mask_email(argv[0])} ({via}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
