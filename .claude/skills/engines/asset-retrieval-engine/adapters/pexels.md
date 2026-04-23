# Adapter — Pexels

## Auth
- Env var: `PEXELS_API_KEY`
- Free tier: 200 requests/hour.

## API
- Endpoint: `GET https://api.pexels.com/v1/search?query=<q>&per_page=<n>`
- Auth via `Authorization: <PEXELS_API_KEY>` header.

## Normalized output
```python
{
    "source": "pexels",
    "source_id": str(photo["id"]),
    "url": photo["url"],
    "download_url": photo["src"]["original"],
    "attribution": f"Photo by {photo['photographer']} on Pexels",
    "license": "pexels-license",
    "license_url": "https://www.pexels.com/license/",
    "dimensions": [photo["width"], photo["height"]],
    "tags": [],
    "description": photo.get("alt"),
}
```

## Rate limiting
429 handling same as Unsplash.

## Attribution
Not strictly required by license, but we include it for consistency with
Unsplash — users can drop attribution from the final published page if
preferred.

## Implementation
Python module: `scripts/adapters/pexels.py` (TBD in Phase C).
