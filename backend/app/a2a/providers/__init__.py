"""Proveedores de modelo de lenguaje para los agentes.

El de Anthropic (`providers/anthropic.py`) no se importa aquí: solo se carga si se elige
(A2A_MODEL_PROVIDER=anthropic), igual que el SDK de A2A solo se carga con A2A_ENABLED=true.
"""

from app.a2a.providers.base import AgentModelProvider, ModelProviderError, ModelRequest
from app.a2a.providers.mock import MockModelProvider

__all__ = ["AgentModelProvider", "MockModelProvider", "ModelProviderError", "ModelRequest"]
