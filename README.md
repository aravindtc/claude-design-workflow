# claude-design-workflow

A design workflow that pairs Claude Code with Figma MCP, Firecrawl, Unsplash, and vision-LLM grading to produce brand-specific design systems — end-to-end from inspiration capture to Figma build.

The core idea: replace "collect screenshots and hope" with a structured pipeline that segments, scores, and extracts reusable design signals, so downstream Figma generation has real references to work from.

---

## What's in here

```
workflow/                         schemas + 10-stage pipeline definition
  stages.yaml                     pipeline manifest (stages 01..10)
  asset-schema.json               AssetBrief: per-section image/vector requests
  inspiration-schema.json         InspirationBrief: brand-level brand/aesthetic/patterns
  pattern-schema.json             Pattern: extracted design-signal output

.claude/skills/
  stages/                         one SKILL.md per pipeline stage (01–10)
  engines/                        reusable skills (asset-need, asset-retrieval)

scripts/                          Python CLIs (stdlib + Pillow + numpy)
  retrieve_assets.py              Unsplash + Firecrawl asset retrieval (photos, vectors)
  retrieve_inspiration.py         Firecrawl-based inspiration capture (capture-only)
  extract_pattern_signals.py      segment → heuristic → vision-LLM → pattern JSON

assets/<project>/                 stock photo / asset candidates + approval log
  briefs/                         AssetBrief JSONs (per section)
  candidates/                     downloaded candidates
  approved/                       user-approved final assets
  metadata/                       approval-log + cache

inspiration/<project>/            raw webpage captures (traceability only)
  briefs/brand.json               InspirationBrief
  raw/                            full-page screenshots + page.md + preview.jpg
  segments/                       cropped regions written by the extractor
  metadata/                       discovery aggregate + extraction summary

pattern-library/                  THE output — structured design patterns
  candidates/                     patterns scoring ≥ 0.70 (JSON + PNG per pattern)
  approved/                       user-curated anchor set
  ratings.json                    user ratings on captures (drives similarity crawls)
```

---

## The two pipelines

### 1. Asset retrieval (photos, vectors, illustrations)

A per-section brief (`assets/<project>/briefs/<section>.json`) defines what's needed (asset_type, role, style, mood, aspect, variants, avoid list). `scripts/retrieve_assets.py` queries Unsplash + Firecrawl, scores candidates against the brief, and saves the top N for user approval.

```bash
python3 scripts/retrieve_assets.py --project symnera-website --section hero
```

### 2. Inspiration → Design patterns (visual signal extraction)

A single brand brief (`inspiration/<project>/briefs/brand.json`) defines aesthetic tags, patterns wanted, avoid list, and source sites. Two scripts run back-to-back:

**Capture** — Firecrawl search + scrape with per-source URL filters that reject gallery / listing / search pages.

```bash
python3 scripts/retrieve_inspiration.py --project symnera-website --per-source-limit 4
```

Targeted "more like X" runs bypass brief-derived queries:

```bash
python3 scripts/retrieve_inspiration.py --project symnera-website --per-source-limit 4 \
  --only-queries "dribbble:alexander jorias site:dribbble.com|awwwards:industrial site:awwwards.com/inspiration"
```

**Extract** — whitespace-aware segmentation of each screenshot, heuristic pre-filter on pixel features (contrast, edge density, color variance, tension, focal-point), then a Claude / OpenAI vision call on shortlisted regions. Promoted patterns land in `pattern-library/candidates/` with structured signals (typography scale/alignment/density, composition symmetry/dominant/balance, contrast, rhythm) + a human-readable `insight`.

```bash
# heuristic only — fast, free
python3 scripts/extract_pattern_signals.py --project symnera-website --input-dir raw

# + vision grading (OpenAI gpt-4o with strict json_schema)
python3 scripts/extract_pattern_signals.py --project symnera-website --input-dir raw \
  --vision --vision-backend openai

# + vision grading (Claude Sonnet 4.6)
python3 scripts/extract_pattern_signals.py --project symnera-website --input-dir raw \
  --vision --vision-backend anthropic
```

Combined score = `0.4 × heuristic + 0.6 × vision`. Default promote gate is `0.70`.

---

## Setup

```bash
# Python deps
python3 -m pip install --user Pillow numpy

# .env (gitignored)
FIRECRAWL_API_KEY=fc-...
UNSPLASH_ACCESS_KEY=...
ANTHROPIC_API_KEY=sk-ant-...    # optional, for Claude vision backend
OPENAI_API_KEY=sk-proj-...      # optional, for OpenAI vision backend
```

Only the keys you actually use are required. `extract_pattern_signals.py` runs heuristic-only without any LLM key.

---

## Pattern output — what the workflow actually produces

Each pattern JSON conforms to `workflow/pattern-schema.json`. A shortened example (Alexander Jorias "Precision Engineering" hero — the Symnera anchor):

```json
{
  "id": "pattern_hero_editorial_390c93",
  "source": "dribbble",
  "source_url": "https://dribbble.com/shots/27070066-...",
  "region": "hero",
  "score": 0.774,
  "score_breakdown": { "heuristic": 0.511, "vision": 0.95, "weighted": 0.774 },
  "signals": {
    "typography": { "scale": "extreme", "alignment": "centered", "density": "normal" },
    "composition": { "symmetry": "symmetrical", "dominant": "text", "balance": "centered" },
    "contrast": "high",
    "rhythm": "structured"
  },
  "insight": "Bold, confident typographic presence with strong contrast and a clear focal point, embodying an editorial and industrial aesthetic.",
  "tags": ["editorial", "dark", "grounded", "industrial", "confident"]
}
```

These patterns — not raw screenshots — are what downstream Figma generation references.

---

## Figma integration

Figma builds happen via MCP (`use_figma`) and follow the skills in `.claude/skills/stages/07-design-system.md` and `.claude/skills/stages/08-figma-build.md`. The pattern-library provides the visual direction; the asset library provides the imagery.

---

## Hard rules

- **Raw screenshots are never inspiration.** They are traceability for the extractor.
- **Only extracted patterns flow downstream.** Curate `pattern-library/candidates/` → `approved/`.
- **No secrets in commits.** `.env`, `.claude/settings.local.json`, `*.pem`, `*.key`, `credentials.json` are gitignored.
- **Ask before pushing** — see [Claude Code memory](./.claude/).

---

## License

Source code: internal use. Inspiration captures retain their original creators' copyrights — `pattern-library/approved/` content is for reference only, not redistribution.
