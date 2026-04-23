---
name: Stage 02 — Inspiration Analysis
description: Collect and decompose inspiration references into usable signals.
stage_id: 02-inspiration-analysis
engine: inspiration-engine
gate: null
---

# Stage 02 — Inspiration Analysis

## Purpose
Turn raw inspiration (URLs, screenshots, Figma files, mood boards) into a
structured set of signals the creative-direction stage can act on.

## Preconditions
- Stage 01 completed.

## Required inputs
- One or more inspiration sources:
  - Figma file keys
  - Image files (PNG/JPG)
  - URLs to reference sites

## Process
Delegates to the `inspiration-engine` skill at
`.claude/skills/inspiration-engine/SKILL.md`. For each source:
1. Decompose into layout, typography, color, imagery style, tone signals.
2. Note what to pursue and what to avoid.
3. Cross-image consolidation: find recurring patterns across references.

## Output
- Inspiration boards (Figma pages, local markdown, or both)
- `visual_references` index at
  `workflow/projects/<project_id>/inspiration.md` — one section per
  reference with decomposition + pursue/avoid notes.

## Notes
This stage does not commit to direction yet. Direction crystallizes in
stage 03 where the user approves.
