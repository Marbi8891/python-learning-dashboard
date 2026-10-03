# API

Python Learning Dashboard exposes a versioned REST API built with FastAPI.

## Base URL

The current public API version is:

    /api/v1

Interactive OpenAPI documentation is available at /docs when ENABLE_DOCS=true.

## Main resources

| Resource | Endpoints |
| --- | --- |
| Authentication | /api/v1/auth/register, /api/v1/auth/login, /api/v1/auth/logout-all |
| Account | /api/v1/users/me, /api/v1/users/me/activity, /api/v1/users/me/export |
| Course content | /api/v1/modules, /api/v1/lessons/{slug} |
| Progress | /api/v1/progress, /api/v1/progress/{slug} |
| Exercise attempts | /api/v1/lessons/{slug}/attempts |
| PCAP state | /api/v1/pcap-state |
| DAW course state | /api/v1/course-state/{course} |

## Authentication

Authenticated endpoints use a Bearer access token:

    Authorization: Bearer <access_token>

The browser client keeps the access token in memory rather than localStorage/sessionStorage.

## Versioning and compatibility

/api/v1 is the documented API surface for new clients.

The previous /api/... routes remain available temporarily for compatibility with existing clients, including the Android application. Legacy routes are excluded from OpenAPI and are deprecated.

New integrations should use /api/v1 only.

## Design rules

- User-owned resources are resolved from the authenticated user, never from a user ID supplied by the client.
- Request and response bodies use Pydantic schemas.
- Arbitrary Python code is not executed by the server API. Code execution remains in the browser through Pyodide/Web Worker.
- API responses include security headers and sensitive responses use Cache-Control: no-store.
