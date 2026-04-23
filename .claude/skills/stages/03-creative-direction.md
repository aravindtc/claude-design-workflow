---
name: Stage 03 — Creative Direction
description: Commit to palette, type, tone, and mood. First hard approval gate.
stage_id: 03-creative-direction
engine: visual-direction-engine
gate: creative_direction_approved
---

# Stage 03 — Creative Direction

## Purpose
Produce a direction document that downstream stages treat as truth:
palette, typography, tone, visual mood, and core anti-patterns. This is
where we stop exploring and start committing.

## Preconditions
- Stage 02 completed.
- At least one inspiration reference decomposed.

## Required inputs
- Inspiration boards from stage 02.
- Any brand assets (logo, existing color tokens) if the project has them.

## Process
1. Synthesize signals from inspiration into a single direction proposal.
2. Write `workflow/projects/<project_id>/direction.md` with:
   - Palette (hex + semantic roles)
   - Typography system
   - Tone of voice
   - Visual mood (3-5 adjectives)
   - Do / Don't list
3. Present to user for approval.
4. On approval: set `gates.creative_direction_approved = true`,
   mark stage completed.

## Gate — `creative_direction_approved`
No UI generation, no content work, no asset work proceeds until this gate
is true. Edits are allowed (revert to status `in_review` and re-approve).

## Output
- `direction.md`
- `state.gates.creative_direction_approved = true`

## Notes
Keep the direction doc short (1-2 pages max). It should be a reference
that stays true throughout the project, not an exhaustive style guide.
