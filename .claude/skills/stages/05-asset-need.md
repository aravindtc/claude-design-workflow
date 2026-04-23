---
name: Stage 05 — Asset Need Detection
description: Decide which sections need imagery and write an approved brief per asset.
stage_id: 05-asset-need
engine: asset-need-engine
gate: asset_briefs_approved
---

# Stage 05 — Asset Need Detection

## Purpose
Decide which sections need visual assets, what type each asset should be,
and the brief per asset. **No retrieval happens here** — only planning.

## Preconditions
- Stage 03 completed, gate `creative_direction_approved = true`.
- Stage 04 completed (`section_plan` and `copy_deck` exist).

## Required inputs
- `direction.md` (palette, mood, tone, do/don't)
- `section_plan.json`
- `copy_deck.md`

## Process
Delegates to `engines/asset-need-engine`. For each section in
`section_plan`:

1. **Classify:** does this section need a visual asset? Some sections are
   better as pure-text (CTAs, pricing tables, transitional blocks).
2. **If yes**, decide:
   - `asset_type` — photo / vector / illustration / abstract_texture /
     diagram / icon
   - `role` — primary_anchor / supporting / background / decorative
   - `style` + `mood` — inherited from direction doc
   - `orientation` / `aspect_ratio`
   - `variants` — how many final candidates to keep
   - `avoid` — specific cliches and anti-patterns to exclude
   - `sources` — priority-ordered list of sources
3. Write `assets/<project>/briefs/<section>.json`, validated against
   `workflow/asset-schema.json`.
4. Write `assets/<project>/briefs/index.json` summarizing all briefs.

**Brief-writing mode: auto-first.** The engine drafts every brief.
User reviews, edits, and approves.

## Gate — `asset_briefs_approved`
Every brief where `need_asset = true` must have
`approval.status = approved` before stage 06 can start. User actions:
- Approve all at once
- Approve per-section
- Edit a brief (returns it to status `draft`) and re-approve

## Failure modes
- Brief missing required fields → validation error, surface to user.
- Section has no resolved copy → mark brief as blocked, surface.
- Two briefs mutually inconsistent in style → flag via
  `critique/system-check.md`.

## Output
- `assets/<project>/briefs/<section>.json` × N
- `assets/<project>/briefs/index.json`
- `state.gates.asset_briefs_approved = true` once approval is complete

## Notes
A brief that says `need_asset: false` is a valid brief. Text-only sections
are perfectly fine and common.
