# claude-design-workflow

A design workflow that pairs **Claude Code** with **Figma MCP**, **Firecrawl**, **Unsplash**, and a **vision LLM** (Claude or OpenAI) to produce brand-specific design systems — end-to-end, from inspiration capture to Figma build.

The core idea: replace "collect screenshots and hope" with a structured pipeline that segments web captures, scores each region, and extracts **reusable design signals** as structured data, so downstream Figma generation has real references to work from instead of a folder full of thumbnails.

---

## Table of contents

1. [Mental model](#mental-model)
2. [Systems used](#systems-used)
3. [Folder layout](#folder-layout)
4. [Pipeline A — Asset retrieval (photos, vectors)](#pipeline-a--asset-retrieval)
5. [Pipeline B — Inspiration → Design patterns](#pipeline-b--inspiration--design-patterns)
6. [How extraction actually works (step by step)](#how-extraction-actually-works-step-by-step)
7. [Scoring reference](#scoring-reference)
8. [Schemas](#schemas)
9. [Setup](#setup)
10. [Figma integration](#figma-integration)
11. [Hard rules](#hard-rules)

---

## Mental model

A brand + section gives rise to two kinds of needs:

- **Assets** — concrete images / vectors / illustrations for specific sections of the page (hero photo, logo variants, supporting imagery).
- **Inspiration** — patterns of composition, typography, rhythm, and contrast that should inform how those sections are *designed* (not what they contain).

The repo has one pipeline for each. They share a folder convention (`<project>/briefs/ + candidates/ + approved/`), share the `.env` secrets file, and share a "user curates candidates into approved" discipline. But they answer different questions.

```
                            ┌─────────────────────────┐
                            │  brief (JSON)           │
                            │  — brand, sections,     │
                            │    aesthetic, avoid     │
                            └─────────────┬───────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
           ┌────────────────┐                          ┌──────────────────┐
           │ Asset pipeline │                          │  Inspiration →   │
           │  (Unsplash +   │                          │  Pattern library │
           │   Firecrawl)   │                          │  (Firecrawl +    │
           │                │                          │   vision LLM)    │
           └───────┬────────┘                          └─────────┬────────┘
                   ▼                                             ▼
           candidates/ → approved/                candidates/ → approved/
           (jpg/png + metadata)                  (structured pattern JSONs)
                   │                                             │
                   └────────────────┐          ┌────────────────┘
                                    ▼          ▼
                              Figma MCP build (use_figma)
```

---

## Systems used

| System | Role | Why |
|---|---|---|
| **Firecrawl** | `/v1/search` for URL discovery; `/v1/scrape` with `screenshot@fullPage` for full-page captures + markdown | handles JS rendering, dynamic content, and returns both markdown + a hosted full-page PNG in one call |
| **Unsplash API** | `/search/photos` for stock photo candidates | CC-licensed, landscape-orientable, has `description` text we can score against briefs |
| **Pillow + numpy** | Image segmentation (whitespace-gutter detection) and pixel-feature heuristics | cheap, deterministic, no network — good pre-filter before expensive vision calls |
| **Anthropic API** (Claude Sonnet 4.6) | vision LLM backend A | strong structured-critique behaviour; good adherence to rubric language |
| **OpenAI API** (gpt-4o) | vision LLM backend B | `response_format: json_schema` with `strict: true` — guarantees valid JSON, eliminates parse failures |
| **Figma MCP** (`use_figma`) | Render pattern library + assets into components, variants, and full-page mockups | native to Claude Code; drives the final design-system output |

The pipeline is **backend-agnostic** on the vision step — you can use either LLM provider via `--vision-backend {anthropic,openai}`, fall back to heuristics-only if you have neither, and the output schema is identical.

---

## Folder layout

```
workflow/                         schemas + pipeline manifest
  stages.yaml                       10-stage definition
  asset-schema.json                 AssetBrief: per-section asset requests
  inspiration-schema.json           InspirationBrief: brand-level aesthetic brief
  pattern-schema.json               Pattern: extracted design-signal output

.claude/skills/
  stages/                           10 SKILL.md files, one per pipeline stage
  engines/                          reusable skills (asset-need, asset-retrieval)

scripts/                          Python CLIs
  retrieve_assets.py                Unsplash + Firecrawl → candidate images
  retrieve_inspiration.py           Firecrawl → raw page captures
  extract_pattern_signals.py        segment → heuristics → vision LLM → patterns

assets/<project>/                 imagery lifecycle
  briefs/                           AssetBrief JSONs (per section)
  candidates/                       downloaded candidates from retrieve_assets
  approved/                         user-approved final images (what Figma uses)
  metadata/                         approval-log, cached API responses

inspiration/<project>/            web capture lifecycle
  briefs/brand.json                 InspirationBrief
  raw/<capture-id>/                 full-page screenshots + page.md + preview.jpg
  segments/<capture-id>/            cropped regions written by extractor
  metadata/                         discovery aggregate + extraction summary

pattern-library/                  THE output — structured design patterns
  candidates/                       patterns scoring ≥ 0.70 (JSON + PNG per)
  approved/                         user-curated anchor set
  ratings.json                      user ratings on captures (informs future crawls)
```

---

## Pipeline A — Asset retrieval

**Input:** one `AssetBrief` per section (`assets/<project>/briefs/<section>.json`). Defines `asset_type`, `role`, `style` prose, `mood`, `orientation`, `aspect_ratio`, `variants` (how many candidates to keep), `avoid` list, `sources` priority list.

**What the script does** (`scripts/retrieve_assets.py`):

1. Expand brief tags into search queries (e.g. `"industrial factory aerial landscape"`).
2. Hit each source in priority order — Unsplash first for photos, Firecrawl for open-web scraping.
3. For each returned item, score it:
   - Keyword overlap between query terms (+ synonym expansion) and the item's `alt_description` / page text
   - People / office-cliché penalties (configurable signal sets)
   - Composition-type bonuses (`aerial`, `architectural`, `geometric`)
4. Keep top N by score, download them to `candidates/<section>/`, write per-candidate metadata + attribution.
5. User reviews candidates, picks one, system records approval in `metadata/approval-log.json`, copies winner to `approved/<section>/`.

```bash
python3 scripts/retrieve_assets.py --project symnera-website --section hero
```

Supported sources (extensible via `scripts/adapters/`): Unsplash, Pexels, Pixabay, Adobe Stock, SVGRepo, Iconify, Firecrawl (open-web).

---

## Pipeline B — Inspiration → Design patterns

This is the more novel pipeline. Instead of "save screenshots to a folder and hope", it treats each web capture as **raw material** and extracts structured design signals.

**Input:** one `InspirationBrief` per project (`inspiration/<project>/briefs/brand.json`). Defines brand colors, aesthetic tags (e.g. `editorial`, `dark`, `industrial`, `lime-accent`), `patterns_wanted` (hero / feature-grid / pricing / …), avoid list, and source list (Awwwards, SiteInspire, Dribbble, Behance, etc.).

**Two scripts run back to back.**

### Step 1 — Capture (`retrieve_inspiration.py`)

```bash
python3 scripts/retrieve_inspiration.py --project symnera-website --per-source-limit 4
```

```
                ┌─────────────────────────┐
brief.json ─►  │ build_queries()         │   ("dark editorial industrial
                │ per-source query tuples │    site of the day site:awwwards.com")
                └───────────┬─────────────┘
                            ▼
                ┌─────────────────────────┐
                │ Firecrawl /v1/search    │   for each query
                └───────────┬─────────────┘
                            ▼
                ┌─────────────────────────┐
                │ URL-pattern filter      │   per-source allow/deny regex
                │ (drops gallery/listing/ │   — e.g. reject /search, /tags/,
                │  search / tag pages)    │     /browse, /websites/ listings
                └───────────┬─────────────┘
                            ▼
                ┌─────────────────────────┐
                │ Firecrawl /v1/scrape    │   formats: ["markdown",
                │ with screenshot@fullPage│              "screenshot@fullPage"]
                └───────────┬─────────────┘
                            ▼
                inspiration/<project>/raw/<capture-id>/
                    screenshot.png  (1920 × N)
                    page.md         (Firecrawl markdown)
                    preview.jpg     (og:image)
                    metadata.json   (url, title, discovery_filter trace)
```

Key design choices:

- **Per-source URL allow/deny regex** (`SOURCE_URL_FILTERS` dict) means searches for `"industrial hero site:dribbble.com"` reject `/search/…`, `/browse/…`, `/tags/…` URLs and only accept `/shots/<id>` individual showcase URLs. Same for every source — Awwwards `/sites/` or `/inspiration/`, Siteinspire `/websites/<id>`, Httpster `/website/<slug>`, etc.
- **`--only-queries` flag** bypasses brief-derived queries for "more like X" targeted runs — crucial for fast iteration once you find an anchor pattern you want more of.
- **Capture-only** — this script does *not* score for design signal. It just decides whether a URL is worth scraping (URL filter + source-authority weighting) and writes raw bytes. Real scoring happens against pixels in the next step.

### Step 2 — Extract (`extract_pattern_signals.py`)

```bash
python3 scripts/extract_pattern_signals.py --project symnera-website \
  --input-dir raw --vision --vision-backend openai
```

```
inspiration/<project>/raw/<id>/screenshot.png
                    │
                    ▼
           ┌─────────────────────────┐
           │ segment_image()         │   whitespace-aware horizontal cut
           │ — row-variance gutters  │   → regions labeled nav / hero /
           └───────────┬─────────────┘     band / footer
                       ▼
           ┌─────────────────────────┐
           │ compute_features()      │   per region, pixel statistics:
           │ — contrast_ratio        │   — luminance p95 / p05
           │ — edge_density          │   — PIL FIND_EDGES > threshold
           │ — color_variance        │   — std across RGB channels
           │ — whitespace_ratio      │   — pixels near dominant bg color
           │ — tension               │   — std of edge-density across quads
           │ — focal_point           │   — max/mean quadrant edge density
           │ — palette_top           │   — 5 dominant colors
           │ — low_signal_flags      │   — nav_like / footer_like /
           └───────────┬─────────────┘      near_empty / uniform_grid
                       ▼
           ┌─────────────────────────┐
           │ heuristic_score()       │   weighted combination;
           │ HEURISTIC_GATE = 0.45   │   hard kills on nav / near-empty;
           └───────────┬─────────────┘   soft penalties on uniform grids
                       ▼
              shortlisted regions only
                       ▼
           ┌─────────────────────────┐
           │ vision_grade_region()   │   Claude Sonnet or OpenAI gpt-4o
           │ — structured rubric     │   returns score_vision ∈ [0,1] +
           │ — strict JSON schema    │   signals{typography, composition,
           │   (OpenAI) or rubric-   │           contrast, rhythm} +
           │   enforced (Claude)     │   region_guess + insight + avoid
           └───────────┬─────────────┘
                       ▼
           weighted = 0.4 · heuristic + 0.6 · vision
           PROMOTE_GATE = 0.70
                       ▼
           ┌─────────────────────────┐
           │ build_pattern() +       │   pattern-library/candidates/
           │ write_pattern()         │     pattern_<region>_<style>_<h>.json
           └─────────────────────────┘     pattern_<region>_<style>_<h>.png
```

The heuristic stage exists to **cheaply pre-filter** — running vision on every region of every capture is wasteful when ~40% of regions are navigation / footer / empty bands that can be killed by pixel statistics. The vision stage exists to provide the judgment heuristics can't: "is this an editorial hero, or a busy product grid?" — questions you can't answer from edge-density alone.

### Real example

Symnera crawl, targeted queries, 6 screenshots → 57 regions → 26 shortlisted by heuristics → **19 promoted** by combined score ≥ 0.70. One of the top patterns:

```json
{
  "id": "pattern_hero_editorial_390c93",
  "source": "dribbble",
  "source_url": "https://dribbble.com/shots/27070066-Hero-Design-Concept-for-Industrial-Engineering-Company",
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

Notice the heuristic gave it only 0.511 — pixel statistics couldn't tell it apart from a busy product grid. The vision LLM scored it 0.95 because it could see the editorial typographic move. The combined 0.774 pushed it past the gate. This is exactly what the two-stage architecture is for.

---

## How extraction actually works (step by step)

Walking through one capture from screenshot to pattern JSONs:

### 1. Whitespace-aware segmentation

Input: `1920 × N` PNG screenshot. Goal: cut horizontally into logical regions.

```python
gray = np.asarray(im.convert("L"))     # grayscale
row_var = gray.var(axis=1)              # per-row pixel variance
gutters = runs where row_var < 8.0 for ≥ 18 consecutive rows
cut_ys  = [0] + [midpoint(gutter) for gutter in gutters] + [H]
```

Each `(cut_ys[i], cut_ys[i+1])` is a region. Regions shorter than `MIN_REGION_HEIGHT = 260px` are discarded (except the very first strip up to `NAV_MAX_HEIGHT = 120px` which is kept as "nav" so it can be explicitly filtered later).

Labels assigned by position within the kept set:
- First kept region, ≤ 120px tall → `nav`
- First (or second, if preceded by `nav`) → `hero`
- Last, if its bottom is in the bottom 15% of the page → `footer`
- Everything else → `band`

### 2. Pixel features

For each region, compute:

| Feature | Formula | What it measures |
|---|---|---|
| `contrast_ratio` | `luminance_p95 / max(luminance_p05, 1)` | dynamic range |
| `edge_density` | `count(FIND_EDGES > 24) / total_pixels` | visual complexity |
| `color_variance` | `std across RGB channels, averaged` | palette richness |
| `whitespace_ratio` | `fraction of pixels within 8-unit distance of dominant bg color` | emptiness |
| `tension` | `std of edge-density across 2×2 quadrants` | asymmetric distribution of content |
| `focal_point` | `max quadrant edge-density / mean` | concentrated vs scattered |
| `palette_top` | 5 most-frequent colors quantized to 16-level | brand-palette check |
| `low_signal_flags` | `{nav_like, footer_like, near_empty, uniform_grid, too_short}` | hard/soft kills |

### 3. Heuristic score

```python
score = (
    0.30 * normalize(contrast_ratio,  1.2, 10.0)
  + 0.22 * normalize(edge_density,    0.01, 0.18)
  + 0.18 * normalize(color_variance,  12.0, 70.0)
  + 0.18 * normalize(tension,         0.005, 0.08)
  + 0.12 * normalize(focal_point,     1.1, 2.2)
)
# hard kills → 0.0 (nav_like, near_empty, too_short)
# soft penalties: uniform_grid × 0.6, footer_like × 0.3
```

Regions scoring `< HEURISTIC_GATE (0.45)` are **skipped before vision** — this is the credit-saving pre-filter. Typically 40–60% of regions die here.

### 4. Vision grading (optional)

Shortlisted regions are downscaled to ≤ 1568px on the long edge (Anthropic's recommended image size), base64-encoded, and sent to the chosen backend with a single rubric prompt:

- **Anthropic backend** — `POST /v1/messages` with a detailed rubric asking for JSON output. Parse with regex-stripping of accidental ``` ```json ``` ``` fences.
- **OpenAI backend** — `POST /v1/chat/completions` with `response_format: { type: "json_schema", strict: true }` — the model is physically incapable of returning malformed JSON. No fence-stripping, no parse fallbacks.

Both return the same shape:

```json
{
  "score_vision": 0.95,
  "signals": { "typography": {...}, "composition": {...}, "contrast": "high", "rhythm": "structured" },
  "region_guess": "hero",
  "insight": "...",
  "avoid": ["..."],
  "tags": ["editorial", "dark", "industrial"]
}
```

Combined score = `0.4 × heuristic + 0.6 × vision`. If vision fails (network error, quota limit), the combined score falls back to heuristic-only, the script logs the failure, and the pattern still gets written (with `vision: null` in its `score_breakdown`).

### 5. Promotion

Regions with combined score `≥ PROMOTE_GATE (0.70)` are:

1. Copied as cropped PNG to `pattern-library/candidates/<pattern_id>.png`
2. Written as structured JSON to `pattern-library/candidates/<pattern_id>.json` conforming to `workflow/pattern-schema.json`

Pattern IDs encode the vision-classified region + the top `tag` + a short hash of `(capture_id, y, height)` for idempotency. Re-running the extractor on the same input is safe and deterministic.

### 6. Curation

`pattern-library/candidates/` is the machine's best guess. The user curates into `approved/`, either by moving JSONs + PNGs manually, or by rating in `ratings.json` and letting a future helper promote high-rated captures.

---

## Scoring reference

**Discovery-layer source authority** (used in `retrieve_inspiration.py`'s URL filter to break ties):

| Source | Weight |
|---|---|
| awwwards | 1.00 |
| siteinspire | 0.95 |
| land-book | 0.90 |
| godly | 0.85 |
| mobbin | 0.80 |
| behance | 0.75 |
| httpster | 0.70 |
| dribbble | 0.65 |
| open_web | 0.50 |

**Heuristic weights** (pixel features → pre-filter score):

| Feature | Weight | Normalized range |
|---|---|---|
| contrast_ratio | 0.30 | [1.2, 10] |
| edge_density | 0.22 | [0.01, 0.18] |
| color_variance | 0.18 | [12, 70] |
| tension | 0.18 | [0.005, 0.08] |
| focal_point | 0.12 | [1.1, 2.2] |

**Gates:**

- `HEURISTIC_GATE = 0.45` — advance to vision
- `PROMOTE_GATE = 0.70` — write to `pattern-library/candidates/`
- `weighted = 0.4 × heuristic + 0.6 × vision`

All thresholds live as module-level constants in `scripts/extract_pattern_signals.py` and can be tuned.

---

## Schemas

All JSON written by the workflow validates against schemas in `workflow/`:

- **`asset-schema.json`** — per-section asset request (`section`, `need_asset`, `asset_type`, `role`, `style`, `mood`, `orientation`, `variants`, `avoid`, `sources`, `license_requirements`, `approval`).
- **`inspiration-schema.json`** — brand-level inspiration brief (`project`, `brand`, `aesthetic`, `patterns_wanted`, `avoid`, `sources`, `max_candidates_per_source`, `min_score`, `approval`).
- **`pattern-schema.json`** — extracted pattern object (`id`, `source`, `region`, `bbox`, `score`, `score_breakdown`, `features_heuristic`, `signals.{typography, composition, contrast, rhythm}`, `insight`, `avoid`, `tags`). This is what downstream Figma generation consumes.

---

## Setup

```bash
# Python deps
python3 -m pip install --user Pillow numpy

# .env at repo root (gitignored)
FIRECRAWL_API_KEY=fc-...
UNSPLASH_ACCESS_KEY=...
ANTHROPIC_API_KEY=sk-ant-...    # optional, for Claude vision backend
OPENAI_API_KEY=sk-proj-...      # optional, for OpenAI vision backend
```

Only the keys you actually use are required. `extract_pattern_signals.py` runs heuristic-only without any LLM key — you'll just get `vision: null` in pattern score breakdowns.

---

## Figma integration

Figma builds happen via MCP (`use_figma`) and follow the skills in `.claude/skills/stages/`:

- `07-design-system.md` — create variables, text styles, effect styles; build base components with variants
- `08-figma-build.md` — compose pages + full-page mockups using patterns from `pattern-library/approved/` and imagery from `assets/<project>/approved/`

The pattern-library provides the visual direction (typography scale, composition, rhythm); the asset library provides the imagery. Figma components bind tokens to design variables so both can evolve without touching every page.

---

## Hard rules

- **Raw screenshots are never inspiration.** They live in `inspiration/<project>/raw/` for traceability only. Only extracted patterns in `pattern-library/` flow downstream.
- **Patterns are machine output until approved.** `candidates/` is algorithm's best guess; `approved/` is human-curated truth.
- **No secrets in commits.** `.env`, `.claude/settings.local.json`, `*.pem`, `*.key`, `credentials.json` are gitignored. CI scans staged diffs for known key prefixes before any push.
- **Ask before pushing.** `git push` is user-approved only; not automated.
- **Atomic scripts.** Failed runs leave partial output only where explicitly logged (`segments/` may contain written crops from a failed vision run — those are safe to delete and re-run).

---

## License

Source code: internal use. Inspiration captures retain their original creators' copyrights — `pattern-library/approved/` content is a reference set for design-direction decisions, not for redistribution or publication.
