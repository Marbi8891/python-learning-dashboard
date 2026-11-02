# Python Learning Dashboard — Business Model

**Status:** Hypotheses to validate, not a sales forecast  
**Date:** 2026-11-02

## 1. Commercial thesis

Start with a free-to-use learning experience for individuals. Test whether engaged learners will pay for advanced paths, structured exam preparation and personalised review. Consider a teacher/academy offer only after individual usage and demand have been validated.

The project is not commercially validated yet. Pricing, conversion, retention and acquisition assumptions below must be tested with users.

## 2. Customer segments

### Initial: individual learners
- Beginners learning Python.
- Spanish vocational students studying programming and related DAW modules.

### Later: certification candidates
People preparing for a technical exam, provided the syllabus, answer keys, exam-format claims and third-party intellectual-property use are reviewed.

### Possible B2B: teachers and small academies
Institutions that need assignments, group progress and reporting. Do not build a full LMS before securing a pilot partner.

## 3. Pricing hypotheses

Indicative prices for research and experiments only. They are not validated market prices and should not be published as final offers until features, legal terms and payment flows are ready.

| Tier | Hypothetical price | Potential value |
|---|---:|---|
| Free | €0/month | Core lessons, selected exercises and personal progress |
| Plus | €7.99/month | Advanced paths, review tools and expanded progress insights |
| Pro | €14.99/month | Advanced exam practice, detailed analysis and personalised study plans |
| Academy | From €99/month | Small-group assignments and teacher progress reports |

Pricing may require VAT, consumer-law, renewal, cancellation, refund and invoicing analysis depending on the transaction and customer. Annual plans should be tested only after monthly retention is understood.

## 4. Revenue scenarios

Illustrative monthly recurring revenue at the proposed individual prices:

| Scenario | Plus accounts | Pro accounts | Gross monthly recurring revenue |
|---|---:|---:|---:|
| Early experiment | 50 | 10 | €549.40 |
| Intermediate | 200 | 50 | €2,344.50 |
| Expansion | 500 | 150 | €6,249.50 |

Formula: (Plus accounts × €7.99) + (Pro accounts × €14.99).

These are arithmetic scenarios, not forecasts or evidence of achievable demand. They exclude VAT where applicable, refunds, payment fees, hosting, email, AI usage, support, marketing, taxes and other operating costs. They also exclude academy revenue.

## 5. Costs and unit economics

Track fixed and variable costs separately.

Potential costs:
- Frontend/API hosting and database.
- Domain, email delivery and monitoring.
- Payment processing and invoicing.
- Customer support and content review.
- Acquisition and marketing.
- AI inference, if added.
- Legal/accounting advice and compliance work.
- Developer time and ongoing maintenance.

Browser-based Pyodide execution keeps ordinary Python exercises off the server, which can limit variable infrastructure costs. Do not assume that all hosting free tiers will be appropriate for a paid service.

Before scaling, estimate:
- gross revenue per paying account,
- variable cost per active/paying account,
- gross margin after variable costs,
- conversion from active free users to paid,
- monthly churn and retention,
- acquisition cost by channel,
- payback period,
- support time per customer.

Do not rely on lifetime-value calculations until there is enough cohort history to estimate retention.

## 6. Go-to-market experiments

### Experiment A — Learner pilot
Recruit 10–20 voluntary beginners and DAW students. Observe first use and repeated study over several weeks. Collect feedback on content, exercise explanations and accessibility.

### Experiment B — Willingness to pay
Interview engaged learners and present clear, non-binding plan concepts. Test which benefit matters enough to pay for. Avoid building a large paywall before evidence exists.

### Experiment C — Academy discovery
Interview teachers and small training centres. Ask how they currently assign practice and monitor progress, what tools they use, and what budget/approval process exists. Seek a pilot commitment before implementing multi-tenant features.

### Acquisition channels to test
- Public GitHub repository and a clear live demo.
- Useful technical articles and free learning exercises.
- Student communities and teacher relationships.
- Demonstrations and case studies showing learning outcomes.
- Referrals from pilot users.

Do not assume a channel is effective until its conversions and effort are measured.

## 7. Freemium boundaries

Keep the free product genuinely useful. Possible paid differentiation:
- advanced learning paths,
- larger or specialised mock exams,
- detailed performance history,
- personalised study planning,
- downloadable reports or project packs.

Do not charge for access to a learner's existing data, block account deletion/export, or imply that a paid subscription grants an official certification. Paid features must exist before being sold.

## 8. B2B academy model

Potential later offer: a monthly fee based on organisation or active learner count, with:
- teacher-created groups,
- assignments and deadlines,
- progress and assessment reports,
- role-based access and organisation-level data separation.

The €99/month starting point is only a hypothesis. Test pricing, onboarding and support requirements with a pilot before choosing per-seat or per-organisation billing.

## 9. Trust, compliance and content

Before accepting payment:
- Identify the legal seller and provide required business/contact information.
- Publish clear terms, privacy notice and applicable consumer information.
- Explain subscription price, billing interval, renewal, cancellation and refund terms.
- Review GDPR/LOPDGDD, LSSI-CE and other applicable consumer and accessibility rules with qualified advice.
- Review processors, retention, data export/deletion and international transfers.
- Document source, attribution and licence for course materials and questions.
- Do not imply affiliation with Python Institute or other certification bodies without authorisation.
- Provide a support and incident-handling process.

This checklist is a planning aid, not a legal compliance determination.

## 10. Go/no-go criteria

Proceed with a paid experiment only when:
- the core learning path works reliably,
- content and scoring have been reviewed,
- account and progress flows are tested,
- privacy and commercial terms are ready,
- at least some engaged users identify a specific paid benefit,
- expected variable costs can be bounded.

Proceed with academy development only when teacher interviews show a repeated problem and a credible pilot partner is available.

## 11. Monthly review

Review actual:
- active learners and returning learners,
- first-exercise and path completion,
- assessment improvement,
- free-to-paid conversion,
- paid retention and cancellations,
- support load and refunds,
- variable cost and gross margin,
- top user complaints.

Record sample size and period. Change prices and scope based on evidence rather than treating these initial assumptions as facts.
