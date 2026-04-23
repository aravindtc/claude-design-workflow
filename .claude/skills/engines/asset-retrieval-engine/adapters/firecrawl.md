# Adapter — Firecrawl (open-web)

## Auth
- Env var: `FIRECRAWL_API_KEY`
- Pricing: paid service (see firecrawl.dev).

## When to use
Firecrawl is a web-crawl tool, not a stock-photo source. Use it when:
- A brief calls for `open_web` scraping (e.g. pulling from a
  specific competitor's public asset URLs).
- The brief references a site-scoped query ("images from that
  manufacturer's case studies page").
- Stock sources fail and the user provides specific URLs to crawl.

Do **not** use Firecrawl as a generic photo search. It's expensive and
inefficient for that.

## Query shape
Unlike Unsplash/Pexels, Firecrawl queries are URL-scoped:
```python
{
    "url": "https://example.com/gallery",   # target page
    "extract": ["images"],                   # what to pull
    "filters": {
        "min_width": 1200,
        "formats": ["jpg", "png", "webp"]
    }
}
```
The retrieval-prompt translates a brief into a list of candidate URLs
to crawl, or into a scoped search (`site:example.com industrial
aerial`) when used with Firecrawl's search mode.

## Normalized output
```python
{
    "source": "firecrawl",
    "source_id": f"{domain}-{sha1(url)[:8]}",
    "url": image_url,                        # where the image lives
    "download_url": image_url,
    "attribution": f"Source: {domain}",
    "license": "unknown",                    # critical: flag user-review
    "license_url": None,
    "dimensions": dimensions_if_available,
    "tags": extracted_alt_tags,
    "description": alt_text,
    "warnings": ["license_unknown"]
}
```

## License warning
Firecrawl pulls images from arbitrary web pages. Their licenses are
generally **not free-to-use**. The adapter MUST flag every firecrawl
candidate with `warnings: ["license_unknown"]` and the user MUST
manually clear licensing before approving such candidates for
production use.

The approval UI should show a red badge on firecrawl candidates.

## Rate limiting
Respect Firecrawl's rate limits; respect source-site robots.txt.

## Implementation
Python module: `scripts/adapters/firecrawl.py` (TBD in Phase C).
