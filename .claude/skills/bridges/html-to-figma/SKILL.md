---
name: html-to-figma
description: Translate HTML/CSS (including Tailwind) into accurate Figma frames using the Plugin API. Preserves layout structure, spacing rhythm, typography, and color tokens.
---

# Skill: HTML → Figma conversion

You convert HTML/Tailwind UI into structured Figma designs.

## Goal

Transform UI code into:
- clean Figma frames
- auto layout structure
- reusable components
- design tokens (if requested)

## Workflow

1. Parse HTML structure
2. Map elements to Figma layers
3. Translate Tailwind classes to design tokens
4. Build auto layout structure
5. Apply spacing and hierarchy
6. Identify component candidates
7. (Optional) Create variables and styles

## Element mapping

- div → frame
- section → frame (grouped)
- h1–h6 → text (heading styles)
- p → text (body styles)
- button → component candidate
- img → image layer

## Hard rules

- always use auto layout (no absolute positioning unless necessary)
- maintain spacing from Tailwind values
- preserve hierarchy from HTML
- do not flatten structure

---

## Reference files

Load these as needed during execution:

- `tailwind-mapping.md` — Tailwind class → Figma value lookup (spacing, colors, typography, shadows, radius)
- `layout-rules.md` — flex/grid → Auto Layout translation, sizing modes, component patterns
- `token-extraction.md` — extract tokens from CSS/Tailwind config and create Figma variables
