"""Agentes A2A (Agent2Agent, especificación 1.0) junto a la API REST. Ver ADR-0034 y docs/a2a.md.

- cards/: Agent Card de cada agente (qué sabe hacer y cómo se le llama).
- agents/: lógica educativa de cada agente, sin nada del protocolo.
- executors/: puente entre el protocolo A2A (tareas, mensajes) y el agente.
- providers/: modelos de lenguaje intercambiables (de momento, solo el simulado).
- server.py: registro de agentes y montaje de sus rutas en la app FastAPI existente.
"""
