---
name: Stage 09 — Code Build
description: Export from Figma to code (web, wordpress, or other target).
stage_id: 09-code-build
engine: outputs/web
gate: null
---

# Stage 09 — Code Build

## Purpose
Translate the approved Figma page into working code for the chosen output
target. Deferred; detailed spec to be written when first code target is live.

## Preconditions
- Gate `figma_build_approved = true`.

## Process (placeholder)
- Decide target: `web` (React/Next), `wordpress`, or other.
- Delegate to the matching output engine under `.claude/skills/outputs/`.
- Use design tokens from stage 07 as the source of truth.

## Output
- Codebase in `outputs/<target>/` or a dedicated repo.
