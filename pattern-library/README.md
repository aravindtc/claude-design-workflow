## pattern-library/

Structured design patterns extracted from raw inspiration captures. These — not screenshots — are the actual inspiration output the rest of the workflow consumes.

### Hard rules

- **Raw screenshots are NEVER inspiration.** They live in `inspiration/<project>/raw/` for traceability only.
- **Patterns are produced by `scripts/extract_pattern_signals.py`**, which segments screenshots into regions, pre-filters with pixel heuristics, then (optionally) grades shortlisted regions with a vision LLM.
- **Only regions scoring ≥ 0.7** after combined scoring get promoted to `candidates/`. The user curates `candidates/` → `approved/`.

### Layout

```
pattern-library/
  candidates/
    pattern_<region>_<style>_<hash>.json   # one file per pattern
    pattern_<region>_<style>_<hash>.png    # cropped region image (copy of segments/)
  approved/                                # curated set used downstream
```

### Pattern structure

See [`workflow/pattern-schema.json`](../workflow/pattern-schema.json) for the full schema. Core fields:

- `region` — hero / band / feature-grid / testimonial / pricing / cta / footer / unknown
- `score` — weighted heuristic + vision score in `[0, 1]`
- `signals.typography` — scale, alignment, density
- `signals.composition` — symmetry, dominant, balance
- `signals.contrast` — high / medium / low
- `signals.rhythm` — repetitive / structured / loose / none
- `insight` — 1–2 sentence human-readable explanation
- `avoid` — where NOT to apply this pattern

### Run

```
# heuristic pre-filter only (fast, free)
python3 scripts/extract_pattern_signals.py --project symnera-website

# heuristic + vision grading (needs ANTHROPIC_API_KEY)
python3 scripts/extract_pattern_signals.py --project symnera-website --vision
```
