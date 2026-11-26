# PLD Beta 0.1.0 — release checklist

**Release branch:** `release/beta-0.1.0`  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head at this audit:** `67385faf55623f0f20bc07511e9e05fdf1aeb15a`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish the Beta until the scope is approved, the release commit is validated, and the presentation/deployment checks are completed.

### Integration and scope
- [x] Beta is based on current main: 57 commits ahead, 0 behind.
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: CI passes on head `9d674df`, but the branch diverges (17 ahead / 41 behind Beta); refresh and review before integration.
- [ ] PR #229 Learning Paths: CI passes on head `2b97957`, but the branch diverges (28 ahead / 9 behind Beta); refresh and review before integration.
- [ ] Decide whether PR #227 Pentest Lab is in scope. It is UI-only and does not run Docker labs or real scans.
- [ ] Record included/excluded scope in release notes.

### Quality and security
- [x] CI #649 passed on Beta head `67385fa`: backend, courses, E2E and WebKit.
- [x] Progress-sync fix commit `f7ffc753` passed CI #641.
- [ ] Re-run CI after this checklist update and confirm it passes on the new exact head.
- [ ] Review dependency/security findings and unresolved Dependabot PRs.
- [ ] Review secrets, debug flags, unsafe defaults and personal data.
- [ ] Manual accessibility and responsive review.
- [ ] Smoke test the public demo.

### Presentation and release
- [ ] README and setup instructions match the release candidate.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy and legal/privacy notices reviewed.
- [ ] Demo works without exposing or altering real user progress.
- [ ] Tag the exact validated commit (version name to confirm).
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Keep `main` unchanged until release approval and an explicit merge plan.

## PR status — verified 2026-11-26

| PR | State | Target | Evidence / next action |
|---|---|---|---|
| #224 Programming Path | Merged | Beta | Merge commit `1c104b38`; CI on Beta head #649 passed. |
| #223 PLD ACADEMY | Draft | Beta | Head `9d674df`; 17 ahead / 41 behind (diverged). CI #648 passed; Deployment Check #331 passed. No reviews. Refresh against Beta and review before integration. |
| #229 Learning Paths | Draft | Beta | Head `2b97957`; 28 ahead / 9 behind (diverged). CI #646 passed; Deployment Check #330 passed. No reviews. Refresh against Beta and review before integration. |
| #227 Pentest Lab | Draft | Main | CI #623 failed in AI Academy routing test; Deployment Check #310 passed. Scope decision pending. |

### Obsolete PRs
PRs #207, #209, #101, #193 and #203 are closed without merge. Do not reopen; replacement work is tracked in current PRs.

### Other open work not integrated into Beta
Open PRs include #205 (AI tutor documentation), #201 (Roadmaps), #199 (AI Academy), #196/#195 (DAW Coach), #186–#183 (hardening/deploy fixes), #180 (NEXARO integration), #175 (Demo Edition), #157 (academic traceability), #146 (DevOps Academy), #102 (brand transition), #95 (project memory), #63 (legal notice), and Dependabot #126–#133. These require individual review; their presence does not mean they are in Beta.

## Security, data and branch notes

- The progress-sync fix handles unknown document versions by reading/merging before PUT and treats HTTP 428 as a version conflict. It was ported to Beta; CI #641 passed on that commit.
- Academy's local demo data is synthetic and stored in namespaced localStorage. The branch escapes stored fields. CI #648 passed its hostile-storage test, but this prototype has no server-side tenancy, institutional authentication, permission enforcement, audit trail or real student-data safeguards.
- Learning Paths aggregate existing course/concept progress read-only. No new XP or lesson-progress store is intended.
- Pentest Lab is a dashboard prototype, not an operational lab or scanner.
- Main and Beta both report `protected:false`; rulesets are not configured. Configure required PR reviews/checks, prevent force-push and deletion before release.
- `beta/programming-path-rebased` has 0 unique commits ahead of Beta and is 28 behind; it is redundant in terms of commit ancestry, but branch deletion is unavailable through the current connector. Other beta port branches diverge and have unique commits; preserve them pending file-level review.

## Release limitations to disclose

Do not describe Academy as production multi-tenant, Pentest Lab as real scanning, or local demo data as server-persisted student records. State which modules are prototypes, what data is synthetic, and which tests were run on the exact candidate.

## Audit record

- Main was not modified.
- No merge beyond the already merged #224, branch deletion, force-push, tag, release or production deployment was performed during this audit.
- CI #648 passed on Academy head `9d674df`; CI #646 passed on Learning Paths head `2b97957`; CI #649 passed on Beta head `67385fa`. The checklist update creates a new Beta commit and requires a new CI run.
