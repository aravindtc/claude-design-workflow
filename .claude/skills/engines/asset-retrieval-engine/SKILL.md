---
name: asset-retrieval-engine
description: Fetch, dedupe, score, and stage candidates per approved asset brief. Wraps pluggable source adapters (Unsplash, Pexels, Firecrawl, SVGRepo, etc). No Figma writes.
---

# Asset Retrieval Engine

## Purpose
The execution layer for stage 06. Takes approved briefs, generates
queries per source, fetches candidates, dedupes, scores, and stages the
results for user approval.

## When to invoke
- Stage 06 entry, when `asset_briefs_approved = true`.
- On retry when earlier fetches returned nothing usable.

## Architecture

```
asset-retrieval-engine
├── SKILL.md                 ← this file
├── retrieval-prompt.md      ← per-brief query generation logic
├── source-priorities.md     ← default source order per asset_type
└── adapters/                ← per-source behavior docs
    ├── unsplash.md
    ├── pexels.md
    ├── firecrawl.md
    └── svgrepo.md
```

Actual network calls live in `scripts/adapters/*.py`. This skill is the
reasoning layer; the Python adapters are the execution layer.

## Per-brief flow

1. **Load brief** from `assets/<project>/briefs/<section>.json`.
2. **Validate** brief against schema; skip if `need_asset: false` or
   approval not granted.
3. **Generate queries** per source (see `retrieval-prompt.md`).
   Typically 3–5 queries per source, variety in phrasing.
4. **Fan out** to each source in `brief.sources` order. Each adapter:
   - Rate-limits its own calls.
   - Returns up to `variants * 2` candidates per source.
   - Normalizes the result into the candidate schema (below).
5. **Merge and dedupe**:
   - Dedup by perceptual hash + (source, source_id) tuple.
   - Dedup between sources (a photo on multiple stock sites = keep one).
6. **Score for fit** — each candidate gets a `fit_score` 0..1 based on:
   - Text match to brief.style and brief.mood
   - Presence of any brief.avoid terms → penalty
   - Composition suitability for brief.role (aspect check)
   - Source reliability (small boost for sources like Unsplash for
     editorial briefs)
   - LLM judgment when heuristics are tied
7. **Rank** by fit_score, keep top `variants * 2`.
8. **Download** files to `assets/<project>/candidates/<section>/` with
   stable names: `NN-<source>-<source_id>.<ext>` where NN is rank 01..
9. **Write metadata** to `assets/<project>/metadata/<section>.json`:
   one entry per candidate, the full schema below.
10. **Build Figma review frame** on an `Assets / Review` page — one
    frame per section showing all candidates laid out + labels (source,
    fit_score, attribution).

## Candidate metadata schema

```json
{
  "section": "hero",
  "brief": "assets/symnera-website/briefs/hero.json",
  "fetched_at": "2026-04-23T12:00:00Z",
  "queries": [
    { "source": "unsplash", "q": "industrial factory aerial minimal" },
    ...
  ],
  "candidates": [
    {
      "rank": 1,
      "file": "01-unsplash-abc123.jpg",
      "source": "unsplash",
      "source_id": "abc123",
      "url": "https://unsplash.com/photos/abc123",
      "download_url": "https://images.unsplash.com/...",
      "attribution": "Photo by J Doe on Unsplash",
      "license": "unsplash-license",
      "license_url": "https://unsplash.com/license",
      "dimensions": [3840, 2160],
      "aspect_ratio": "16:9",
      "tags": ["factory", "aerial", "industrial"],
      "fit_score": 0.87,
      "reason": "Aerial composition matches brief; muted palette; no people.",
      "perceptual_hash": "ffa8..."
    },
    ...
  ],
  "review_frame": {
    "figma_page": "Assets / Review",
    "node_id": "123:456"
  },
  "approval": {
    "status": "candidates_ready | in_review | approved | blocked",
    "approved": [],
    "rejected": [],
    "decided_at": null,
    "by": null
  }
}
```

## Gate handoff

After files land in `candidates/` and metadata is written, the engine
pauses. The gate `assets_approved` stays false until the approval step
runs (driven by the user).

Approval supports both input modes (the user asked for both):

- **A — In-chat:** user types e.g. "for hero pick 2 and 7, for problem
  pick 1". A small script (`scripts/approve_assets.py`) parses the
  instruction, moves files from `candidates/` to `approved/`, updates
  metadata.
- **B — Figma review frame:** user selects candidates on the review
  page; a script reads the current selection and records decisions.

Either way the final state is identical: approved files in
`assets/<project>/approved/<section>/` with clean names, metadata
updated, `assets_approved = true`.

## Error handling

| Error | Action |
|---|---|
| API unauthorized | Surface to user; stop retrieval for that source. |
| Rate limited | Back off (exp 1s → 60s, max 3 retries); continue with other sources. |
| Zero results | Rewrite queries once; if still empty, flag and ask user. |
| All candidates fit_score < 0.3 | Surface; suggest tightening brief. |
| License incompatible | Reject candidate with reason; continue. |
| Download failure | Retry 2x, then skip with error in metadata. |
| Perceptual hash library unavailable | Fall back to source_id-only dedup. |

## Caching

- Per-query results cached under
  `assets/<project>/metadata/_cache/<source>/<query_hash>.json`
  for 24h. Reruns within cache TTL skip network.
- Downloaded files also cached; reruns skip redownload if hash matches.

## Prompt logic

See `retrieval-prompt.md` for query generation details and the
avoid-list enforcement rules.

## Adapters

See `adapters/*.md` for per-source behavior notes. Each corresponds to
a Python module under `scripts/adapters/`.

## Idempotency

Running the engine twice on the same brief should produce the same
metadata file (dedup + cache ensure this). Re-ranking may shift as
candidates expire or the prompt evolves.

## What this engine does NOT do
- Does not import to Figma. That's stage 08 / `import_assets_to_figma.py`.
- Does not mutate `project-state.json` gates directly. The approval
  script (`approve_assets.py`) writes gates after the user decides.
- Does not create briefs. That's `asset-need-engine`.
