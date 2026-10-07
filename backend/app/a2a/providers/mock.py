"""Modelo simulado para desarrollo y tests (A2A_MOCK_MODEL=true).

No llama a ningún servicio externo ni necesita API key: devuelve la guía que ha preparado el
agente, marcada como simulada, para probar el protocolo A2A de punta a punta.
No se debe activar en producción: sus respuestas no son de un modelo de lenguaje.
"""

from app.a2a.providers.base import ModelRequest

MOCK_NOTICE = "_Modo de desarrollo: respuesta preparada por el tutor sin modelo de IA._"


class MockModelProvider:
    name = "mock"
    model = "mock"
    unavailable_message = "El tutor no está disponible ahora mismo."

    async def generate(self, request: ModelRequest) -> str:
        return f"{request.outline}\n\n{MOCK_NOTICE}"
