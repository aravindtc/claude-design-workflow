---
name: Stage 10 — Final QA
description: Responsive, a11y, content, system checks. Sign-off before delivery.
stage_id: 10-final-qa
engine: null
gate: project_signed_off
---

# Stage 10 — Final QA

## Purpose
Final pass before delivery. Runs the critique checks and captures
sign-off.

## Preconditions
- Stage 09 completed.

## Process
Run each critique doc:
- `critique/final-visual-check.md`
- `critique/responsive-check.md`
- `critique/content-check.md`
- `critique/system-check.md`

Fix blocking issues; log non-blocking ones as `known_issues` in state.

## Gate — `project_signed_off`
User gives explicit sign-off. Marks project complete.

## Output
- QA report at `workflow/projects/<project_id>/qa-report.md`
- `state.gates.project_signed_off = true`
