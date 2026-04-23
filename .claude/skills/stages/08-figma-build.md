---
name: Stage 08 — Figma Build
description: Compose final Figma pages from components + approved assets.
stage_id: 08-figma-build
engine: outputs/figma
gate: figma_build_approved
---

# Stage 08 — Figma Build

## Purpose
Assemble the final Figma page by placing component instances + approved
assets according to the section plan.

## Preconditions
- Stage 07 completed (component library exists).
- Gate `assets_approved = true` (approved assets ready to import).
- `section_plan.json` exists.

## Process
1. Create or open the target Figma page.
2. For each section in section_plan (in order):
   - Drop the section component instance.
   - Run `scripts/import_assets_to_figma.py` to place approved assets
     into that section's image slots.
3. Update `state.artifacts.image_slots` with node IDs per section.
4. Validate with `critique/final-visual-check.md`.
5. Present to user for approval.
6. On approval: set `figma_build_approved = true`.

## Gate — `figma_build_approved`
No code build starts until the Figma page is signed off.

## Output
- Final Figma page with real content + real assets.
- Updated state with all image_slots mapped.
