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
- [ ] Create final changelog entry.
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
- PR #223 remains open and cannot currently merge. The base branch advanced when #224 merged. The Academy persistence E2E was corrected in head commit `230dfa2015eed29425f6e282004e04aae85d60a0` to follow the public landing CTA to the workspace. No CI run is available for that commit, and the branch still diverges (12 commits ahead / 19 behind the current release branch at last comparison). The GitHub connector has no branch-rebase/update operation; it must be rebased or ported before integration. The separate PCAP viewport assertion failure also remains to be checked.
- PR #227 remains separate against `main`; scope decision is pending. CI failures include missing English translation for the new “Pentest Lab” label and a WebKit account-recovery test failing to find the expected mailto link.
- `release/beta-0.1.0` is currently 35 commits ahead of `main` and 0 behind; `main` was not modified.
- There are still several open PRs targeting `main`; they are not considered integrated into the Beta unless separately ported/reviewed.

## Known limitations to disclose

- Do not describe Pentest Lab as an actual scanning or Docker lab platform unless real execution infrastructure is implemented and tested.
- Do not describe institutional Academy features as production multi-tenant unless server-side tenant isolation, roles, and authorization are implemented and audited.
- Clearly distinguish demo data from persisted user data.
- Treat any unverified test claims in PR descriptions as claims, not release evidence. Re-run checks on the final release commit.
