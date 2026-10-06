"""Proveedores de modelo de lenguaje para los agentes."""

from app.a2a.providers.base import AgentModelProvider, ModelRequest
from app.a2a.providers.mock import MockModelProvider

__all__ = ["AgentModelProvider", "MockModelProvider", "ModelRequest"]
