# Source Priorities

Default ordering per asset type. The asset-need-engine uses these as
priors when populating `brief.sources`. The retrieval engine respects
the order as fan-out priority.

## By asset type

| `asset_type` | Default priority |
|---|---|
| `photo` | `unsplash`, `pexels`, `firecrawl`, `adobe_stock` |
| `vector` | `svgrepo`, `iconify` |
| `illustration` | `adobe_stock`, `open_web` (firecrawl) |
| `icon` | `iconify`, `svgrepo` |
| `abstract_texture` | `unsplash`, `pexels` |
| `diagram` | `firecrawl` (open_web targeted), `adobe_stock` |

## Licensing tiers

| Tier | Sources |
|---|---|
| `cc0` / free | `unsplash`, `pexels`, `pixabay`, `svgrepo`, `iconify` |
| `royalty_free_paid` | `adobe_stock`, `getty` |
| `commercial_only` | force `adobe_stock` / `getty` only; exclude Unsplash for brands with strict legal review |

If `brief.license_requirements = commercial_only`, override defaults
and use paid sources only.

## Provider notes

### Unsplash
- Strong editorial aerials, landscapes, architecture.
- Weak for commercial diversity photography (consistent portraits).
- Consistent API; 50 req/hour on free tier.

### Pexels
- Similar coverage to Unsplash; often has alternatives Unsplash doesn't.
- Slightly weaker curation; may need more fit-scoring.

### Firecrawl
- General-purpose crawler. Use for:
  - Scraping a specific competitor's asset URLs
  - Pulling from niche sites without public APIs
  - Crawling Pinterest-style boards (respect robots.txt + ToS)
- Adds complexity — queries are URL-shaped or site-scoped, not plain text.
- Not a stock photo source; treat as fallback and inspiration channel.

### SVGRepo
- Free SVG library. Huge catalogue, quality variable.
- Use for icon grids and single-concept vectors.

### Iconify
- Icon aggregator across 100+ icon sets.
- Best for consistent icon systems (Phosphor, Lucide, Heroicons).

### Adobe Stock / Getty
- Paid; use only when `license_requirements` demands it or when free
  sources fail a brief.
- Adapter integration is more complex (auth, licensing flow).
