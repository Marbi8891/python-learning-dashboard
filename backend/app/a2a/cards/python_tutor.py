"""Agent Card del Python Tutor.

Solo declara lo que está implementado: JSON-RPC, sin streaming ni notificaciones push, texto de
entrada (más un objeto JSON opcional con la lección, el código y el error) y texto de salida.
"""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    HTTPAuthSecurityScheme,
    SecurityRequirement,
    SecurityScheme,
    StringList,
)
from a2a.utils.constants import PROTOCOL_VERSION_1_0, TransportProtocol

AGENT_VERSION = "0.1.0"
BEARER = "bearer"


def build_python_tutor_card(agent_url: str, mock_model: bool) -> AgentCard:
    description = (
        "Tutor de Python del Python Learning Dashboard: explica conceptos y errores, revisa código "
        "sin ejecutarlo, propone ejercicios adaptados al nivel y guía sin resolver por el alumno."
    )
    if mock_model:
        description += " Modo de desarrollo: responde un modelo simulado."
    return AgentCard(
        name="Python Tutor",
        description=description,
        version=AGENT_VERSION,
        supported_interfaces=[
            AgentInterface(
                url=agent_url,
                protocol_binding=TransportProtocol.JSONRPC.value,
                protocol_version=PROTOCOL_VERSION_1_0,
            )
        ],
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        # La misma sesión que la API REST: JWT en «Authorization: Bearer» (o la cookie de la web)
        security_schemes={
            BEARER: SecurityScheme(
                http_auth_security_scheme=HTTPAuthSecurityScheme(
                    scheme="Bearer",
                    bearer_format="JWT",
                    description="Token de POST /api/v1/auth/login",
                )
            )
        },
        security_requirements=[SecurityRequirement(schemes={BEARER: StringList()})],
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="python-learning",
                name="Aprender Python",
                description=(
                    "Fundamentos de Python, depuración y explicación de errores, explicación y "
                    "revisión de código, ejercicios y orientación de estudio."
                ),
                tags=["python", "fundamentals", "debugging", "code explanation", "exercises"],
                examples=[
                    "¿Qué diferencia hay entre una lista y una tupla?",
                    "Me sale NameError: name 'total' is not defined, ¿por qué?",
                    "Propón un ejercicio de bucles para practicar",
                ],
            )
        ],
    )
