# assets/

Project-scoped asset storage. Each project gets its own subdirectory
keyed by `project_id` from `workflow/projects/<id>/project-state.json`.

## Structure

```
assets/
└── <project_id>/
    ├── briefs/              Plan — one JSON per section, schema-validated
    │   ├── index.json       Summary of all briefs + approval status
    │   ├── hero.json
    │   └── problem.json
    ├── candidates/          Raw — retrieved images, not yet approved
    │   ├── hero/
    │   │   ├── 01-unsplash-abc123.jpg
    │   │   ├── 02-pexels-def456.jpg
    │   │   └── 03-firecrawl-example-com-xyz.jpg
    │   └── problem/
    ├── approved/            Curated — user-picked shortlist, ready for Figma import
    │   ├── hero/
    │   │   ├── hero-01.jpg
    │   │   └── hero-02.jpg
    │   └── problem/
    └── metadata/            Audit — candidate metadata and approval log
        ├── hero.json
        ├── problem.json
        └── approval-log.json
```

## Flow

```
stage 05              stage 06 retrieval         stage 06 approval         stage 08
asset-need-engine     asset-retrieval-engine     approve_assets.py         import_assets_to_figma.py
┌───────────────┐     ┌───────────────────┐     ┌────────────────────┐    ┌──────────────────┐
│  briefs/*.json│ ──▶ │ candidates/ +     │ ──▶ │ approved/ (moved)  │──▶ │ Figma image fill │
│  (approved)   │     │ metadata/*.json   │     │ metadata updated   │    │                  │
└───────────────┘     └───────────────────┘     └────────────────────┘    └──────────────────┘
          gate: asset_briefs_approved              gate: assets_approved       gate: figma_build_approved
```

## Gate rules

- Entering `candidates/` means nothing is approved yet.
- Moving from `candidates/` to `approved/` is a deliberate action
  (script or user command). The move is the approval act.
- Anything in `approved/` is ready for `scripts/import_assets_to_figma.py`.
- Files that ship to Figma but later get swapped stay tracked in
  `metadata/approval-log.json` so the history is auditable.

## License hygiene

Every candidate metadata entry records `license` and (where relevant)
`license_url`. Candidates from sources like Firecrawl with unknown
licenses are flagged with `warnings: ["license_unknown"]` and must be
user-cleared before approval.

## Size and git

Images in `candidates/` and `approved/` are binary files. For small
projects (under a few hundred MB) it's fine to track them in git.
For larger projects, consider:
- Git LFS for `assets/*/approved/` and `assets/*/candidates/`
- Or an `.gitignore` entry that ignores binary assets and tracks only
  metadata + briefs

Default: we track everything. Revisit if repo size becomes a problem.
