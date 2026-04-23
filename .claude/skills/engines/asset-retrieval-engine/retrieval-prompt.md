# Retrieval Query Generation Prompt

Query writer for the asset-retrieval-engine. Receives an `AssetBrief`
and a target source; returns 3–5 queries tuned for that source plus the
avoid-term list.

## Inputs
- `brief` — a fully approved AssetBrief (see `workflow/asset-schema.json`)
- `source` — one of the enums in `brief.sources`

## Thinking steps (internal)
1. Read the brief. Identify the **visual intent** in one sentence:
   what will the viewer see, and why does the layout need it?
2. Decide the composition cue based on `brief.role`:
   - `primary_anchor` → full-bleed, wide, aerial, or editorial hero cue
   - `supporting` → card-sized, clean subject, room for text overlay
   - `background` → texture-y, low contrast, non-dominant subject
   - `decorative` → single-concept, simple silhouette
3. Draft 3–5 diverse queries varying along at least two of:
   - **Subject phrasing** — literal vs evocative
   - **Style cues** — aesthetic modifiers (editorial, minimal, muted, documentary)
   - **Composition cues** — aerial, close-up, wide, detail, overhead
4. Remove any query that contains a term in `brief.avoid`.
5. Add source-specific modifiers:
   - `unsplash` — short, strong nouns + one style modifier
   - `pexels` — slightly more literal subject phrases
   - `firecrawl` — narrower, exact phrasing targeted at known URLs or
     site-restricted queries
   - `svgrepo` / `iconify` — single concept only, no style adjectives
   - `adobe_stock` — longer tails, include commercial qualifiers
     ("editorial", "royalty-free", "lifestyle")

## Output (JSON, machine-readable)

```json
{
  "section": "hero",
  "source": "unsplash",
  "intent": "industrial factory aerial; precision + calm; no people; no drone-selfie aesthetic",
  "queries": [
    {
      "q": "industrial factory aerial overhead minimal",
      "reason": "matches muted aerial brief; strong Unsplash aerial collections"
    },
    {
      "q": "manufacturing plant top down muted",
      "reason": "alternate phrasing, targets documentary style"
    },
    {
      "q": "refinery aerial editorial",
      "reason": "adjacent subject with same composition cue"
    },
    {
      "q": "power plant overhead geometric",
      "reason": "fallback subject with strong composition"
    }
  ],
  "avoid_terms": ["people", "team", "corporate", "handshake", "drone selfie"],
  "expected_variants": 5
}
```

## Constraints

- Never emit a query containing an `avoid` term.
- Never append generic SaaS cliches (e.g. "hero image", "banner",
  "startup", "teamwork") unless explicitly asked in `brief.style`.
- For `asset_type: "vector" | "icon"`, queries target SVGRepo/Iconify:
  single concept, no style adjectives, no composition cues.
- For `asset_type: "diagram"`, prefer "technical diagram",
  "architecture diagram", "schematic"; skip photo sources entirely.
- For `asset_type: "abstract_texture"`, prefer terms like "texture",
  "pattern", "gradient", "film grain"; avoid representational subjects.

## Anti-patterns
- 5 near-identical queries differing only in minor word swaps.
  Vary at least two dimensions (subject + composition, or style + subject).
- Over-qualifying with more than 5 adjectives. Sources return empty.
- Including the brand name in queries. It biases results toward
  unrelated logos.

## Example — contrast short vs bloated

Brief: `{ section: "hero", style: "editorial industrial minimal", mood: ["grounded", "calm"] }`

- ✅ `industrial factory aerial overhead minimal`
- ✅ `manufacturing plant muted palette editorial`
- ❌ `a beautiful industrial factory aerial overhead minimal editorial
  photography with muted color palette grounded calm mood professional
  high resolution` (too long, confuses source search)
