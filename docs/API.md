# API

Python Learning Dashboard exposes a versioned REST API built with FastAPI.

## Base URL

The current public API version is:

    /api/v1

Interactive OpenAPI documentation is available at /docs when ENABLE_DOCS=true.

## Main resources

| Resource | Endpoints |
| --- | --- |
| Authentication | /api/v1/auth/register, /api/v1/auth/login, /api/v1/auth/logout, /api/v1/auth/logout-all |
| Password recovery ([auth.md](auth.md)) | /api/v1/auth/forgot-password, /api/v1/auth/reset-password (aliases of /auth/password-reset/request and /confirm) |
| Account | /api/v1/users/me, /api/v1/users/me/activity, /api/v1/users/me/export |
| Course content | /api/v1/modules, /api/v1/lessons/{slug} |
| Progress | /api/v1/progress, /api/v1/progress/{slug} |
| Exercise attempts | /api/v1/lessons/{slug}/attempts |
| PCAP state | /api/v1/pcap-state |
| DAW course state | /api/v1/course-state/{course} |

## A2A agents

When `A2A_ENABLED=true`, the same FastAPI app also serves A2A 1.0 agents under `/a2a/*` (ADR-0034). They don't replace any REST endpoint.

| Resource | Endpoints |
| --- | --- |
| Agent Card (public) | /.well-known/agent-card.json, /a2a/python-tutor/.well-known/agent-card.json |
| Python Tutor (JSON-RPC, session required) | POST /a2a/python-tutor with header `A2A-Version: 1.0` |

See [a2a.md](a2a.md) (in Spanish) for the message format, examples and security rules.

## Authentication

Authenticated endpoints accept a Bearer access token:

    Authorization: Bearer <access_token>

The web client uses an HttpOnly session cookie instead (ADR-0033). It sends this header on every request:

    X-PLD-Session: cookie

With that header, `POST /auth/login` and `POST /users/me/password` put the token in the `__Host-pld_session` cookie (`HttpOnly; Secure; SameSite=None; Partitioned`) and return `{"access_token": null, "token_type": "cookie"}`. The cookie is only accepted when the header is present (CSRF protection). `POST /auth/logout` and `POST /auth/logout-all` clear it.

Clients that don't send the header, such as the Android app, keep getting the token in the response body. If both a Bearer header and the cookie arrive, the Bearer header wins.

## Versioning and compatibility

/api/v1 is the documented API surface for new clients.

The previous /api/... routes remain available temporarily for compatibility with existing clients, including the Android application. Legacy routes are excluded from OpenAPI and are deprecated.

New integrations should use /api/v1 only.

## Design rules

- User-owned resources are resolved from the authenticated user, never from a user ID supplied by the client.
- Request and response bodies use Pydantic schemas.
- Arbitrary Python code is not executed by the server API. Code execution remains in the browser through Pyodide/Web Worker.
- API responses include security headers and sensitive responses use Cache-Control: no-store.
