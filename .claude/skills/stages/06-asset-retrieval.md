---
name: Stage 06 — Asset Retrieval
description: Fetch candidates from sources, stage for review, approve. No Figma import yet.
stage_id: 06-asset-retrieval
engine: asset-retrieval-engine
gate: assets_approved
---

# Stage 06 — Asset Retrieval

## Purpose
Fetch asset candidates per approved brief from configured sources. Save
locally with metadata. Present for review. Collect user approval.
**Do not import to Figma at this stage** — stage 08 handles import.

## Preconditions
- Stage 05 completed.
- Gate `asset_briefs_approved = true`.
- API keys available for every source in the briefs (env-checked).

## Required inputs
- Approved briefs under `assets/<project>/briefs/*.json`
- API credentials in env:
  - `UNSPLASH_ACCESS_KEY`
  - `PEXELS_API_KEY`
  - `FIRECRAWL_API_KEY`
  - (optional) `ADOBE_STOCK_*`, `GETTY_*`

## Process
Delegates to `engines/asset-retrieval-engine`. For each brief:

1. Load `retrieval-prompt.md` and generate 3-5 queries per source.
2. Call each source adapter in `scripts/adapters/`:
   - Fetch `variants * 2` candidates per source (over-fetch for dedup).
3. Dedupe across sources (perceptual hash + source ID).
4. Score each candidate for fit against the brief.
5. Keep top `variants * 2`.
6. Download files to `assets/<project>/candidates/<section>/`.
7. Write `assets/<project>/metadata/<section>.json` — one entry per
   candidate with source URL, attribution, license, dimensions, tags,
   fit_score, and a short "reason" string.
8. Build a Figma review frame on an `Assets / Review` page. One frame
   per section, laying out all candidates with their source and score
   labeled.
9. Transition stage to `awaiting_approval`.

## Gate — `assets_approved` (UX: both A and B)
User reviews candidates per section. Two input methods both supported:

- **A — In-chat** (fast): User types e.g. "for hero pick 2 and 7, for
  problem pick 1". Script parses and moves files.
- **B — Figma review frame** (visual): User selects candidates directly
  on the Figma review page. Script reads the selection and records
  decisions.

Selected files move to `assets/<project>/approved/<section>/` and are
renamed for stable Figma import (e.g. `hero-01.jpg`, `hero-02.jpg`).
Metadata is updated with the approval record.

## Failure modes
- No candidates returned from any source → re-query with rewritten prompt;
  if still empty, surface to user (suggest manual upload or brief revision).
- Source API rate-limited → back off, retry with other sources.
- License conflict detected → reject candidate, record reason.
- All candidates below fit-score threshold → ask user to tighten brief.

## Output
- `assets/<project>/candidates/` populated with files + metadata
- `assets/<project>/approved/` populated after approval
- Figma `Assets / Review` page with review frames (left as-is or
  archived depending on user preference)
- `state.gates.assets_approved = true` after approval

## Notes
Retrieval can be expensive (API calls + downloads). The engine caches
per-query results for 24 h under `assets/<project>/metadata/_cache/`
to avoid re-fetching on retries.
