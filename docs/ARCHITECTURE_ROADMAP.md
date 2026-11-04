# Python Learning Dashboard — Architecture Roadmap

**Status:** Proposed target architecture  
**Date:** 2026-11-02  
**Principle:** Evolve the existing system incrementally; preserve working behaviour and learner data.

## 1. Current documented architecture

According to the repository README:

- **Frontend:** HTML, CSS and JavaScript ES modules, served through GitHub Pages.
- **Code runner:** Pyodide in a Web Worker, with a timeout and network APIs disabled in the worker.
- **Backend:** Python and FastAPI, with SQLAlchemy and Alembic.
- **Data:** PostgreSQL (Neon) in production and SQLite for local development.
- **Identity:** optional email and Google login; session cookie and CSRF-related request header are described in the README.
- **Content:** version-controlled files under `frontend/data/`, generated/checked by scripts.
- **Delivery:** GitHub Actions, GitHub Pages, Render/Docker and automated unit, backend and E2E tests.

The README explicitly notes that a Web Worker is not a complete security sandbox because code runs within the web origin. Do not treat disabling network APIs as a complete isolation boundary.

## 2. Target architecture

Keep a modular monolith for the API and a static frontend/PWA. Introduce boundaries by domain before considering separate deployable services.

```text
Learner browser
  ├── Static web/PWA: HTML + CSS + ES modules
  │     ├── Learn / course navigation
  │     ├── Practice / code runner
  │     ├── Assess / quizzes and exams
  │     ├── Progress / review and recommendations
  │     └── Account / preferences and data controls
  ├── Web Worker + Pyodide for supported Python exercises
  └── HTTPS API (FastAPI)
        ├── Identity and account
        ├── Course and content metadata
        ├── Attempts and assessment results
        ├── Progress and review scheduling
        ├── Recommendations
        └── Future billing / organisation features
              |
          PostgreSQL
```

Content authoring and validation pipeline:

```text
Version-controlled course files
  -> schema validation
  -> exercise/code and answer validation
  -> curriculum/source/licence checks
  -> review approval
  -> versioned release
```

This is a target design. Do not infer that all modules or the pipeline already exist.

## 3. Architecture decisions

### ADR-001 — Keep the existing frontend
**Decision:** Continue with vanilla JavaScript ES modules for now.  
**Reason:** The current app is built around this stack; a rewrite adds migration risk without proving learner value.  
**Revisit if:** measured maintainability or team constraints show a framework migration is cheaper than continued incremental work.

### ADR-002 — Keep FastAPI as a modular monolith
**Decision:** Keep one API deployment and separate domains in code.  
**Reason:** Current scale and team size do not justify distributed operations.  
**Revisit if:** an independently scaling or independently secured workload has a clear operational case.

### ADR-003 — Keep browser-based Python execution
**Decision:** Use Pyodide/Web Workers for suitable exercises.  
**Reason:** Avoids per-execution server costs and local installation.  
**Constraint:** It is not a complete security boundary. Keep restrictive CSP/origin controls, test runner behaviour and avoid executing untrusted code in privileged contexts. Server-side execution requires a separate isolation design.

### ADR-004 — Treat course content as versioned data
**Decision:** Use a documented schema and stable IDs for courses, lessons, objectives, exercises, answer keys, difficulty, source, licence, version and review status.  
**Reason:** Supports validation, localisation and additional learning paths without hard-coding every course into UI logic.

### ADR-005 — Make progress sync conflict-safe
**Decision:** Define a canonical event/attempt model, stable IDs, idempotent writes, timestamps/versioning and deterministic conflict resolution. Preserve existing records during migrations.  
**Reason:** Avoid lost progress across devices or tabs.  
**Constraint:** Do not treat client-reported XP or scores as trustworthy for paid exams, verified achievements or other high-stakes outcomes. Validate those server-side.

### ADR-006 — Use transparent recommendations first
**Decision:** Begin with explainable rules based on attempts, correctness, recency, difficulty and review intervals.  
**Reason:** Easier to test and explain than an unvalidated AI system.  
**Revisit if:** measured outcomes show a need for more advanced personalisation.

## 4. Domain boundaries

Keep modules small and aligned to these responsibilities:

- **Identity:** authentication, sessions, account recovery, export and deletion.
- **Content:** course catalogue, versions, prerequisites, objectives and publication status.
- **Practice:** exercise definitions, attempts and feedback.
- **Assessment:** quiz/exam sessions, scoring rules and reviewed answer keys.
- **Progress:** mastery evidence, review scheduling and history.
- **Recommendations:** next-step rules, reason codes and evaluation.
- **Analytics:** privacy-minimised product events and aggregate metrics.
- **Billing (future):** entitlements, subscription state, invoices/payment-provider references and cancellation.

Avoid duplicating course content in database tables and static files without a defined source of truth. Keep content files as the canonical source initially; store user-specific attempts and progress in the database.

## 5. Data model direction

Do not implement every entity at once. Evolve from current models with migrations and tests.

Candidate concepts:
- Course, CourseVersion, Lesson, LearningObjective, Exercise, ContentSource
- User, Session, Attempt, AssessmentSession, AssessmentResult
- ProgressSnapshot or derived progress view, ReviewItem
- ProductEvent with minimised fields and retention policy
- Future: Organisation, Membership, Group, Assignment, SubscriptionEntitlement

Stable content IDs and version identifiers are important so historical attempts remain interpretable after a lesson changes. Avoid storing unnecessary personal data or raw learner code in analytics.

## 6. API and compatibility

- Keep the existing API prefix and routes unless a migration plan is documented.
- Validate request and response schemas.
- Make state-changing operations idempotent where retries are possible.
- Enforce authorisation on the server, not only in the UI.
- Use pagination and bounded payload sizes for history and reporting.
- Add database migrations with forward/backward compatibility where practical.
- Do not expose production API documentation or debug details unnecessarily.
- Maintain explicit CORS origins, cookie attributes, CSRF protections and rate limits appropriate to deployment topology.

## 7. Security, privacy and accessibility gates

Before a public paid release:
- Review authentication, account recovery, session expiry and logout.
- Test account export/deletion and document deletion propagation to backups where applicable.
- Review rate limiting for multiple API instances; in-memory limits do not coordinate across instances.
- Verify secrets are not committed and rotate any exposed credentials.
- Review dependencies and deployment configuration.
- Test content security policy, cross-origin isolation assumptions and Web Worker behaviour.
- Conduct manual keyboard and screen-reader checks alongside automated accessibility tests.
- Minimise analytics, set retention periods and document vendors/processors.
- Review applicable GDPR/LOPDGDD, LSSI-CE, consumer and accessibility obligations with qualified advice before selling.

## 8. Observability and reliability

Add structured logs and basic metrics without logging credentials, session tokens, full learner code or unnecessary personal data. Track:
- API error rates and latency,
- login/recovery failures and rate limiting,
- sync conflicts and failed writes,
- frontend runtime errors,
- runner timeout/error rates,
- content-validation failures,
- deployment health and database backup/restore status.

Define alert thresholds only after collecting a baseline. Test database restoration rather than assuming backups are usable.

## 9. Implementation order

1. Audit current implementation and close data-loss/security regressions.
2. Add regression tests for sync, account flows and runner timeouts.
3. Document and validate the content schema.
4. Add stable content/version metadata and validation in CI.
5. Add privacy-minimised analytics.
6. Implement transparent recommendations.
7. Validate demand before billing or multi-tenant organisation features.
8. Revisit infrastructure only when measured load or reliability requires it.

## 10. Definition of done for architecture changes

A change is ready when:
- Existing learner progress is preserved.
- Relevant unit, API and E2E tests pass.
- Migrations and rollback/recovery implications are documented.
- Authentication/authorisation and privacy effects are reviewed.
- Keyboard and responsive behaviour remain usable.
- Operational configuration and failure behaviour are documented.
- The PR states the user problem and the evidence for the change.
