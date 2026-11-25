# Programming Path: curriculum map and reuse audit

This document is the implementation map for the programming curriculum. It is intentionally a roadmap, not a second lesson store.

## Principles

- Reuse PLD course lessons, concepts, practice blocks, banks, project evidence and Career units.
- New units are navigation records with objectives and references; they are not copied explanations or quizzes.
- A gap is only a candidate for original PLD content after verifying that an equivalent lesson, exercise, project or assessment does not already exist.
- Resource references point to the original source. Do not reproduce copyrighted courses or exercise banks.
- The Python source `scripts/career/programming_path.py` is a draft data source for the Career generator. It is not yet registered in the generator or runtime catalog. It must be validated and generated before activation.

## Curriculum sequence

| Level | Modules | Existing PLD content to reuse | Gaps to develop after audit |
|---|---|---|---|
| Foundations | Computer science; problem solving | Entornos `ent-lenguajes`; Programming `prog-ut1`; concepts algorithms, pseudocode, tracing, conditions, loops | Computational thinking practice, complexity |
| Python | Python 0–intermediate; Python engineering | `prog-ut2`–`prog-ut8`; concepts variables, types, operators, IO, validation, functions, collections, exceptions, modules, files, OOP | Typing, generators, decorators, advanced testing |
| Developer tools | Shell, Git, environments, debugging | Pro Git resource; Entornos course | MIT Missing Semester labs, profiling/workflow practice |
| Algorithms & data structures | Search, sorting, lists, stacks, queues, trees, graphs | Existing concepts/algorithm blocks where equivalent | Advanced data structures and complexity exercises |
| Web | HTML/CSS/JS/DOM/async | Marcas `mar-html`, `mar-json`; JS `js-fundamentos`, `js-funciones`, `js-datos`, `js-dom`, `js-asincronia` | Accessibility, responsive and performance labs where gaps exist |
| Modern frontend | TypeScript, React, architecture, frontend testing | Existing JavaScript course and web resources | TypeScript/React curriculum, only if no current PLD content |
| Databases | Relational design, SQL, transactions, NoSQL | SQL `bd-ud1`–`bd-ampliacion` | PostgreSQL performance, database internals, NoSQL practice |
| Backend | HTTP, REST, FastAPI, auth, persistence, API testing | Existing Python, SQL, JS and Career AI Engineer modules | FastAPI-focused learning units only where not already covered |
| Software engineering | Clean code, SOLID, patterns, testing, documentation | Career Applied AI roadmap M1/M2; existing courses and projects | Focused labs and review rubrics where verified gaps remain |
| Java / enterprise | Java syntax, OOP, collections | Java `java-basico`, `java-control`, `java-poo`, `java-herencia`, `java-colecciones` | Spring Boot and enterprise project if absent |
| Systems | Linux, networks, concurrency | Entornos and existing cybersecurity/networking content | OS fundamentals and concurrency labs where missing |
| DevOps / cloud | Docker, Compose, CI/CD, cloud, Kubernetes | Docker resource; existing PLD deployment and project evidence | Cloud-provider track, Kubernetes labs, operations |
| Security | OWASP, secure coding, DevSecOps | Existing cybersecurity content and NEXARO projects | Secure-development checkpoints, only if no equivalent |
| AI/ML | ML, DL, Transformers, LLMs, RAG, agents | Existing Career roadmap `applied-ai-engineer` M3–M6 and relevant resources | Link existing units; no parallel AI curriculum |
| Expert | System design, reliability, performance, specialization, capstone | Existing projects (PLD, NEXARO, JobRadar) and career evidence | Advanced design review, performance testing, final evidence rubric |

## Sources added to PLD resources

The resources catalog contains official/university references for CS50x, CS50P, CS50 SQL, CS50 Web, MIT Missing Semester, TypeScript Handbook, React Learn, FastAPI, PostgreSQL, pytest, OWASP, PyTorch, Hugging Face, Linux man-pages, Kubernetes, Dev.java, Spring Guides, MDN HTTP, MIT algorithms, CMU database systems, The Odin Project, freeCodeCamp and Full Stack Open.

Resource IDs must be reused. Do not add another entry for the same URL or resource.

## Activation gate

Before activating the roadmap in `frontend/data/career/index.json`:

1. Run `python scripts/career/build_career.py` locally and review the generated catalog.
2. Run `python scripts/career/build_career.py --check`.
3. Validate all references and stable IDs.
4. Review whether any unit overlaps an existing Career unit or DAW lesson; replace the duplicate with a reference.
5. Add the generated JSON and index entry only after all checks pass.
6. Run the full CI, including Career generator validation and UI tests.
7. Keep the PR draft until this is complete. Do not publish to main or Pages automatically.


## New gap-specific references (audit 2026-11-25)

These sources were added because the existing PLD content does not fully cover the corresponding advanced objectives. They are external links only; PLD does not copy lessons or exercises.

| Gap | Resource IDs | Source |
|---|---|---|
| Python typing, async, packaging, advanced testing | `res-python-typing`, `res-python-asyncio`, `res-python-packaging`, `res-python-testing`, `res-hypothesis` | Python docs, Python Packaging Authority, Hypothesis |
| Advanced algorithms and structures | `res-princeton-algorithms` | Princeton University Algorithms |
| Accessibility and web performance | `res-w3c-wai-tutorials`, `res-webdev-performance` | W3C WAI, web.dev |
| API-specific security | `res-owasp-api-top10` | OWASP API Security |
| Deployment configuration and CI/CD | `res-12factor`, `res-github-actions` | Twelve-Factor App, GitHub Actions docs |
| NoSQL | `res-mongodb-docs` | MongoDB official manual |
| ML foundations | `res-google-mlcc` | Google Machine Learning Crash Course |
| Cloud fundamentals and native ecosystem | `res-azure-fundamentals`, `res-cncft-cloud-native` | Microsoft Learn, CNCF |
| System reliability / expert systems | `res-google-sre` | Google SRE resource library |

All curriculum resource references were checked against the source catalog: no missing resource IDs. Resource source and generated catalog synchronization still needs to be run with the project generator and CI.
