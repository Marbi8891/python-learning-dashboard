# Phase 1 — Design System Reconciliation

## Outcome

Created `DESIGN.md` as the authoritative frontend visual specification, based on the actual current implementation in `frontend/css/tokens.css` and the existing design documentation.

## Reconciliation decisions

- Current `tokens.css` values are adopted as the implementation baseline rather than the older values in `docs/DISENO.md`.
- Backgrounds: dark `#101318`, light `#f4f5f7`.
- Sidebar width: `260px` (older doc said 272px).
- Radius scale: 10/14/20px (older doc said 8/12/16px).
- Primary light-theme action text color uses dark text; `--color-primary` is the darker amber for text/focus while `--color-primary-strong` is the button fill.
- Cyan developer accent is auxiliary, not a replacement for the amber primary accent.
- Responsive shell breakpoint remains 900px; 600/900/1280px are review breakpoints, not a claim that every stylesheet uses only those values.
- Existing accessibility preferences and dark code surfaces are explicitly protected.

## Files reviewed

- `frontend/css/tokens.css`
- `frontend/css/base.css`
- `frontend/css/redesign.css`
- `docs/DISENO.md`
- `docs/REDISENO-FRONTEND.md`
- Phase 0 audit

## Changes in this phase

- Added `DESIGN.md`.
- Added this reconciliation report.
- No CSS, HTML, JavaScript, dependencies, routes, content, backend, tests or infrastructure changed.

## Validation

- Reviewed token values against current source.
- Runtime/browser screenshot comparison and contrast recalculation are not available through this GitHub-only session; therefore not claimed.
- Next implementation phase: component inventory and CSS ownership mapping, then controlled visual changes after a local browser baseline is available.
