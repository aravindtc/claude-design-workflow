## inspiration/

Design inspiration references harvested from designer sites (Awwwards, SiteInspire, Land-book, Dribbble, Behance, etc.) and scored against a brand-inspiration brief.

### Layout

```
inspiration/
  <project>/
    briefs/               # brand-inspiration brief JSON (author manually)
    candidates/           # scraped references (one folder per candidate)
      <source>-<slug>-<hash8>/
        screenshot.png    # full-page screenshot (primary training signal)
        page.md           # Firecrawl markdown (text + structure)
        preview.jpg       # og:image thumbnail fallback
        metadata.json     # url, source, author, tags, engagement, score
    approved/             # user-curated references promoted out of candidates
    metadata/
      inspiration.json    # aggregate: all candidates + scores
      approval-log.json   # which candidates got promoted, when, by whom
```

### Run

```
python3 scripts/retrieve_inspiration.py --project symnera-website
```

### Scoring (v0.1)

Each candidate gets a normalized score in `[0, 1]` from:
- **aesthetic_match** — keyword overlap between brief `aesthetic` tags and scraped title/description/tags
- **pattern_match** — brief `patterns_wanted` keywords present in scraped content
- **source_authority** — curation quality weight per source (Awwwards 1.0, SiteInspire 0.95, Land-book 0.9, …)
- **engagement** — likes/views when extractable from source markdown (Dribbble/Behance)

Pixel-level palette matching is **not** implemented in v0.1 — add in v0.2 with Pillow.

### Legal / ToS

Only public-facing pages are scraped via Firecrawl. No authentication, no bypassing paywalls. Attribution is preserved in every `metadata.json`. If you promote something to `approved/`, respect the original author's license for any downstream use.
