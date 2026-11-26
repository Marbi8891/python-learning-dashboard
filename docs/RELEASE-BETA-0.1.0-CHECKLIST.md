# PLD Beta 0.1.0 — Release checklist

**Release target:** `release/beta-0.1.0`  
**Repository:** https://github.com/Marbi8891/python-learning-dashboard  
**Public demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not publish or merge the release until every required item below is verified.

### Scope and integration
- [x] Confirm the release branch is based on the current `main` commit (`be801c5afa1c27ba6d5f24695236fe8ee67bdcee`; 0 commits behind at audit time).
- [ ] Review PR #223 (PLD ACADEMY institutional demo) against the updated release branch; it needs rebasing after #224.
- [x] Review and integrate PR #224 (Programming Path) into the release branch.
- [x] Confirm Programming Path reuses existing career-roadmap progress and lesson/resource IDs; it does not create a parallel progress store or duplicate existing lessons.
- [ ] Confirm Academy demo storage isolation and flows in CI/manual review. The prototype uses a namespaced localStorage key and synthetic data, but its CI has failures and it is not production multi-tenant.
- [ ] Decide whether PR #227 (Pentest Lab dashboard) is in Beta scope. It is UI-only; it does not perform real scans or deploy Docker labs.
- [ ] Record included and excluded features in the release notes.

### Quality and security
- [ ] CI is green on the exact release commit.
- [ ] Backend tests and coverage pass on the exact release commit.
- [ ] Frontend unit tests pass on the exact release commit.
- [ ] Playwright E2E tests pass on the exact release commit.
- [ ] Curriculum/content validation scripts pass on the exact release commit.
- [ ] Dependency/security checks have no unreviewed blocking findings.
- [ ] Check secrets, personal data, debug flags, and unsafe demo defaults.
- [ ] Verify authentication, persistence, and demo-mode isolation.
- [ ] Review accessibility (keyboard, focus, responsive layout, WCAG/axe checks).

### Product presentation
- [ ] README has current feature summary, setup instructions, screenshots, demo link, and clear project status.
- [ ] Demo route works without requiring a real account and does not touch real user data.
- [ ] Academy demo explains institutional use and limitations.
- [x] Programming Path is integrated into the Beta branch; runtime/progress smoke test still pending.
- [ ] Screenshots are current and do not expose personal information.
- [ ] Spanish and English copy is checked for consistency.
- [ ] Legal/privacy documentation is current for the features included.

### Release
- [x] Add a provisional Beta 0.1.0 changelog entry; final release notes remain pending validation.
- [ ] Tag the exact validated commit as `v0.1.0-beta` (or agreed version).
- [ ] Publish GitHub Release with notes, known limitations, and demo link.
- [ ] Verify GitHub Pages deployment and smoke-test the public site.
- [ ] Keep `main` unchanged until the release is approved and the merge plan is explicit.

## Current audit notes (2026-11-26)

- PR #207 was closed as superseded by #224.
- PR #209 was closed as superseded by #223.
- PR #101 was closed as superseded by the Programming Path work.
- PR #193 was closed as an older AI Tutor specification.
- PR #203 was closed as outdated relative to the current AI Tutor direction.
- PR #224 merged into `release/beta-0.1.0` at `1c104b3816f82a55bc883b18e8896a5b011c6597`. Its CI jobs (backend, e2e, webkit, courses) and Deployment check were green on the PR head SHA. Post-merge CI on the merge commit is not yet verified.
- PR #223 remains open as draft. Its head is `230dfa2015eed29425f6e282004e04aae85d60a0`; compare against current Beta shows 12 commits ahead and 32 behind (diverged). CI #622 failed in `e2e/learn.spec.js:558` on the PCAP sidebar heading viewport assertion. Deployment Check #309 passed. The branch must be rebased or ported before integration; the connector has no safe branch-rebase/update operation.
- PR #227 remains draft against `main`; scope decision is pending. Head `67ca9b23ace5676e635164a3b0b3356428121038` has CI #623 failed in the new `ai-academy-routing.test.mjs` assertion, which expects an `aiacademy` loader absent from this PR's `app.js`/base. Deployment Check #310 passed. This is an unrelated test/branch-content mismatch; resolve it before marking the PR ready.
- `release/beta-0.1.0` remains based on the current `main` SHA and is ahead of it; `main` was not modified. The Academy PR base is stale and requires rebase/porting.
- There are still several open PRs targeting `main`; they are not considered integrated into the Beta unless separately ported/reviewed.

## Known limitations to disclose

- Do not describe Pentest Lab as an actual scanning or Docker lab platform unless real execution infrastructure is implemented and tested.
- Do not describe institutional Academy features as production multi-tenant unless server-side tenant isolation, roles, and authorization are implemented and audited.
- Clearly distinguish demo data from persisted user data.
- Treat any unverified test claims in PR descriptions as claims, not release evidence. Re-run checks on the final release commit.


## Audit update (2026-11-26, 19:34 CET)

- Current refs verified: `main` = `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`; `release/beta-0.1.0` = `c31244aaf6abdf8743bab4f629d382bbd7b4ba7d`. Beta is based on the current main commit and remains 0 commits behind; the ahead count changes as audit documentation is updated. Main was not modified.
- No Actions runs are associated with the Beta branch head; the commit status is pending with zero status entries. Do not treat the green main `CI monitor` run (#45872078451) as a full Beta test.
- PR #229 is draft, head `066804beb7967d6d5014525a1c1f607a07c1f146`; it was 25 commits ahead of the previous Beta base and now requires refresh after the audit documentation commit(s). CI #636 failed only the E2E job; backend, course validation, WebKit smoke, frontend unit tests, npm audit and pip-audit passed. The failing E2E is the same PCAP sidebar viewport assertion at `e2e/learn.spec.js:558`; Deployment Check #323 passed. No review is recorded.
- PR #223 is draft. CI #622 has the same E2E viewport assertion failure; backend, course checks, WebKit and Deployment Check #309 passed. No review is recorded.
- PR #227 is draft. CI #623 fails the unit test `tests/unit/ai-academy-routing.test.mjs`, whose expectation for the `aiacademy` loader is not present in this branch. Other jobs skipped after the unit-test failure; backend, courses and WebKit were successful; Deployment Check #310 passed. No review is recorded.
- PR #224 is closed and merged into Beta at `1c104b3816f82a55bc883b18e8896a5b011c6597`; no post-merge CI run was found for the current Beta head.
- The five obsolete PRs #207, #209, #101, #193 and #203 are confirmed closed without merge.
- `main` and `release/beta-0.1.0` report `protected: false`. Required branch protection is not configured/verified; treat this as a release risk.
- Branch cleanup review: `beta/programming-path-rebased` has 0 unique commits ahead of Beta and is fully behind, so it is a deletion candidate. Other listed beta port branches diverge and have unique commits; preserve them until their content is inspected. Branch deletion is not available through the current GitHub connector.
- No PR merges, branch deletions, force pushes, release tags, or production deployments were performed in this audit.

- PR #229 was converted back to draft during this audit to prevent merge while CI is failing; its description now records the failure and refresh requirement.

- Latest branch comparisons confirm the Academy and Learning Paths branches diverge from the current Beta; Pentest Lab is based on current main. Exact behind counts are not retained here because audit documentation commits advance Beta.


## Audit update (2026-11-26, 20:28 CET)

- Fresh refs: `main` = `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`; Beta before this update = `7be9e8234b35b6de11b0c420bd2c0a374344950f`. Compare shows Beta 52 commits ahead, 0 behind. No changes were made to `main`.
- `.github/workflows/ci.yml` on Beta was updated at commit `a993adeca5e53beabc81bdd909e89d7a7879f324` to run CI on pushes to both `main` and `release/beta-0.1.0`. A run on the resulting Beta head must be checked; this trigger change does not itself prove CI passed.
- PR #224 remains merged into Beta (merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`). Its checks passed on the PR head; no full post-merge run on Beta was verified.
- PR #223 is draft, no reviews. Compare current head `230dfa2015eed29425f6e282004e04aae85d60a0` with Beta: 12 commits ahead, 36 behind (diverged). CI #622 failed at `e2e/learn.spec.js:558` because the PCAP sidebar heading is resolved but has viewport ratio 0. Deployment Check passed. Do not integrate until refreshed and tested.
- PR #229 is draft, no reviews. Head `066804beb7967d6d5014525a1c1f607a07c1f146`; compare: 25 commits ahead, 4 behind. CI #636 failed the same PCAP sidebar viewport assertion. Backend, course validation, WebKit, frontend unit tests, npm audit and pip-audit passed; Deployment Check #323 passed. Refresh/rebase and rerun CI before ready.
- PR #227 is draft, no reviews, targets `main`; CI #623 failed the routing test because it expects an `aiacademy` loader expression absent from the branch's `app.js`. Backend, courses and WebKit passed; Deployment Check passed. Scope remains undecided and this PR is not integrated into Beta.
- The obsolete PRs #207, #209, #101, #193 and #203 remain closed without merge. No reopen action was taken.
- GitHub reports `protected:false` for both `main` and Beta; the repository has no rulesets returned. Protect main and the release branch before release (PR-only changes, required checks, prevent force-push/deletion, review).
- `beta/programming-path-rebased` is 23 commits behind Beta and 0 ahead; it is a redundant-branch deletion candidate, but branch deletion is not available through the current connector. Other beta port branches diverge and have unique commits; retain them pending file-level review.
- The current CI monitor on main passed, but it is not evidence of a full suite on Beta. No tag, release, deployment, merge, or branch deletion was performed.


## Audit update (2026-11-26, 20:38 CET)

- **Progress-sync mismatch found and ported:** Beta backend rejects PUTs without a known version (428), but its `frontend/js/doc-sync.js` only handled 409 and could attempt an unversioned PUT before reading the account. Ported the PLD-003 client fix from `fix/state-document-versioning`: reread+merge before first PUT when version is unknown, treat 428 as a conflict, and retry with the adopted version. Expanded `tests/unit/doc-sync.test.mjs` to cover this and prove that remote answers are preserved. This is a targeted fix to avoid progress overwrites; validation is pending the new Beta CI run.
- Security review of Academy draft found stored demo count fields interpolated without escaping in several views. Fixed them on the Academy branch and added a hostile-localStorage E2E test. Latest PR head is `346b19d704d22caf1f193e320fa20b206c3ed2b3`; CI #640 is in progress. This code is not in Beta.
- CI run #638 is still running on the previous Beta audit commit. The new sync fix + checklist commit will trigger another full CI run on the updated release head.
- Current scope remains: #223 and #229 draft/unreviewed; #227 draft/scope decision pending; #224 merged. No release, deployment or merge was made.
