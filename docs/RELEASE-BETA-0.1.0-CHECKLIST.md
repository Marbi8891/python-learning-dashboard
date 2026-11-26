# PLD Beta 0.1.0 — release checklist

**Release branch:** `release/beta-0.1.0`  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head at this audit:** `16bc225e59ef855f47ce3e6d34d74b7a1dc948a5`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish the Beta until all required checks pass on the exact release commit and the scope is approved.

### Integration and scope
- [x] Beta is based on current main: 56 commits ahead, 0 behind.
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] Review/integrate PR #223 Academy after its current CI succeeds and branch is refreshed against Beta.
- [ ] Review/integrate PR #229 Learning Paths after refreshing it against Beta and rerunning CI.
- [ ] Decide whether PR #227 Pentest Lab is in scope. It is UI-only; it does not run Docker labs or real scans.
- [ ] Record included/excluded scope in final release notes.

### Quality and security
- [x] CI #647 passed on Beta head `16bc225`: backend, courses, E2E and WebKit.
- [x] Progress-sync fix commit `f7ffc753` passed CI #641 (all four jobs).
- [ ] Run CI on the exact commit after this checklist update.
- [ ] Backend tests/coverage, frontend unit tests, curriculum validation and E2E pass on release candidate.
- [ ] Security/dependency checks reviewed; no unreviewed blockers.
- [ ] Check for secrets, debug flags, unsafe defaults and personal data.
- [ ] Accessibility and responsive review completed.
- [ ] Smoke test the public demo.

### Presentation and release
- [ ] README and setup instructions match the candidate.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy and legal/privacy notices reviewed.
- [ ] Demo works without exposing or altering real user progress.
- [ ] Tag the exact validated commit (version name to confirm).
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Keep `main` unchanged until release approval and an explicit merge plan.

## Current PR status — 2026-11-26

| PR | State | Target | Evidence / next action |
|---|---|---|---|
| #224 Programming Path | Merged | Beta | Merge commit `1c104b38`; CI on the current Beta head #647 passed. |
| #223 PLD ACADEMY | Draft | Beta | Head `9d674df`; 17 ahead / 40 behind Beta (diverged). CI #644 failed (603 passed, 1 failed); the hostile-storage test fixture was corrected and CI #648 is running. Deployment Check #331 is running. |
| #229 Learning Paths | Draft | Beta | Head `2b97957`; 28 ahead / 8 behind Beta (diverged). CI #646 passed; Deployment Check #330 passed. Refresh against Beta and rerun before integration. |
| #227 Pentest Lab | Draft | Main | CI #623 failed in the AI Academy routing test; Deployment Check #310 passed. Scope decision remains pending. |

No reviews are recorded for #223 or #229. Keep both drafts until updated, validated and reviewed.

### Obsolete PRs
PRs #207, #209, #101, #193 and #203 are closed without merge. Do not reopen; keep their replacement work in the current PRs.

### Other open work not integrated into Beta
Open PRs currently include #205 (AI tutor documentation), #201 (Roadmaps), #199 (AI Academy), #196/#195 (DAW Coach), #186–#183 (hardening/deploy fixes), #180 (NEXARO integration), #175 (Demo Edition), #157 (academic traceability), #146 (DevOps Academy), #102 (brand transition), #95 (project memory), #63 (legal notice), and Dependabot #126–#133. They require individual review; their presence does not mean they are in Beta.

## Security, data and branch notes

- The progress-sync fix handles unknown document versions by reading/merging before PUT and treats HTTP 428 as a version conflict. It was ported to Beta; CI #641 passed on that commit.
- Academy's local demo data is synthetic and stored in namespaced localStorage. The branch escapes stored fields, but the hostile-storage E2E is being revalidated on #648. This prototype has no server-side tenancy, institutional authentication, permission enforcement, audit trail or real student-data safeguards.
- Learning Paths aggregate existing course/concept progress read-only. No new XP or lesson-progress store is intended.
- Pentest Lab is a dashboard prototype, not an operational lab or scanner.
- Main and Beta both report `protected:false`; the rulesets API returned none. Branch-protection details could not be read (403). Configure required PR reviews/checks, prevent force-push and deletion before release.
- `beta/programming-path-rebased` is a deletion candidate (no unique commits ahead of Beta in the previous comparison). Other beta port branches diverge and have unique commits; preserve them pending file-level review. Branch deletion is unavailable through the current connector.

## Release limitations to disclose

Do not describe Academy as production multi-tenant, Pentest Lab as real scanning, or local demo data as server-persisted student records. State which modules are prototypes, what data is synthetic, and which tests were run on the exact candidate.

## Audit record

- Main was not modified.
- No PR merge beyond the already merged #224, branch deletion, force-push, tag, release or production deployment was performed during this audit.
- Latest verified CI is tied to the commits listed above; do not extrapolate results to later commits until their runs finish.
