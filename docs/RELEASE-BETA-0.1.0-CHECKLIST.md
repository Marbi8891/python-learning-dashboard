# PLD Beta 0.1.0 — release checklist

**Updated:** 2026-11-27 05:30 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head before this document refresh:** `e415c92586afddc09c4a8c5fd28854cd7798a7a2`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish Beta until the included scope is approved, CI is green on the exact candidate commit, and manual demo/accessibility checks are completed.

## Scope and PR status

- [x] Beta is based on main: 70 commits ahead, 0 behind.
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: draft, head `9d674df`, 17 ahead / 54 behind Beta. CI #45890668077 and Deployment Check #45890668052 passed on this head. No approvals. Refresh against Beta, inspect overlap/conflicts, then rerun checks. Prototype is synthetic/localStorage only; no tenant isolation, institutional auth, server persistence or permissions.
- [ ] PR #229 Learning Paths: draft, head `88b9434`, 32 ahead / 22 behind Beta (merge base `c31244a`). CI #45934058607 failed at E2E; backend, courses and WebKit jobs passed. Deployment Check #45934058622 passed. Playwright report artifact exists, but the available connector cannot download it to inspect the failing assertion. Rerun of failed jobs is in progress; result pending. No approvals. Review read-only progress adapters and shared frontend files; update/integrate sequentially, not in parallel.
- [ ] PR #227 Pentest Lab: draft against main, head `67ca9b2`, 16 ahead / 0 behind main. Latest CI #45851158102 failed in frontend unit tests (step 8); backend, courses and WebKit passed; E2E was skipped. Deployment Check #45851158126 passed. Rerun was attempted and failed at the same step; details are unavailable through the connector. Stop reruns until the failing assertion is inspected. Decide scope; UI only, no Docker execution or real scans.
- [x] Obsolete PRs #207, #209, #101, #193 and #203 remain closed without merge.

## CI evidence

- [x] Exact Beta head `e415c925`: CI #45934210432 passed all four jobs (backend, courses, E2E and WebKit). https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45934210432
- [ ] PR #229: run #45934058607 failed E2E; rerun accepted and in progress, pending result. Deployment check passed.
- [x] PR #223: run #45890668077 passed all four jobs; deployment check #45890668052 passed. This does not validate against current Beta.
- [ ] PR #227: run #45851158102 failed frontend unit tests; rerun failed at the same step. Inspect output before another retry. Deployment check passed.
- [ ] Main: last full CI recorded in previous audit failed AI Academy routing (569/570 tests); not rechecked this run. Current CI-monitor runs on main are green but are not full-suite evidence.
- [ ] Fix/retest AI Academy routing failure on #227 and related hardening PR before considering those branches.
- [ ] Verify Dependabot heads before merging. Latest known: #126, #127, #129–#133 had green checks; #128 had one green and one failed check (accessibility issue previously reported as serious `label-content-name-mismatch`). #185 runtime isolation also had one green and one failed check. #183, #184 and #186 had green checks in the last queried runs.

## Security and release quality

- [x] Workflow review from prior audit: CI uses read-only contents permissions, checkout with `persist-credentials: false`, backend `pip-audit`, frontend `npm audit --audit-level=high`. Recheck workflow changes before release.
- [ ] Review current dependency findings, secrets, debug settings, unsafe defaults and privacy notices on release candidate.
- [ ] Manual accessibility, responsive and public-demo smoke test.
- [ ] Confirm that demo walkthrough does not touch real account/progress data.

## Main and branches

- Main remains at `be801c5`; no writes made.
- Branch listing paginated: 106 branches (100 on page 1, 6 on page 2). All returned branches report `protected:false`; main and Beta are unprotected. Rulesets endpoint returned an empty list. Branch-protection detail endpoint is forbidden to the connector; no settings changed.
- PR #223: 17 ahead / 54 behind Beta; PR #229: 32 ahead / 22 behind Beta. Both overlap on app navigation, index, precache and English translations; inspect conflicts and integrate sequentially.
- `beta/programming-path-rebased` compares 0 ahead / 41 behind Beta, with no unique commits in ancestry; redundant candidate. No branch-deletion tool is available, so it was not deleted.
- Other beta-port branches diverge and retain unique commits; preserve until their commits/files are reviewed. No branch deletions or force-pushes performed.

## Presentation and release

- [ ] README, setup instructions and changelog reflect the final included scope.
- [ ] Screenshots are current and contain no personal data.
- [ ] Spanish/English copy, legal and privacy notices reviewed.
- [ ] Demo walkthrough works without touching real progress/account data.
- [ ] Manual smoke test of published Pages site.
- [ ] Create a new Beta tag on the exact validated commit (name to approve); do not move/reuse `v1.0.0`.
- [ ] Publish GitHub Release with notes, known limitations and demo link.
- [ ] Main stays unchanged until explicit release/merge approval.

## Known limitations to disclose

Academy is a local demo with synthetic data, not a production multi-tenant institution service. Learning Paths aggregates existing progress read-only; no duplicate lesson/XP store is intended. Pentest Lab is a planning dashboard, not a working scanner/lab. State which checks ran against the exact release candidate.

## Audit record — 2026-11-27 05:30 CET

- Main `be801c5` unchanged. Beta `e415c925` is 70 ahead / 0 behind main and its exact-head CI #45934210432 passed all four jobs.
- #229 CI #45934058607 failed E2E on head `88b9434`; failure details could not be retrieved. Rerun accepted and is currently in progress. Deployment check passed.
- #227 CI #45851158102 failed in frontend unit tests; rerun failed at the same step. The connector does not provide test output; no more retries until inspected. Deployment check passed.
- #223 CI and deployment check passed on `9d674df`; it remains 17 ahead / 54 behind Beta, draft, without approval.
- #224 is merged. No further integration.
- PR reviews: #223/#227 none; #229 has COMMENTED reviews only, no approval.
- No merge, branch deletion, force-push, tag, release or production deployment performed.
