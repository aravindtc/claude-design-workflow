---
name: Stage 07 — Design System
description: Build component library and tokens from direction doc.
stage_id: 07-design-system
engine: ui-pro-max-adapter
gate: null
---

# Stage 07 — Design System

## Purpose
Translate the direction doc into a concrete component library and design
tokens. This is the scaffolding everything else plugs into.

## Preconditions
- Stage 03 completed with `creative_direction_approved = true`.

## Required inputs
- `direction.md` (palette, type, tokens-in-prose)
- Brand assets (logos, icons, custom imagery)

## Process
1. Create variable collections (primitives + semantic with modes).
2. Create text and effect styles.
3. Build foundation pages (color, typography, spacing, radius, elevation).
4. Build brand asset pages (logo, pictogramme, graphic system).
5. Build core components (buttons, inputs, card, navbar, footer, etc).
6. Build section templates.

## Output
- Figma library file with populated components + variables + styles.
- Optional: token export for downstream code build.

## Notes
For existing Figma-first projects (like Symnera), this stage may already
be largely complete when stages 05-06 enter. That is fine — the
workflow supports partial/retrofitted state.
