# scripts/

Python scripts that execute the side-effect parts of the workflow —
API calls, file I/O, Figma uploads, state mutations.

Design: all scripts read from and write to
`workflow/projects/<id>/project-state.json`. They never hold state
in memory across invocations.

## Planned modules

| File | Stage | Purpose |
|---|---|---|
| `state.py` | all | Typed read/write helpers for `project-state.json` |
| `validate_briefs.py` | 05 | Validate briefs against `workflow/asset-schema.json` |
| `generate_asset_briefs.py` | 05 | Orchestrates asset-need-engine; produces briefs |
| `retrieve_assets.py` | 06 | Orchestrates asset-retrieval-engine; fetches candidates |
| `approve_assets.py` | 06 | Moves `candidates/` → `approved/`; updates gates |
| `generate_review_frame.py` | 06 | Creates Figma review frame for candidates |
| `import_assets_to_figma.py` | 08 | Uploads approved assets to target Figma frames |
| `adapters/` | 06 | Per-source modules: unsplash, pexels, firecrawl, svgrepo |

All TBD — written in Phase C (see `.claude/skills/stages/06-asset-retrieval.md`).

## Conventions

- Python 3.11+.
- Dependencies declared in `pyproject.toml` (TBD).
- API keys read from environment variables, not files. Document required
  env vars in each adapter's README.
- Every script is callable via `python scripts/<name>.py --project <id>`.
- Every script logs to stdout in a human-readable format; errors exit
  non-zero.
- Idempotent where reasonable: rerunning retrieve_assets on the same
  brief within the cache TTL is free.

## Auth & secrets

Environment variables expected (not all required — depends on brief
sources):

```
UNSPLASH_ACCESS_KEY=...
PEXELS_API_KEY=...
FIRECRAWL_API_KEY=...
ADOBE_STOCK_KEY=...
```

Put these in a local `.env` file (git-ignored) and load via
`python-dotenv`.
