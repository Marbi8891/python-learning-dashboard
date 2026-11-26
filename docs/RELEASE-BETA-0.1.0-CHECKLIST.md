# PLD Beta 0.1.0 — release checklist

**Release branch:** `release/beta-0.1.0`  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head at this audit:** `e987f7649ac7e30c784b4d07855316319a701669`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish Beta until scope is approved, the exact candidate commit has CI green, and manual deployment/presentation checks are completed.

### Integration and scope
- [x] Beta is based on current main: 58 commits ahead, 0 behind.
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: draft; head `9d674df`, 17 commits ahead / 42 behind Beta. CI #648 and Deployment Check #331 passed. No reviews. Refresh against Beta and review before integration.
- [ ] PR #229 Learning Paths: draft; head `2b97957`, 28 commits ahead / 10 behind Beta. CI #646 and Deployment Check #330 passed. No reviews. Refresh against Beta and review before integration.
- [ ] Decide whether PR #227 Pentest Lab is in scope. Draft against main; CI #623 failed in the AI Academy routing test. Deployment Check #310 passed. The feature is UI-only and does not run Docker labs or real scans.
- [ ] Record included/excluded scope in release notes.

### Quality and security
- [x] CI #650 passed on Beta head `e987f76`: backend, courses, E2E and WebKit.
- [x] Progress-sync fix commit `f7ffc753` passed CI #641.
- [ ] Review dependency/security findings and unresolved Dependabot PRs.
- [ ] Review secrets, debug flags, unsafe defaults and personal data.
- [ ] Manual accessibility and responsive review.
- [ ] Smoke test the public demo.
- [ ] Re-run CI after any further changes and confirm it passes on the exact release candidate.

### Presentation and release
- [ ] README and setup instructions match the release candidate.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy and legal/privacy notices reviewed.
- [ ] Demo works without exposing or altering real user progress.
- [ ] Create a Beta tag on the exact validated commit; tag name to confirm.
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Keep main unchanged until release approval and an explicit merge plan.

## PR status — verified 2026-11-26

| PR | State | Target | Evidence / next action |
|---|---|---|---|
| #224 Programming Path | Merged | Beta | Merge commit `1c104b38`; CI #650 on current Beta passed. |
| #223 PLD ACADEMY | Draft | Beta | Head `9d674df`; 17 ahead / 42 behind (diverged). CI #648 passed; Deployment Check #331 passed. No reviews. Refresh and review before integration. |
| #229 Learning Paths | Draft | Beta | Head `2b97957`; 28 ahead / 10 behind (diverged). CI #646 passed; Deployment Check #330 passed. No reviews. Refresh and review before integration. |
| #227 Pentest Lab | Draft | Main | CI #623 failed in `ai-academy-routing.test.mjs`: the test expects a lazy loader expression that is absent from main. Deployment Check #310 passed. Scope decision pending. |

### Obsolete PRs
PRs #207, #209, #101, #193 and #203 are closed without merge. Do not reopen; replacement work is tracked in current PRs.

### Other open work not integrated into Beta
Open PRs include #205 (AI tutor documentation), #201 (Roadmaps), #199 (AI Academy), #196/#195 (DAW Coach), #186–#183 (hardening/deploy fixes), #180 (NEXARO integration), #175 (Demo Edition), #157 (academic traceability), #146 (DevOps Academy), #102 (brand transition), #95 (project memory), #63 (legal notice), and Dependabot #126–#133. Review each separately; their presence does not mean they are in Beta.

### Dependency PR checks
- #126 Python 3.15, #127 Playwright, #129 Ruff, #130 Alembic, #131 pytest-cov, #132 SQLAlchemy, #133 FastAPI: checks reported green on their heads.
- #128 axe-core Playwright: E2E and WebKit fail with serious `label-content-name-mismatch` on the brand links. Fix and rerun before merging.

### Hardening PR checks
- #183 Pages deploy-job split, #184 verified-exam concurrency and #186 state-document versioning: checks passed on the recorded heads.
- #185 Python runtime isolation: E2E failed in the same AI Academy routing assertion; backend, courses and WebKit passed. Investigate and rerun before merge.

## Security, data and branch notes

- Main and Beta report `protected:false`; the repository rulesets endpoint returned an empty list. Detailed branch-protection access is denied to the current integration (403). Configure required PR reviews/checks, prevent force-push and deletion before release.
- The progress-sync fix reads/merges before PUT when the document version is unknown and treats HTTP 428 as a version conflict. It is in Beta; CI #641 passed on that commit.
- Academy demo data is synthetic and namespaced in localStorage. Stored values are escaped. The prototype has no server-side tenant isolation, institutional authentication, permission enforcement, audit trail or real student-data safeguards.
- Learning Paths aggregate existing course/concept progress read-only. No new XP or lesson-progress store is intended.
- Pentest Lab is a dashboard prototype, not an operational lab or scanner.
- `v1.0.0` tag exists (tagged 2026-09-29) and points to `fdf6409`, 324 commits behind main and 382 behind Beta. No GitHub Releases are published. This tag is not the Beta candidate; do not move or reuse it.
- `beta/programming-path-rebased` has 0 unique commits ahead of Beta and is 29 behind; it is redundant in commit ancestry. Branch deletion is unavailable through the current connector.
- Other old Beta port branches diverge and contain unique commits. Preserve pending file-level review: Academy port (11 ahead/46 behind), AI Academy port (16/52), hardening-rebased (19/49), port-hardening (22/53), port-pld003 (14/53), Programming Path port (18/46).

## Release limitations to disclose

Do not describe Academy as production multi-tenant, Pentest Lab as real scanning, or local demo data as server-persisted student records. State which modules are prototypes, what data is synthetic, and which tests ran on the exact candidate.

## Audit record
- Main remains at `be801c5`; no change to main.
- Beta head `e987f76`; CI #650 passed on that exact commit.
- Checklist update is the only change made in this audit run; its new commit requires a new CI run.
- No merge, branch deletion, force-push, new tag, GitHub Release or production deployment performed.
