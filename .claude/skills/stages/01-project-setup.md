---
name: Stage 01 — Project Setup
description: Initialize a new project — id, output target, Figma file, basic metadata.
stage_id: 01-project-setup
engine: null
gate: null
---

# Stage 01 — Project Setup

## Purpose
Bootstrap a new project in the workflow. Collects minimal metadata needed
for the downstream stages to run. Writes the initial `project-state.json`.

## Preconditions
None. This is the entry stage.

## Required inputs (from user)
- `project_id` (kebab-case, e.g. `symnera-website`)
- Output target(s): `figma`, `web`, `wordpress` (pick one or more)
- Optional: existing Figma file key if continuing work

## Process
1. Create `workflow/projects/<project_id>/project-state.json` from the
   initial template.
2. Create folder structure:
   - `assets/<project_id>/{briefs,candidates,approved,metadata}/`
3. Record `current_stage = "01-project-setup"`, status `in_progress`.
4. Capture any existing artifacts (Figma file key) in `state.artifacts`.
5. Mark stage `completed`; transition to stage 02.

## Output
- `workflow/projects/<project_id>/project-state.json`
- Empty asset folders under `assets/<project_id>/`

## Notes
This stage is lightweight. It exists so every downstream stage has a
predictable state file to read and write.
