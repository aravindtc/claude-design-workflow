# Adapter — Unsplash

## Auth
- Env var: `UNSPLASH_ACCESS_KEY`
- Free tier: 50 requests/hour.

## API
- Endpoint: `GET https://api.unsplash.com/search/photos?query=<q>&per_page=<n>`
- Response: photo objects with `id`, `urls.regular`, `urls.full`,
  `user.name`, `user.links.html`, `description`, `alt_description`.

## Normalized candidate output
```python
{
    "source": "unsplash",
    "source_id": photo["id"],
    "url": photo["links"]["html"],
    "download_url": photo["urls"]["full"],
    "attribution": f"Photo by {photo['user']['name']} on Unsplash",
    "license": "unsplash-license",
    "license_url": "https://unsplash.com/license",
    "dimensions": [photo["width"], photo["height"]],
    "tags": [t["title"] for t in photo.get("tags", [])],
    "description": photo.get("alt_description") or photo.get("description"),
}
```

## Rate limiting
On 429 or hourly cap: back off exponentially (1s → 60s, 3 retries).
After exhausting retries, skip Unsplash for this run and log the
blockage to metadata.

## Attribution requirement
Unsplash license requires crediting the photographer when using images
in a public context. Store `attribution` in metadata and surface it in
the Figma review frame.

## Implementation
Python module: `scripts/adapters/unsplash.py` (TBD in Phase C).
