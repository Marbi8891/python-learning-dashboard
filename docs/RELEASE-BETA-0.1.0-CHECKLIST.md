# PLD Beta 0.1.0 — release checklist

**Updated:** 2026-11-27 06:53 CET (CI rerun checked)  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta head before this document refresh:** `18406e9a258a7075d01be1e751389ee72fe0fcd2`  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not tag or publish Beta until the included scope is approved, CI is green on the exact candidate commit, and manual demo/accessibility checks are completed.

## Scope and PR status

- [x] Beta is based on main: 73 commits ahead, 0 behind.
- [x] PR #224 Programming Path merged to Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] PR #223 Academy: draft, head `9d674df`, 17 ahead / 56 behind Beta. CI #45890668077 and Deployment Check #45890668052 passed on this head. No approvals. Refresh against Beta, inspect overlap/conflicts, then rerun checks. Prototype is synthetic/localStorage only; no tenant isolation, institutional auth, server persistence or permissions.
- [ ] PR #229 Learning Paths: draft, head `88b9434`, 32 ahead / 24 behind Beta (merge base `c31244a`). CI #45934058607 failed E2E on `Learning Paths selection is optional and persisted locally`: after `page.reload()`, `#paths-view` remained empty. I downloaded and inspected the Playwright artifact; both first attempt and retry show the same failure. Rerun of the failed E2E job is accepted and in progress. Deployment Check #45934058622 passed. No approvals. Review read-only progress adapters and shared frontend files; update/integrate sequentially, not in parallel.
- [ ] PR #227 Pentest Lab: draft against main, head `67ca9b2`, 16 ahead / 0 behind main. Latest CI #45851158102 failed frontend unit tests at `ai-academy-routing.test.mjs`: it asserts the AI Academy loader/view is present, but `main`'s `frontend/js/app.js` does not contain that loader. This is a baseline/main mismatch, not a Pentest Lab test. Backend, courses and WebKit passed; E2E was skipped. Deployment Check #45851158126 passed. No further rerun requested. Decide scope; UI only, no Docker execution or real scans.
- [x] Obsolete PRs #207, #209, #101, #193 and #203 remain closed without merge.

## CI evidence

- [x] Historical exact Beta head `e415c925`: CI #45934210432 passed all four jobs. Current code candidate `5754170`: CI #45940620642 first attempt failed WebKit smoke test `e2e/landing.spec.js` at `#/portada/como-funciona` (URL remained `#/portada`, marked flaky); failed-job rerun then passed all four jobs. This validates `5754170`, not the newest document commit `18406e9`. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45940620642
- [ ] PR #229: run #45934058607 failed after reload because the Paths view remained blank; artifact confirms the same failure on retry. E2E rerun is accepted and in progress. Deployment check passed.
- [x] PR #223: run #45890668077 passed all four jobs; deployment check #45890668052 passed. This does not validate against current Beta.
- [ ] PR #227: run #45851158102 failed a unit assertion requiring the AI Academy loader that is absent from main; this unrelated baseline mismatch blocks CI. Deployment check passed.
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
- PR #223: 17 ahead / 56 behind Beta; PR #229: 32 ahead / 24 behind Beta. Both overlap on app navigation, index, precache and English translations; inspect conflicts and integrate sequentially.
- `beta/programming-path-rebased` compares 0 ahead / 43 behind Beta, with no unique commits in ancestry; redundant candidate. No branch-deletion tool is available, so it was not deleted.
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

## Audit record — 2026-11-27 06:53 CET (rerun results)

- Main `be801c5` unchanged. Beta `18406e9` is 73 ahead / 0 behind main; the latest change is checklist-only. No check result for this exact commit is available through the connector.
- CI #45940620642 rerun passed all four jobs on code commit `5754170` (backend, courses, E2E and WebKit). The first WebKit attempt was flaky on the landing route `#/portada/como-funciona`; rerun passed.
- #229 CI #45934058607: backend, courses and WebKit passed in the rerun; E2E remains in progress. The failed attempt's artifact confirms the selection-persistence test leaves `#paths-view` blank after reload. The failed-job rerun is still running; no code changes made.
- #227 CI #45851158102 fails an existing routing assertion requiring an AI Academy loader absent from `main`; unrelated to Pentest Lab. Deployment Check passed.
- #223 remains draft, 17 ahead / 56 behind Beta; CI #648 and Deployment Check passed on head; no reviews. #224 remains merged. #229 has COMMENTED reviews only, no approval; #227 no reviews.
- PRs #207, #209, #101, #193 and #203 remain closed without merge.
- Branch inventory: 106 total; redundant Programming Path rebase is 0 ahead / 43 behind.
- No merge, branch deletion, force-push, tag, release or production deployment performed.
