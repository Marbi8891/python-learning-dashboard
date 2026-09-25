# Política de seguridad

Si encuentras una vulnerabilidad, **no abras un issue público**. Repórtala por
[GitHub Security Advisories](../../security/advisories/new) con los pasos para reproducirla.

Buenas prácticas del proyecto:
- Los secretos van en `backend/.env`, que nunca se sube al repositorio (ver `.env.example`).
- CORS solo admite los orígenes configurados.
- Dependabot mantiene las dependencias actualizadas.
