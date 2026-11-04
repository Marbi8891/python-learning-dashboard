# Python Learning Dashboard — Product Strategy

**Status:** Working strategy, version 1.0  
**Date:** 2026-11-02  
**Horizon:** November 2026–October 2027  
**Primary objective:** Product + professional portfolio  
**Initial audience:** Broad, with staged prioritisation  
**Scope:** Hybrid learning platform for programming, vocational study and technical certification preparation

## 1. Executive decision

Evolve Python Learning Dashboard (PLD) into a practical technology-learning platform built around structured content, browser-based practice, assessment and learner progress. Keep the existing repository and architecture; do not undertake a framework migration or microservices rewrite without measured need.

The product can serve several audiences over time, but development must be sequenced. The first beachhead is individual learners: programming beginners and Spanish vocational-training students, starting with Python and selected DAW content. Certification preparation follows after content quality and assessment accuracy are validated. Teacher and academy features are a later B2B experiment.

## 2. Vision and mission

**Vision:** Help people learn technical skills by practising, receiving useful feedback and seeing what they can actually do.

**Mission:** Bring lessons, browser-based exercises, assessments and a coherent learning path into one accessible application.

## 3. Target users and sequencing

| Segment | Job to be done | Priority | Evidence needed |
|---|---|---:|---|
| Beginners learning programming | Learn core concepts without installing tools | P1 | First lesson completion, return rate, exercise success |
| Spanish DAW/DAM students | Practise module outcomes and prepare assessments | P1 | Student interviews, curriculum mapping, repeat use |
| Certification candidates | Prepare against a defined syllabus and exam format | P2 | Content review, practice-test feedback, willingness to pay |
| Teachers and small academies | Assign practice and monitor group progress | P3 | Interviews and a paid or committed pilot |

“Everyone” is the long-term addressable audience, not a single MVP specification. The platform should be extensible, while the first release serves P1 users well.

## 4. Positioning

**Working value proposition:** Learn technology by practising. Follow a structured path, run code in the browser and use feedback to decide what to study next.

PLD should compete on the quality of the learning loop rather than on the size of its course catalogue or the presence of a generic AI chatbot.

### Product principles

1. Practice before gamification: XP and streaks support learning but are not learning outcomes.
2. Feedback must explain the mistake and give a useful next action.
3. Make progress understandable: distinguish activity completed from demonstrated mastery.
4. Keep the core experience accessible, responsive and usable without a paid account where feasible.
5. Use source-controlled, versioned learning content with automated validation.
6. Protect learner data and make account, export and deletion behaviour clear.
7. Prefer evidence and small experiments over speculative feature expansion.

## 5. Product pillars

### Learn
Structured courses, short explanations, examples, prerequisites and explicit learning objectives.

### Practice
Exercises with feedback, code execution in a browser for supported languages, and progressive challenges.

### Assess
Quizzes and practice exams with transparent scoring, reviewed answer keys and explanations. Do not imply an official certification or endorsement unless authorised.

### Progress
Learning history, review scheduling, strengths and gaps, and clear next-step recommendations. Avoid claiming a learner has mastered a skill from one correct answer.

### Paths
Curated routes for Python foundations, selected DAW modules and later technical certifications. Every path must state its audience, prerequisites, outcomes, version and review date.

## 6. Differentiation

- Python execution in the browser using Pyodide and Web Workers.
- Exercises that explain common errors and offer related practice.
- Curriculum mapping that links exercises to explicit learning outcomes where verified.
- A progression model based on evidence from multiple attempts and review over time.
- A lightweight web/PWA experience rather than a mandatory local development setup.

The recommendation system should begin with transparent rules. Add an AI tutor only when it solves a validated problem, is grounded in reviewed course material, and can be evaluated for correctness, privacy and cost.

## 7. Scope boundaries

### In scope for the first product cycle
- Stabilise existing learner, account and progress flows.
- Make one Python path coherent from entry to final assessment.
- Improve content metadata, quality checks and curriculum traceability.
- Establish product analytics with data minimisation.
- Test with real learners and learn what they will pay for.

### Out of scope until validated
- Microservices, a full React rewrite, native mobile apps.
- A full school-management system or LMS administration suite.
- Server-side execution of arbitrary learner code without a separate threat model and isolation design.
- AI-generated grading or official certificates without validation.
- Expanding every course/module just to increase catalogue size.

## 8. Success measures

First instrument the baseline; then set targets from observed data. Do not report targets as achieved results.

- Activation: percentage of new learners who complete a first meaningful exercise.
- Learning engagement: percentage who complete the first learning unit.
- Retention: percentage returning after 7 and 28 days.
- Learning effectiveness: change between comparable pre- and post-path assessments.
- Content quality: broken/invalid exercises, disputed answers, review coverage and time to fix reports.
- Product reliability: failed syncs, API error rate, frontend errors and availability.
- Commercial validation: conversion to paid plans, cancellations, revenue per paying account and contribution after variable costs.
- Portfolio quality: reproducible setup, CI, documented decisions, accessible flows and a demonstrable end-to-end learning journey.

## 9. Validation plan

Recruit 10–20 voluntary testers for a multi-week pilot. Include beginners and DAW students. Observe task completion and interview them after use. Do not rely on compliments or page views alone.

Questions to answer:
1. Can a new learner understand where to begin?
2. Can they complete a lesson and an exercise without help?
3. Does feedback help them correct a mistake?
4. Do they return without being prompted?
5. Which outcome would justify paying?
6. What is confusing, unreliable or inaccessible?

## 10. Decision rules

- Do not expand the catalogue while the core path has broken exercises or unclear explanations.
- Do not launch paid learning claims until content, support, terms and payment flows are ready.
- Do not build academy features until interviews identify a repeated need and at least one credible pilot opportunity.
- Do not add an AI feature without a baseline, evaluation set, privacy review and cost limit.
- Review this strategy quarterly using actual usage and learner feedback.

## 11. Current repository baseline

The README currently documents HTML/CSS/JavaScript ES modules, Pyodide in a Web Worker, a FastAPI backend, SQLAlchemy/Alembic, PostgreSQL in production, optional accounts, PWA behaviour, learning content and automated tests. It also documents limitations including browser-calculated XP/progress, in-memory login rate limits, free-tier backend cold starts and incomplete manual screen-reader testing.

Treat these as the repository's documented state, not as independently re-tested production guarantees. Confirm each item against the current default branch and deployed application before release.
