---
name: asset-need-engine
description: Transform a creative direction and section plan into validated per-section asset briefs. Decides which sections need imagery, what type, style, count, and what to avoid. Plans only — does not fetch.
---

# Asset Need Engine

## Purpose
The planning layer for asset work. Given an approved creative direction
and a section plan, produce one validated `AssetBrief` per section and
write them to `assets/<project_id>/briefs/`.

## When to invoke
- Stage 05 entry, when `direction.md` and `section_plan.json` are both
  ready and `creative_direction_approved = true`.
- Re-invoke whenever a section's copy or role changes materially.

## Inputs
- `workflow/projects/<project_id>/direction.md`
- `workflow/projects/<project_id>/section_plan.json`
- `workflow/projects/<project_id>/copy_deck.md`
- `workflow/asset-schema.json` (validation target)

## Logic (per section)

### 1. Role classification
Classify how the section uses visuals:

| Role | Typical sections | Default variants |
|---|---|---|
| `primary_anchor` | hero, featured card | 5 |
| `supporting` | feature cards, testimonials with portraits | 3 |
| `background` | section-level texture, watermark | 2 |
| `decorative` | icons, dividers, small accents | 1 |
| `need_asset: false` | pure-text blocks (CTA, pricing, transitions) | — |

A strong default: **if a section's copy carries the message alone, it
often doesn't need imagery**. Don't default every section to
`need_asset: true`.

### 2. Asset type routing

| Section pattern | Preferred `asset_type` |
|---|---|
| Hero, full-bleed imagery | `photo` or `abstract_texture` |
| Feature card with portrait | `photo` |
| Illustrative feature | `illustration` |
| Process / steps | `diagram` or `vector` |
| Icon grid / list of capabilities | `icon` |
| Background accent | `abstract_texture` or `vector` |

### 3. Style and mood
Copy verbatim from `direction.md`. Keep `style` prose short
(one sentence), `mood` as 2-4 adjectives. Translate aesthetic cues into
retrieval-friendly terms (e.g. "industrial yet calm" → "industrial
minimal, grounded, muted palette").

### 4. Orientation and aspect ratio
- If the section's Figma frame exists, derive aspect from slot dimensions.
- Otherwise default by role:
  - `primary_anchor` (hero) → `landscape`, 16:9 or 16:10
  - `supporting` (card) → `landscape`, 4:3 or 3:2 (or square for grid)
  - `background` → `any`
  - `decorative` → `square` or `any`

### 5. Variants count
Use the table above. Primary anchors deserve 5 options because their
rejection rate is higher — users are pickier about the hero image.

### 6. Avoid list
Always include the **global defaults**:
- generic smiling teams
- corporate handshake
- obvious SaaS office stock
- fake laptop-on-desk
- over-saturated "lifestyle" cliches

Then add **direction-specific avoids** from the direction doc's
do/don't list.

Keep avoid lists short (3-6 items). Avoid lists that are too long
hamstring retrieval.

### 7. Source selection

| `asset_type` | Default sources (priority) |
|---|---|
| `photo` | unsplash, pexels, firecrawl, adobe_stock |
| `vector` | svgrepo, iconify |
| `illustration` | adobe_stock, open_web |
| `icon` | iconify, svgrepo |
| `abstract_texture` | unsplash, pexels |
| `diagram` | open_web (firecrawl), adobe_stock |

Override defaults if the brief requires licensing (e.g. commercial-only
→ prefer adobe_stock).

## Output (per section)
A JSON file validated against `workflow/asset-schema.json`, written to
`assets/<project_id>/briefs/<section_id>.json`.

Example:
```json
{
  "section": "hero",
  "need_asset": true,
  "asset_type": "photo",
  "role": "primary_anchor",
  "style": "editorial industrial minimal, muted palette, grounded composition",
  "mood": ["grounded", "intelligent", "calm"],
  "orientation": "landscape",
  "aspect_ratio": "16:9",
  "variants": 5,
  "avoid": [
    "generic smiling teams",
    "corporate handshake",
    "drone-selfie aesthetic",
    "people"
  ],
  "sources": ["unsplash", "pexels", "firecrawl"],
  "license_requirements": "any",
  "approval": {
    "status": "draft",
    "approved_at": null,
    "approved_by": null,
    "notes": null
  }
}
```

Also produce `assets/<project_id>/briefs/index.json`:
```json
{
  "project_id": "symnera-website",
  "generated_at": "2026-04-23T12:00:00Z",
  "total_sections": 10,
  "with_assets": 6,
  "text_only": 4,
  "briefs": [
    { "section": "hero", "need_asset": true, "approval": "draft" },
    { "section": "problem", "need_asset": false, "approval": "draft" },
    ...
  ]
}
```

## Mode: auto-first
The engine **drafts every brief automatically**. The user then reviews,
edits, and approves. This is faster for typical projects. Manual-first
mode (user dictates each brief) is also possible but not default.

## Anti-patterns to avoid
- Defaulting every section to `need_asset: true`. Pure-text sections are
  common and valuable.
- Copying direction prose verbatim into `style` without translating to
  retrieval cues (e.g. "bold, strategic" is too abstract; "editorial,
  high-contrast, architectural" is retrievable).
- Overloading `avoid` beyond 6 items — kills search recall.
- Requesting 20 variants "just in case". Over-fetching wastes API
  budget and the user's review time.
- Inconsistent style across briefs. Run a cross-brief coherence check
  at the end (see `critique/system-check.md`).

## Validation
Every brief must pass JSON Schema validation before it can be approved.
Use `python -m jsonschema -i <brief.json> workflow/asset-schema.json` or
the equivalent via `scripts/validate_briefs.py`.

## References
- Brief template: `brief-template.md`
- Section role patterns: `section-taxonomy.md`
