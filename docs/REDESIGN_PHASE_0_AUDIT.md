# PLD Frontend Redesign — Phase 0 Audit

**Branch:** `frontend-redesign/phase-0-audit`  
**Baseline:** `main` at branch creation  
**Status:** Audit/inventory only. No production code or UI has been modified.

## Scope and safety

This work is limited to the presentation layer. The redesign must preserve existing behavior, routes, content, API contracts, persistence, learning progression, Python execution and infrastructure.

Out of scope:
- `backend/`, API contracts, auth and database
- `frontend/data/` curriculum and lesson content
- Python execution, Pyodide, Web Worker and runner logic
- XP, achievements, streaks, learning state, sync and stores
- Docker, CI/CD, hosting and dependencies

JavaScript may be touched only when required for presentation/accessibility, after verifying the target code does not own business or learning logic. Prefer CSS-only changes.

## Repository baseline inventory

### Application entry and shell
- `frontend/index.html`: CSP, metadata, stylesheet order, theme bootstrap, application shell, mobile top bar, sidebar, navigation, course path/progress areas and landing mount.
- `frontend/js/app.js`: application routing/orchestration. Treat as protected unless a narrowly scoped presentation-only change is justified.
- `frontend/js/theme-init.js`: theme and text-size initialization; protected behavior.

### Stylesheets
The application loads the design tokens first and the redesign layer last. The current order in `index.html` is:
`tokens.css`, vendor Highlight.js, `base.css`, `sidebar.css`, `content.css`, `console.css`, `widgets.css`, `game.css`, `ux.css`, `academy.css`, `pcap.css`, `certificate.css`, `daw.css`, `excel.css`, `cybersecurity.css`, `career.css`, `pro.css`, `plans.css`, `learn.css`, `dashboard.css`, `landing.css`, and `redesign.css`.

The existing documentation identifies duplicated definitions/overrides (notably shared buttons and course heroes) and a number of legacy breakpoints. These are redesign candidates, not permission for a wholesale CSS rewrite.

### Frontend areas / screen inventory
This inventory is based on the navigation shell, stylesheet names and E2E spec filenames. Exact route-to-screen mapping must be confirmed in the browser during visual baseline capture.

- Public landing and onboarding
- Navigation shell, sidebar, mobile drawer and route states
- Student dashboard
- Learning planner / daily learning
- Theory and lesson content
- Practice/exercise flow and feedback
- Python console/editor, execution state and output
- Progress, mastery, XP, achievements and game elements
- PCAP course and exam
- DAW course and exam preparation
- Excel Academy/course
- Cybersecurity course
- Career roadmap / career dashboard
- Plans, account, profile and authentication
- AI tutor/assistant panel
- Sync and notification states
- Legal pages and not-found state

## Existing design direction

Source documents:
- `docs/DISENO.md`
- `docs/REDISENO-FRONTEND.md`

Existing direction includes graphite/warm-paper themes, amber primary actions, cyan developer accents, semantic green/red states, Inter/Fraunces/JetBrains Mono typography, subtle borders, readable study content, responsive sidebar and reduced-motion support.

**Important:** these documents contain some differing values and overlapping descriptions. Phase 1 must reconcile them, with the selected `DESIGN.md` treated as the design source of truth. Do not change tokens during Phase 0.

## CSS audit observations

1. Many area-specific stylesheets coexist with a global `redesign.css` override layer.
2. Shared component definitions (for example `.btn` and `.course-hero`) are known to be duplicated across stylesheets.
3. Breakpoints are not fully consolidated; existing docs mention 600, 900 and 1280 px as preferred, with legacy values also present.
4. CSS ownership should be documented before moving rules. Avoid deleting overrides based solely on filename or apparent duplication.
5. Keep code/editor surfaces dark in both themes unless the design specification explicitly changes this.

## Testing inventory

- Unit: `npm run test:unit` (Node test runner, `tests/unit/*.test.mjs`)
- E2E: `npm run test:e2e` (Playwright, `e2e/*.spec.js`)
- Accessibility E2E spec: `e2e/a11y.spec.js` using axe-core/Playwright
- Playwright config starts frontend and real backend services. E2E therefore requires the backend development dependencies and runtime.

Relevant E2E areas include landing, dashboard, navigation, learning, console, PCAP, DAW, Excel, cybersecurity, academy, career, account, AI tutor, study, inclusion, sync, widgets and security.

### Phase 0 validation status

| Check | Status | Notes |
|---|---|---|
| Repository tree / file inventory | Completed | Read from GitHub main |
| Design docs reviewed | Completed | `docs/DISENO.md`, `docs/REDISENO-FRONTEND.md` |
| Entry HTML / stylesheet order | Completed | `frontend/index.html` |
| Test scripts/config inventory | Completed | `package.json`, `playwright.config.js` |
| Local test run | Not run | Repository is not checked out in a local runtime through this GitHub connector |
| Browser screenshots | Not captured | Requires a browser/runtime checkout |
| Manual keyboard/screen-reader review | Not run | Requires browser access |
| Visual baseline (two themes, viewports) | Pending | First implementation task once local checkout/browser is available |

## Visual baseline capture matrix

Capture current-state screenshots before implementation, with no UI changes:

| Screen | Light | Dark | 375px | 768px | 1280px | 1440px |
|---|---:|---:|---:|---:|---:|---:|
| Landing | Pending | Pending | Pending | Pending | Pending | Pending |
| Dashboard | Pending | Pending | Pending | Pending | Pending | Pending |
| Learning | Pending | Pending | Pending | Pending | Pending | Pending |
| Theory/lesson | Pending | Pending | Pending | Pending | Pending | Pending |
| Practice | Pending | Pending | Pending | Pending | Pending | Pending |
| Console | Pending | Pending | Pending | Pending | Pending | Pending |
| PCAP | Pending | Pending | Pending | Pending | Pending | Pending |
| DAW | Pending | Pending | Pending | Pending | Pending | Pending |
| Excel | Pending | Pending | Pending | Pending | Pending | Pending |
| Cybersecurity | Pending | Pending | Pending | Pending | Pending | Pending |
| Career | Pending | Pending | Pending | Pending | Pending | Pending |
| Account/profile | Pending | Pending | Pending | Pending | Pending | Pending |

This is a matrix to be completed, not a claim that screenshots or visual checks have been performed.

## Phase 0 deliverables

- Separate branch created from `main`.
- Audit and inventory document committed.
- No frontend code changed.
- Baseline screenshots and local test results remain pending because a local browser/runtime checkout is not available in this audit session.

## Next phase recommendation

Phase 1 should implement/reconcile the design tokens and shared primitives on this branch only. Before changing CSS, obtain a local checkout and capture the pending visual baseline. Keep each phase reviewable and run tests after each change.
