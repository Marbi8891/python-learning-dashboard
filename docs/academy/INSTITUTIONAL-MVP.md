# PLD ACADEMY — Institutional MVP

## Purpose
PLD ACADEMY is the institutional layer for schools, vocational centres, bootcamps and training providers. It is separate from the individual PLD Learning experience while sharing the existing learning engine and runtime.

## MVP included in this branch
- New `#/academy` route and sidebar entry.
- Institutional workspace UI with overview, groups, activities, analytics and centre settings.
- Demo role switch for administrator, teacher and student views.
- Create groups and assignments from forms.
- Persist demo data in browser localStorage.
- Responsive layout and E2E coverage for the demo flows.

## Important limitation
This is a frontend prototype with local demo storage. It is **not yet suitable for real schools or student records**. There is no server-side tenant isolation, institutional authentication, permission enforcement, real enrollment, grading service, audit trail, privacy workflow, or backend persistence. Demo names and numbers are synthetic.

## Product architecture target
- Organization / tenant
- Academic year
- Departments and programs
- Subjects and class groups
- Teacher assignments
- Enrollments
- Curriculum and curriculum versions
- Activities, assignments and submissions
- Assessments, rubric scores and grades
- Student progress and mastery
- Portfolio
- Audit and data-retention controls

The tenant boundary must be enforced on the backend for every query and write. Frontend role simulation must never be treated as authorization.

## Next implementation milestones
1. Tenant and organization models, migrations, authorization policies and isolation tests.
2. Institution provisioning and admin/teacher/student accounts with roles.
3. Groups, enrollments and teacher assignments backed by API/database.
4. Curriculum mapping and versioned content customization, reusing PLD content IDs.
5. Assignments, submission tracking and grading.
6. Integrate existing PLD progress, quiz, exercise runtime and mastery without duplicating them.
7. Audit logs, export/deletion/retention and privacy review.
8. Institutional analytics and teacher AI assistant with teacher approval workflows.
9. SSO and LMS integration (e.g. CSV import/export first; evaluate standards-based integrations later).

## Data/content safety
- Do not edit or overwrite global PLD curriculum to customize a centre's course.
- Create immutable or versioned institution-specific copies/overlays.
- Use stable content IDs so course updates do not invalidate student progress.
- Do not send identifiable student data to external AI services by default.
- Educational analytics are advisory; avoid automated high-stakes decisions.

## Demo comercial guiada
- Etiqueta visible de entorno de demostración.
- Recorrido breve para dirección: resumen, grupos, actividades, seguimiento y simulación de roles.
- El recorrido aclara que los datos son sintéticos y que el cambio de rol no es autenticación ni autorización.
- Los datos de demo se pueden restaurar desde la configuración del centro.

## Public commercial demo
- Public product page at `#/academy-info` explaining the institutional value and core capabilities.
- CTA opens the fictional centre workspace at `#/academy`.
- The public page is responsive and clearly labels the experience as a demo.
- E2E test covers the landing page and the CTA transition.
