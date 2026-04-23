---
name: Stage 04 — Content and Story
description: Define the section plan and authoritative copy for the project.
stage_id: 04-content-story
engine: content-story-engine
gate: null
---

# Stage 04 — Content and Story

## Purpose
Establish WHAT the design will say. Produces the ordered section plan
and the copy deck. Downstream stages treat this as authoritative content.

## Preconditions
- Stage 03 completed with `creative_direction_approved = true`.

## Required inputs
- Direction doc (tone anchor).
- User-provided content or business goals.

## Process
1. Draft section plan: ordered list of sections with role + intent
   (e.g., hero, problem, method, CTA, testimonial, footer).
2. Draft copy per section: eyebrow, headline, subhead, body, CTA text.
3. Review with user; iterate until copy reads as a single narrative.
4. Write:
   - `workflow/projects/<project_id>/section_plan.json`
   - `workflow/projects/<project_id>/copy_deck.md`
5. Mark stage completed.

## Section plan schema (one entry per section)
```json
{
  "id": "hero",
  "order": 1,
  "role": "opening_statement",
  "intent": "Establish brand, state clarity/design/deliver promise",
  "copy_ref": "copy_deck.md#hero"
}
```

## Output
- `section_plan.json`
- `copy_deck.md`

## Notes
- Do not yet decide which sections get imagery — that is stage 05.
- Do not yet build components — that is stage 07.
