"""Modelo simulado (A2A_MOCK_MODEL=true o A2A_MODEL_PROVIDER=mock).

No llama a ningún servicio externo ni necesita API key: devuelve la respuesta que ha preparado el
propio tutor con sus reglas y el contenido revisado del curso, marcada como «sin IA». Sirve para
desarrollo y tests y, mientras no haya un modelo en producción, como tutor sin IA: sus respuestas
nunca se presentan como de un modelo de lenguaje (la tarea lleva `source: simulated`).
"""

from app.a2a.providers.base import ModelRequest

MOCK_NOTICE = (
    "_Tutor sin IA: respuesta preparada con reglas y con el contenido revisado del curso; no la "
    "ha escrito un modelo de lenguaje._"
)


class MockModelProvider:
    name = "mock"
    model = "mock"
    unavailable_message = "El tutor no está disponible ahora mismo."

    async def generate(self, request: ModelRequest) -> str:
        return f"{request.outline}\n\n{MOCK_NOTICE}"
