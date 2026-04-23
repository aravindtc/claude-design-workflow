# Asset Brief Template

Starting template for a new asset brief. Copy, fill in, validate against
`workflow/asset-schema.json`.

```json
{
  "section": "<section_id from section_plan>",
  "need_asset": true,

  "asset_type": "photo | vector | illustration | abstract_texture | diagram | icon",
  "role": "primary_anchor | supporting | background | decorative",

  "style": "<one-sentence prose describing desired style>",
  "mood": ["<adjective>", "<adjective>", "<adjective>"],

  "orientation": "landscape | portrait | square | any",
  "aspect_ratio": "16:9",

  "variants": 5,

  "avoid": [
    "generic smiling teams",
    "corporate handshake",
    "<direction-specific avoid>"
  ],

  "sources": ["unsplash", "pexels", "firecrawl"],
  "license_requirements": "any",

  "approval": {
    "status": "draft",
    "approved_at": null,
    "approved_by": null,
    "notes": null
  }
}
```

For a text-only section:

```json
{
  "section": "<section_id>",
  "need_asset": false,
  "approval": {
    "status": "draft",
    "approved_at": null,
    "approved_by": null,
    "notes": "Pure-text section; no imagery required."
  }
}
```
