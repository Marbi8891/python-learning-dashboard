# PLD Beta 0.1.0 — release checklist

**Updated:** 2026-11-27 04:25 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head before this checklist update:** `130073ff4a0164b1cc6d3869c8548eaa392bb427`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish Beta until the included scope is approved, CI is green on the exact candidate commit, and manual demo/accessibility checks are completed.

## Integration and scope

- [x] Beta is based on `main`: 69 commits ahead, 0 behind (before this document update).
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: draft, head `9d674df`, 17 ahead / 53 behind Beta. CI #648 and Deployment Check #331 passed on that head; no reviews. Refresh against Beta, inspect overlap/conflicts, rerun CI before integration. Prototype uses synthetic localStorage data; no real tenant isolation, institutional auth, backend persistence or permissions.
- [ ] PR #229 Learning Paths: draft, head now `88b9434`, 32 ahead / 21 behind Beta (merge base `c31244a`). CI #659 failed on its prior head `8a7ec94`; fix to test reset is in commit `88b9434`. CI #664 is in progress (courses passed; backend, E2E and WebKit running). Deployment Check #335 passed. No reviews. Review read-only progress adapters and overlap with Academy; integrate sequentially.
- [ ] Decide scope of PR #227 Pentest Lab. Draft against main, head `67ca9b2`, 16 ahead / 0 behind main. CI #623 failed in the AI Academy routing test; Deployment Check #310 passed. UI only; no Docker execution, real scans or live infrastructure.
- [x] Obsolete PRs #207, #209, #101, #193 and #203 remain closed without merge. Replacement work is tracked separately.

## Quality and security

- [ ] CI on the exact current Beta head. CI #655 passed on `63da4a4` (backend, courses, E2E and WebKit); Beta was subsequently updated with documentation. The latest head `954478e` has no workflow run/status returned by the available connector, so it is not verified.
- [ ] Resolve/retest the Learning Paths CI failure. CI #659 failed E2E: 286 passed, one failed. The persistence test's `addInitScript` cleared localStorage on reload, invalidating its own assertion. Corrected in #229 commit `88b9434` using a sessionStorage one-time marker. CI #664 is queued; wait for result. Do not weaken the assertion.
- [x] CI #648 on Academy head passed (backend, courses, E2E, WebKit); Deployment Check #331 passed. This is not validation against current Beta.
- [ ] Fix/retest the AI Academy routing failure on #227 and the related hardening PR before considering those branches.
- [ ] Review current dependency findings. Dependabot #128 last recorded accessibility failure: serious `label-content-name-mismatch` on brand links. Other #126–#127 and #129–#133 had green checks in prior audit; verify current heads before merge.
- [ ] Manual accessibility, responsive and public-demo smoke test.
- [x] Workflow review from prior audit: CI uses read-only contents permissions, checkout with `persist-credentials: false`, backend `pip-audit`, frontend `npm audit --audit-level=high`. Recheck workflow changes before release.
- [ ] Review secrets, debug settings, unsafe defaults and data/privacy notices on the release candidate.

## Main and branches

- Main remains at `be801c5`; no writes made. The last full main CI evidence in the previous audit was run #528, E2E failed in AI Academy routing (569/570 passed). Not rechecked this run.
- Main and Beta were last confirmed unprotected (`protected:false`); rulesets were empty. Detailed branch-protection endpoint returned 403 to the integration. Configure required PRs/reviews/checks and disallow force-push/deletion before release; not changed.
- Current compare before this document update: Beta is 69 ahead / 0 behind main.
- #223 is 17 ahead / 53 behind Beta; #229 is 32 ahead / 20 behind Beta. Their shared frontend files include app navigation, index, precache and English translations; review and integrate sequentially.
- #229's earlier duplicate route rendering was corrected in `2ff0cfc` and `ef1d18d`; E2E coverage added in `8a7ec94`. The malformed-span report was false and withdrawn.
- Branch search for `beta` returned the port branches `academy-institutional-port`, `academy-institutional-rebased`, `ai-academy-port`, `hardening-rebased`, `port-hardening`, `port-pld003`, `programming-path-port`, and `programming-path-rebased`. This search is not a complete repository branch inventory.
- `beta/programming-path-rebased` compares 0 ahead / 39 behind Beta and has no unique commits in ancestry; it is redundant. Deletion was not performed.
- Other port branches diverge; preserve until their unique commits/files are reviewed. No branch deletions or force-pushes performed.

## Presentation and release

- [ ] README, setup instructions and Changelog reflect final included scope.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy, legal and privacy notices reviewed.
- [ ] Demo walkthrough works without touching real progress/account data.
- [ ] Manual smoke test of published Pages site.
- [ ] Create a new Beta tag on the exact validated commit (name to approve); do not move/reuse `v1.0.0`.
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Main stays unchanged until explicit release/merge approval.

## Known limitations to disclose

Academy is a local demo with synthetic data, not a production multi-tenant institution service. Learning Paths aggregates existing progress read-only; no duplicate lesson/XP store is intended. Pentest Lab is a planning dashboard, not a working scanner/lab. State which tests ran against the exact release candidate.

## Audit record — 2026-11-27 04:23 CET

- Main remains unchanged at `be801c5`.
- Beta head at start of this checklist update: `130073ff`, 69 ahead / 0 behind main. No CI status was returned for this exact commit.
- #229 CI #659 failed its persistence-after-reload E2E assertion because the test fixture reset localStorage on each page load. Fix committed on the PR branch as `88b9434`. CI #664 is in progress (courses passed; backend, E2E and WebKit still running); Deployment Check #335 passed. No merge.
- #223 and #227 remain draft. #224 is already merged to Beta.
- No merge, deletion, force-push, tag, release or production deployment performed.
