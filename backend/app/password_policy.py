"""Política de contraseñas (MITRE ATT&CK M1027 «Password Policies», ADR-0023).

Frena los ataques que prueban contraseñas habituales contra muchas cuentas (T1110.003 Password
Spraying) o reutilizan listas filtradas (T1110.004 Credential Stuffing): no se aceptan las
contraseñas más comunes ni las que contienen el email o el nombre de la persona.
Sin servicios externos: la lista va en el código y la comprobación es local.
"""

import re
import unicodedata

# Las más usadas en listas públicas de filtraciones, más variantes habituales en España.
# Se comparan en minúsculas y sin espacios alrededor.
COMMON_PASSWORDS = frozenset(
    """
    123456 123456789 12345678 1234567890 1234567 12345 123123 111111 000000 654321 666666
    121212 112233 123321 987654321 87654321 11111111 00000000 88888888 12341234 11223344
    password password1 password123 passw0rd p@ssw0rd qwerty qwerty123 qwertyuiop azerty
    abc123 abcd1234 a123456 123456a 12345678a 1q2w3e4r 1q2w3e4r5t 1qaz2wsx q1w2e3r4
    qwe123 asdasd asdfgh asdfghjk asdfghjkl zxcvbnm aaaaaaaa iloveyou welcome admin admin123
    administrator letmein monkey dragon football baseball sunshine princess master superman
    batman trustno1 starwars pokemon internet computer google facebook iphone samsung
    contraseña contrasena contraseña1 contrasena1 contraseña123 contrasena123 micontraseña
    secreto teamo tequiero tequieromucho mariposa corazon hola1234 hola123 holahola
    barcelona realmadrid madrid españa espana sevilla valencia futbol mimamamemima gatito
    perrito princesa estrella chocolate america veronica daniel alejandro
    python python123 programacion programación estudiante alumno profesor daw12345 dam12345
    """.split()
)

MIN_PERSONAL_PART = 4  # «ana» es demasiado corto para descartar contraseñas que lo contengan


def _plain(text: str) -> str:
    """Minúsculas y sin tildes: «María» y «maria» cuentan igual."""
    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def weakness(password: str, email: str = "", name: str = "") -> str | None:
    """Motivo por el que la contraseña no es aceptable, o None si lo es."""
    candidate = password.strip().lower()
    if candidate in COMMON_PASSWORDS:
        return "Esa contraseña es de las más usadas y se adivina enseguida. Elige otra."
    if len(set(candidate)) <= 2:
        return "La contraseña repite casi siempre el mismo carácter. Elige otra."
    if candidate.isdigit() and candidate in "01234567890123456789" + "98765432109876543210":
        return "Una secuencia de números se adivina enseguida. Elige otra contraseña."
    local = email.split("@")[0]
    personal = [_plain(local), *re.split(r"[\s._+-]+", _plain(f"{local} {name}"))]
    plain = _plain(candidate)
    if any(len(part) >= MIN_PERSONAL_PART and part in plain for part in personal):
        return "La contraseña no puede contener tu email ni tu nombre."
    return None
