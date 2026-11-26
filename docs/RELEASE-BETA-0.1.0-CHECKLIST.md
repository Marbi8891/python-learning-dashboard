# PLD Beta 0.1.0 — Release checklist

**Release target:** `release/beta-0.1.0`  
**Repository:** https://github.com/Marbi8891/python-learning-dashboard  
**Public demo:** https://marbi8891.github.io/python-learning-dashboard/

## Release gate

Do not publish or merge the release until every required item below is verified.

### Scope and integration
- [ ] Confirm the release branch is based on the intended, current `main` commit.
- [ ] Review PR #223 (PLD ACADEMY institutional demo) against the release branch.
- [ ] Review PR #224 (Programming Path) against the release branch.
- [ ] Confirm these features reuse existing progress and storage systems and do not duplicate or overwrite content.
- [ ] Decide whether PR #227 (Pentest Lab dashboard) is in Beta scope. It is a UI prototype; it does not perform real scans or deploy Docker labs.
- [ ] Record included and excluded features in the release notes.

### Quality and security
- [ ] CI is green on the exact release commit.
- [ ] Backend tests and coverage pass.
- [ ] Frontend unit tests pass.
- [ ] Playwright E2E tests pass.
- [ ] Curriculum/content validation scripts pass.
- [ ] Dependency/security checks have no unreviewed blocking findings.
- [ ] Check secrets, personal data, debug flags, and unsafe demo defaults.
- [ ] Verify authentication, persistence, and demo-mode isolation.
- [ ] Review accessibility (keyboard, focus, responsive layout, WCAG/axe checks).

### Product presentation
- [ ] README has current feature summary, setup instructions, screenshots, demo link, and clear project status.
- [ ] Demo route works without requiring a real account and does not touch real user data.
- [ ] Academy demo explains institutional use and limitations.
- [ ] Programming Path is visible and its progress integration is verified.
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
- PR #223 and #224 target this release branch and are the primary Beta integration candidates.
- PR #227 remains separate on `main`; scope decision and review are pending.
- The repository still has multiple open PRs. They have not been declared integrated merely because they are listed here.

## Known limitations to disclose

- Do not describe Pentest Lab as an actual scanning or Docker lab platform unless real execution infrastructure is implemented and tested.
- Do not describe institutional Academy features as production multi-tenant unless server-side tenant isolation, roles, and authorization are implemented and audited.
- Clearly distinguish demo data from persisted user data.
- Treat any unverified test claims in PR descriptions as claims, not release evidence. Re-run checks on the final release commit.
