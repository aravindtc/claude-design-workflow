# Adapter — SVGRepo

## Auth
SVGRepo does not require auth for read-only catalog access. If using
their API, check current docs for any key requirements.

## When to use
- `asset_type: vector` or `asset_type: icon`.
- Need a free, CC-licensed SVG.

## Query shape
Plain text, single concept:
- `factory`
- `warehouse`
- `arrow right`

No style adjectives — SVGRepo search is literal.

## Normalized output
```python
{
    "source": "svgrepo",
    "source_id": str(svg["id"]),
    "url": svg["page_url"],
    "download_url": svg["svg_url"],
    "attribution": svg.get("author", "SVGRepo"),
    "license": svg.get("license", "CC0"),
    "license_url": "https://www.svgrepo.com/page/licensing/",
    "dimensions": None,
    "tags": svg.get("tags", []),
    "description": svg.get("title"),
}
```

## Note on file handling
SVGs get stored as `.svg` directly. Downstream Figma import uses
`figma.createNodeFromSvg(svgString)`; no raster conversion needed.

## Implementation
Python module: `scripts/adapters/svgrepo.py` (TBD in Phase C).
