# PLD Beta 0.1.0 — release checklist

**Audit updated:** 2026-11-27 02:31 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head at start of this audit update:** `6bc9bf8d33ec0e8a793ad50716157aa93011ce7a`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish Beta until scope is approved, CI is green on the exact candidate commit, and manual deployment/presentation checks are completed.

### Integration and scope
- [x] Beta is based on current main: 62 commits ahead, 0 behind (before this audit-document commit).
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: draft; head `9d674df`, 17 commits ahead / 46 behind Beta (diverged). CI #648 and Deployment Check #331 passed. No reviews. Refresh, inspect diff/conflicts, and rerun CI before integration.
- [ ] PR #229 Learning Paths: draft; head `2b97957`, 28 commits ahead / 14 behind Beta (diverged). CI #646 and Deployment Check #330 passed. No reviews. Refresh, inspect adapters/routes, and rerun CI before integration.
- [ ] Decide whether PR #227 Pentest Lab is in scope. Draft against main; CI #623 failed in the AI Academy routing test. Deployment Check #310 passed. It is UI-only and does not execute Docker labs or real scans.
- [ ] Record included/excluded scope in release notes.

### Quality and security
- [x] CI #654 passed on the exact current Beta head `6bc9bf8`: backend, courses, E2E and WebKit. CI #653 also passed on `9ac1866`.
- [x] CI #650 passed on prior Beta head `e987f76`.
- [x] Progress-sync fix `f7ffc753` passed CI #641.
- [ ] Review dependency/security findings and unresolved Dependabot PRs.
- [ ] Review secrets, debug flags, unsafe defaults and personal data.
- [ ] Manual accessibility and responsive review.
- [ ] Smoke test the public demo.
- [ ] CI #652 failed on `1c9163f` in E2E. Logs report one flaky test (`e2e/dashboard.spec.js`, alumno nuevo: progreso se actualiza y persiste); the failing assertion was the chart SVG aria-label expecting `/1 actividad/` (line 92). Runs #653 on `9ac1866` and #654 on `6bc9bf8` both passed with 285 E2E tests. Compare `1c9163f...9ac1866` shows only a checklist change, so this appears intermittent; root cause remains unconfirmed. Monitor rather than weaken the test.
- [x] CI #653 completed successfully on `9ac1866`; CI #654 completed successfully on the exact Beta head `6bc9bf8`. This checklist update creates a new commit, so its CI remains pending.
- [ ] Review current-main CI failure: run #45500809581 E2E had 569/570 tests pass; the failed test expects the AI Academy loader expression that is absent from main. Backend, courses and WebKit passed. The Pages/config/Docker run #45500809865 passed.

### Presentation and release
- [ ] README and setup instructions match the release candidate.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy and legal/privacy notices reviewed.
- [ ] Demo works without exposing or altering real user progress.
- [ ] Create a Beta tag on the exact validated commit; tag name to confirm.
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Keep main unchanged until release approval and an explicit merge plan.

## PR status — verified 2026-11-27

| PR | State | Target | Evidence / next action |
|---|---|---|---|
| #224 Programming Path | Merged | Beta | Merge commit `1c104b38`; current Beta CI #654 passed. |
| #223 PLD ACADEMY | Draft | Beta | Head `9d674df`; 17 ahead / 46 behind. CI #648 and Deployment Check #331 passed; no reviews. Refresh and review before integration. |
| #229 Learning Paths | Draft | Beta | Head `2b97957`; 28 ahead / 14 behind. CI #646 and Deployment Check #330 passed; no reviews. Refresh and review before integration. |
| #227 Pentest Lab | Draft | Main | CI #623 failed in `ai-academy-routing.test.mjs`: the test expects a loader expression absent from main. Deployment Check #310 passed. Scope decision pending. |

### Obsolete PRs
PRs #207, #209, #101, #193 and #203 are closed without merge. Do not reopen; replacement work is tracked separately.

### Other open PRs
There are 27 open PRs. Apart from #223/#227/#229, the backlog includes #205 AI tutor documentation, #201 Roadmaps, #199 AI Academy, #196/#195 DAW Coach, #183–#186 hardening/deploy fixes, #180 NEXARO integration, #175 Demo Edition, #157 academic traceability, #146 DevOps Academy, #102 brand transition, #95 project memory, #63 legal notice and Dependabot #126–#133. Review independently; open does not mean included in Beta.

### Dependency PR checks (last recorded)
- #126 Python, #127 Playwright, #129 Ruff, #130 Alembic, #131 pytest-cov, #132 SQLAlchemy and #133 FastAPI: last recorded checks were green; verify current heads before merge.
- #128 axe-core Playwright: last recorded E2E/WebKit failure reported serious `label-content-name-mismatch` on brand links. Fix and rerun.

### Hardening PR checks (last recorded)
- #183 Pages deploy-job split, #184 verified-exam concurrency and #186 state-document versioning: last recorded checks passed on their heads.
- #185 Python runtime isolation: last recorded E2E failure was the AI Academy routing assertion; backend, courses and WebKit passed. Recheck the current head.

## Security, data and branch notes
- Main and Beta report `protected:false`; repository rulesets endpoint returns an empty list. Detailed branch-protection API access is denied to the current integration (403). Configure required PR reviews/checks and prevent force-push/deletion before release.
- Progress-sync fix reads/merges before PUT when the document version is unknown and treats HTTP 428 as a version conflict. It is in Beta; CI #641 passed on that commit.
- Academy demo data is synthetic and namespaced in localStorage. Stored values are escaped. The prototype has no server-side tenant isolation, institutional authentication, permission enforcement, audit trail or real student-data safeguards.
- Learning Paths aggregate existing progress read-only. No new XP or lesson-progress store is intended.
- Pentest Lab is a dashboard prototype, not an operational lab or scanner.
- Tag `v1.0.0` is annotated but unsigned, dated 2026-09-29, and points to `fdf6409`. Compare confirms main is 324 commits ahead of the tag and Beta is 386 commits ahead. No GitHub Releases are published. Do not reuse or move it for Beta.
- There are 106 branch refs. `beta/programming-path-rebased` has 0 unique commits ahead and is 33 behind; it is redundant in ancestry. Deletion is unavailable through the current connector.
- Other old Beta port branches diverge and retain unique commits: Academy port (11/50), AI Academy port (16/56), hardening-rebased (19/53), port-hardening (22/57), port-pld003 (14/57), Programming Path port (18/50) ahead/behind relative to Beta. Preserve pending file-level review.

## Release limitations to disclose
Do not describe Academy as production multi-tenant, Pentest Lab as real scanning, or local demo data as server-persisted student records. State which modules are prototypes, what data is synthetic, and which tests ran on the exact candidate.

## Audit record
- Main remains at `be801c5`; no changes to main.
- Beta head at start of update `6bc9bf8`; CI #652 failed with an intermittent E2E assertion, but #653 passed on `9ac1866` and #654 passed on this exact head. The only commit between #652 and #653 changed the checklist; no code fix was made. Root cause remains unknown.
- This checklist update creates a new Beta commit; CI for the new exact head will be pending.
- No merge, branch deletion, force-push, new tag, GitHub Release or production deployment performed.
