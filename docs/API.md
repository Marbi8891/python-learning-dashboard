# API

Python Learning Dashboard exposes a versioned REST API built with FastAPI.

## Base URL

The current public API version is:

    /api/v1

Interactive OpenAPI documentation is available at /docs when ENABLE_DOCS=true.

## Main resources

| Resource | Endpoints |
| --- | --- |
| Authentication | /api/v1/auth/register, /api/v1/auth/login, /api/v1/auth/google, /api/v1/auth/logout, /api/v1/auth/logout-all |
| Password recovery ([auth.md](auth.md)) | /api/v1/auth/password-reset/request, /api/v1/auth/password-reset/confirm |
| Account | /api/v1/users/me, /api/v1/users/me/activity, /api/v1/users/me/export, POST /api/v1/users/me/delete (exactly one of `password` or `google_credential`, see [auth.md](auth.md)) |
| Health | GET /api/v1/health → `status`, `email` (reset emails can be sent), `google` (`GOOGLE_CLIENT_ID` is set) |
| Course content | /api/v1/modules, /api/v1/lessons/{slug} |
| Progress | /api/v1/progress, /api/v1/progress/{slug} |
| Exercise attempts | /api/v1/lessons/{slug}/attempts |
| PCAP state | /api/v1/pcap-state |
| DAW course state | /api/v1/course-state/{course} (`sql`, `js`, `java`, `entornos`, `programacion`, `learn`, `game`) |
| Student dashboard | GET /api/v1/dashboard?utc_offset_minutes=, GET /api/v1/dashboard/activity?limit=&offset= |

## A2A agents

When `A2A_ENABLED=true`, the same FastAPI app also serves A2A 1.0 agents under `/a2a/*`. They don't replace any REST endpoint.

| Resource | Endpoints |
| --- | --- |
| Agent Card (public) | /.well-known/agent-card.json, /a2a/python-tutor/.well-known/agent-card.json |
| Python Tutor (JSON-RPC, session required) | POST /a2a/python-tutor with header `A2A-Version: 1.0` |

The default model provider is a free local model through Ollama (`A2A_MODEL_PROVIDER=ollama`); Anthropic is available but only used when chosen explicitly (`A2A_MODEL_PROVIDER=anthropic`, key only in `ANTHROPIC_API_KEY`); tests use the mock model (`A2A_MOCK_MODEL=true`). The agent only depends on the `AgentModelProvider` interface.

**Hybrid tutor** ([tutor-hibrido.md](tutor-hibrido.md)): `GET /api/v1/tutor/modes` (session required) tells the client which tutor modes the backend offers — `free` (always available) and `advanced` (optional OpenAI, disabled by default) — plus the student's advanced quota for today (`daily_limit`, `used_today`, `remaining`, `global_available`, `max_input_chars`, `max_output_tokens`). The tutor message accepts two new optional data fields: `mode` (`free` or `advanced`, default `free`) and `alternative` (boolean). The backend validates the mode: an unavailable mode, a message over the advanced input limit or an exhausted quota ends the task as `TASK_STATE_REJECTED` with reason `advanced_unavailable`, `advanced_input_too_long`, `advanced_limit_reached` or `advanced_global_limit`, and still includes the free answer. The artifact metadata gains `mode` and, for advanced answers, `quota_remaining`. Existing clients that send neither field keep the previous behaviour.

See [a2a.md](a2a.md) (in Spanish) for the message format, examples, security, data minimization and cost limits.

## Authentication

Authenticated endpoints accept a Bearer access token:

    Authorization: Bearer <access_token>

The web client uses an HttpOnly session cookie instead. It sends this header on every request:

    X-PLD-Session: cookie

With that header, `POST /auth/login` and `POST /users/me/password` put the token in the `__Host-pld_session` cookie (`HttpOnly; Secure; SameSite=None; Partitioned`) and return `{"access_token": null, "token_type": "cookie"}`. The cookie is only accepted when the header is present (CSRF protection). `POST /auth/logout` and `POST /auth/logout-all` clear it.

Clients that don't send the header (scripts, tests) keep getting the token in the response body. If both a Bearer header and the cookie arrive, the Bearer header wins.

## Versioning and compatibility

Every route lives under /api/v1. The only exception is GET /api/health, kept because Render uses it as `healthCheckPath` (`render.yaml`).

The web client can still write paths as `/api/...`: `frontend/js/api.js` adds the `/v1` prefix before sending the request.

## Student dashboard

`GET /api/v1/dashboard` returns, for the authenticated user only, what the dashboard needs and only the server has: the user (`display_name`, `email`, `created_at`, `sign_in_method`: `google`, `password` or `null`), PCAP lessons (total, completed, last completion, next lesson, per module), exercise attempts (count, passed, lessons tried/passed, last attempt), daily activity for the last 30 days in the student's local day (`utc_offset_minutes`, -720..840) and which progress documents are synced (`pcap` and each `course-state`). No passwords, tokens or internal fields.

`GET /api/v1/dashboard/activity` is the learning history (lesson completions and attempts, newest first), paginated with `limit` (1-50, default 20) and `offset`; the submitted code is not included. Both return 401 without a session and 422 for invalid parameters.

## Design rules

- User-owned resources are resolved from the authenticated user, never from a user ID supplied by the client.
- Request and response bodies use Pydantic schemas.
- Arbitrary Python code is not executed by the server API. Code execution remains in the browser through Pyodide/Web Worker.
- API responses include security headers and sensitive responses use Cache-Control: no-store.
