#!/usr/bin/env python3
"""
Mini asset retrieval pipeline (Phase C — v0.1).

Loads an approved brief, generates queries, calls Unsplash and Firecrawl,
scores candidates, downloads top N, writes metadata.

Does NOT touch Figma — approval happens separately.

Usage:
    python3 scripts/retrieve_assets.py --project symnera-website --section hero
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


# ========== helpers ==========

def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha1_short(s: str, n: int = 8) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:n]


def http_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    payload: dict | None = None,
    timeout: int = 30,
) -> tuple[int, dict | str]:
    data = None
    hdrs = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8", errors="replace")
        except Exception:
            err = str(e)
        return e.code, err
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def download(url: str, dest: Path, timeout: int = 60) -> bool:
    """Download a binary file to `dest`. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "claude-design-workflow/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  download failed for {url}: {e}")
        return False


# ========== query generation ==========

def generate_queries(brief: dict) -> list[str]:
    """
    Rule-based query generator for v0.1. 3 queries.

    Varies: subject core (from style keywords), composition cue, style modifier.
    """
    style = (brief.get("style") or "").lower()
    mood = brief.get("mood") or []
    role = brief.get("role")

    # subject core: pull first noun-ish tokens from style; fallback to "image"
    # For the hero brief, style = "editorial industrial minimal..." -> pick "industrial"
    tokens = [t for t in re.findall(r"[a-z]+", style) if len(t) > 3]
    noun_candidates = [t for t in tokens if t not in {"editorial", "minimal", "grounded", "clean", "muted", "palette", "composition"}]
    subject = noun_candidates[0] if noun_candidates else tokens[0] if tokens else "scene"

    # composition cue by role
    composition = {
        "primary_anchor": "aerial overhead",
        "supporting": "close-up detail",
        "background": "texture",
        "decorative": "minimal",
    }.get(role, "")

    queries: list[str] = []

    # Q1 — subject + composition + style core
    queries.append(f"{subject} {composition} editorial".strip())

    # Q2 — mood-led
    if mood:
        queries.append(f"{subject} {mood[0]} composition minimal")
    else:
        queries.append(f"{subject} architecture minimal")

    # Q3 — alternative phrasing
    alt_subject_map = {
        "industrial": "manufacturing plant",
        "urban": "cityscape",
        "nature": "landscape",
    }
    alt = alt_subject_map.get(subject, subject)
    queries.append(f"{alt} {composition} muted".strip())

    # Dedup and clean
    seen = set()
    out = []
    for q in queries:
        q = re.sub(r"\s+", " ", q).strip()
        if q and q not in seen:
            seen.add(q)
            out.append(q)
    return out


# ========== sources ==========

def search_unsplash(key: str, query: str, per_page: int = 10, orientation: str = "landscape") -> list[dict]:
    qs = urllib.parse.urlencode({
        "query": query,
        "per_page": per_page,
        "orientation": orientation,
    })
    url = f"https://api.unsplash.com/search/photos?{qs}"
    status, body = http_json(url, headers={
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {key}",
    })
    if status != 200 or not isinstance(body, dict):
        print(f"  unsplash error ({status}): {str(body)[:200]}")
        return []
    out = []
    for p in body.get("results", []):
        out.append({
            "source": "unsplash",
            "source_id": p["id"],
            "url": p["links"]["html"],
            "download_url": p["urls"]["full"],
            "preview_url": p["urls"]["regular"],
            "attribution": f"Photo by {p['user']['name']} on Unsplash",
            "license": "unsplash-license",
            "license_url": "https://unsplash.com/license",
            "dimensions": [p.get("width"), p.get("height")],
            "aspect_ratio": None,
            "tags": [t["title"] for t in p.get("tags", [])],
            "description": p.get("alt_description") or p.get("description") or "",
            "warnings": [],
        })
    return out


def search_firecrawl(key: str, query: str, limit: int = 5) -> list[dict]:
    status, body = http_json(
        "https://api.firecrawl.dev/v1/search",
        method="POST",
        headers={"Authorization": f"Bearer {key}"},
        payload={"query": query, "limit": limit},
    )
    if status != 200 or not isinstance(body, dict):
        print(f"  firecrawl search error ({status}): {str(body)[:200]}")
        return []
    out = []
    for r in body.get("data", []) or body.get("results", []):
        if not isinstance(r, dict):
            continue
        out.append({
            "source": "firecrawl",
            "source_id": sha1_short(r.get("url") or str(r)),
            "url": r.get("url"),
            "download_url": None,  # not an image URL — needs scrape step
            "preview_url": None,
            "attribution": f"Source: {r.get('url')}",
            "license": "unknown",
            "license_url": None,
            "dimensions": None,
            "aspect_ratio": None,
            "tags": [],
            "description": r.get("title", "") + " — " + (r.get("description", "") or "")[:240],
            "warnings": ["license_unknown", "requires_scrape_for_image_urls"],
        })
    return out


# ========== scoring ==========

# Style modifiers that carry no subject signal — skip when extracting keywords.
_STYLE_STOPWORDS = {
    "minimal", "minimalist", "editorial", "grounded", "muted", "clean",
    "palette", "composition", "geometry", "geometric", "style", "mood",
    "moody", "light", "dark", "bright", "subtle", "bold", "quiet",
    "simple", "soft", "hard", "raw", "polished", "refined", "pure",
    "with", "from", "into", "onto", "that", "this", "these", "those",
    "some", "many", "more", "less", "none", "people", "person", "human",
}

# Strong negatives when brief says "no people" / avoid humans.
_PEOPLE_SIGNALS = {
    "person", "people", "human", "humans",
    "man", "men", "woman", "women", "boy", "girl", "guy", "lady",
    "child", "children", "kid", "kids", "baby",
    "team", "teams", "crew", "group", "couple", "crowd", "audience",
    "portrait", "portraits", "face", "faces", "smile", "smiling",
    "standing", "sitting", "walking", "wearing", "holding",
    "hand", "hands", "arm", "arms",
    "worker", "workers", "employee", "staff", "engineer", "engineers",
    "shirt", "suit", "dress", "jacket", "wears",
    "looking", "talking", "posing", "working",
    "customer", "customers", "user", "users",
}

# Generic office / corporate / SaaS-stock cliches — always demote.
_OFFICE_CLICHE_SIGNALS = {
    "chair", "chairs", "desk", "desks", "laptop", "laptops",
    "computer", "computers", "office", "offices",
    "meeting", "meetings", "handshake", "handshakes",
    "keyboard", "mouse", "monitor", "screen", "display",
    "coffee", "latte", "notebook", "notepad", "pen", "pencil",
    "boardroom", "conference",
}


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"[a-z]+", (s or "").lower()))


# Composition signals — words that describe "how the photo is shot / framed".
# Boosted when brief.role is primary_anchor or background with aerial orientation.
_COMPOSITION_SIGNALS = {
    "aerial", "overhead", "top", "topdown", "rooftop", "drone",
    "wide", "landscape", "panoramic", "vast", "sprawling",
    "detail", "closeup", "close",
    "architecture", "architectural", "facade", "building", "buildings",
    "geometric", "geometry", "structure", "structural",
    "pattern", "texture", "surface",
}

# Lightweight synonym groups — if brief style mentions one, candidates matching
# any in the group get the subject boost too.
_SUBJECT_SYNONYMS = {
    "industrial": {"industrial", "industry", "factory", "factories",
                   "manufacturing", "plant", "plants", "warehouse",
                   "refinery", "machinery", "machines"},
    "urban": {"urban", "city", "cityscape", "downtown", "metropolis"},
    "nature": {"nature", "landscape", "forest", "mountain", "mountains",
               "river", "lake", "coast", "ocean", "desert"},
    "architectural": {"architectural", "architecture", "building",
                      "buildings", "structure", "facade"},
    "minimal": {"minimal", "minimalist", "sparse", "clean", "empty"},
    "editorial": {"editorial", "documentary", "journalistic"},
}


def _style_keywords(brief: dict) -> list[str]:
    """Subject-bearing words from brief.style only (not meta fields)."""
    style = brief.get("style") or ""
    tokens = _tokenize(style)
    return [t for t in tokens if len(t) >= 4 and t not in _STYLE_STOPWORDS]


def _expanded_subjects(style_keywords: list[str]) -> set[str]:
    """Expand style keywords via synonym groups."""
    expanded: set[str] = set()
    for kw in style_keywords:
        expanded.add(kw)
        for group in _SUBJECT_SYNONYMS.values():
            if kw in group:
                expanded.update(group)
    return expanded


def extract_subject_keywords(brief: dict) -> list[str]:
    """Public: returns the expanded subject set as a sorted list (for logs)."""
    kws = _style_keywords(brief)
    return sorted(_expanded_subjects(kws))


def _brief_forbids_people(brief: dict) -> bool:
    style = (brief.get("style") or "").lower()
    if "no people" in style or "no person" in style:
        return True
    for a in brief.get("avoid") or []:
        al = a.lower()
        if "people" in al or "person" in al or "human" in al or "face" in al or "team" in al:
            return True
    return False


def score_candidate(candidate: dict, brief: dict) -> tuple[float, str]:
    """Returns (fit_score 0..1, reason). v0.2 heuristic."""
    desc = candidate.get("description") or ""
    tags_raw = " ".join(candidate.get("tags") or [])
    blob = _tokenize(desc + " " + tags_raw)

    score = 0.5
    reasons: list[str] = []

    # 1. Subject keyword match (with synonym expansion) — strongest positive.
    subjects = _expanded_subjects(_style_keywords(brief))
    subject_hits = subjects & blob
    if subject_hits:
        score += 0.10 * min(len(subject_hits), 4)  # cap at +0.40
        reasons.append(f"+subject({','.join(sorted(subject_hits)[:3])})")

    # 2. Composition signal match — aerial/overhead/architecture etc.
    #    Boost applies whenever these hit; the query generator typically
    #    steers retrieval here already, so matches should be common.
    comp_hits = _COMPOSITION_SIGNALS & blob
    if comp_hits:
        score += 0.06 * min(len(comp_hits), 3)  # cap at +0.18
        reasons.append(f"+comp({','.join(sorted(comp_hits)[:2])})")

    # 3. Mood phrases — rare match on literal captions, small bonus when it hits.
    for m in brief.get("mood") or []:
        if m.lower() in desc.lower():
            score += 0.04
            reasons.append(f"+mood:{m}")

    # 3. Explicit brief.avoid — match any substantive word.
    for a in brief.get("avoid") or []:
        avoid_words = {w for w in re.findall(r"[a-z]+", a.lower()) if len(w) > 3}
        hit = avoid_words & blob
        if hit:
            score -= 0.25
            reasons.append(f"-avoid:{sorted(hit)[0]}")

    # 4. Hardcoded "no people" filter when brief forbids them.
    if _brief_forbids_people(brief):
        people_hits = _PEOPLE_SIGNALS & blob
        if people_hits:
            score -= 0.40
            reasons.append(f"-people:{sorted(people_hits)[0]}")

    # 5. Generic office cliche filter — always on for editorial briefs.
    office_hits = _OFFICE_CLICHE_SIGNALS & blob
    if office_hits:
        score -= 0.25
        reasons.append(f"-office:{sorted(office_hits)[0]}")

    # 6. Orientation check.
    dims = candidate.get("dimensions")
    if dims and dims[0] and dims[1]:
        w, h = dims[0], dims[1]
        orient = brief.get("orientation")
        if orient == "landscape":
            if w >= h:
                score += 0.05
                reasons.append("+orient")
            else:
                score -= 0.15
                reasons.append("-orient_mismatch")
        elif orient == "portrait":
            if h > w:
                score += 0.05
                reasons.append("+orient")
            else:
                score -= 0.15
                reasons.append("-orient_mismatch")

    # 7. Clean-license bonus (small).
    if candidate.get("source") == "unsplash":
        score += 0.03
        reasons.append("+license")

    # 8. Warnings penalty (e.g. Firecrawl's license_unknown).
    if candidate.get("warnings"):
        score -= 0.12 * len(candidate["warnings"])
        reasons.append(f"-warn({len(candidate['warnings'])})")

    score = max(0.0, min(1.0, score))
    return score, ", ".join(reasons) if reasons else "neutral"


def dedup_candidates(candidates: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for c in candidates:
        key = (c.get("source"), c.get("source_id"))
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


# ========== main ==========

def run(project: str, section: str) -> int:
    env = load_env(ENV_FILE)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    briefs_dir = PROJECT_ROOT / "assets" / project / "briefs"
    brief_path = briefs_dir / f"{section}.json"
    if not brief_path.exists():
        print(f"ERROR: brief not found: {brief_path}", file=sys.stderr)
        return 2

    brief = json.loads(brief_path.read_text())
    if not brief.get("need_asset"):
        print(f"Brief {section} has need_asset=false; nothing to retrieve.")
        return 0

    print(f"=== Retrieving for {project}/{section} ===")
    print(f"style:  {brief.get('style')}")
    print(f"mood:   {brief.get('mood')}")
    print(f"variants target: {brief.get('variants', 5)}")
    print()

    queries = generate_queries(brief)
    print("Generated queries:")
    for q in queries:
        print(f"  - {q}")
    print()

    all_candidates: list[dict] = []
    sources = brief.get("sources") or []

    # per-source fan-out
    for source in sources:
        print(f"[{source}] searching…")
        if source == "unsplash":
            key = os.environ.get("UNSPLASH_ACCESS_KEY")
            if not key:
                print("  skipping: UNSPLASH_ACCESS_KEY not set")
                continue
            for q in queries:
                found = search_unsplash(key, q, per_page=6)
                for c in found:
                    c["query"] = q
                all_candidates.extend(found)
                print(f"  q={q!r} → {len(found)} results")
                time.sleep(0.4)  # gentle on rate limit
        elif source == "firecrawl":
            key = os.environ.get("FIRECRAWL_API_KEY")
            if not key:
                print("  skipping: FIRECRAWL_API_KEY not set")
                continue
            # Firecrawl search is slow; use fewer queries
            for q in queries[:2]:
                found = search_firecrawl(key, q, limit=3)
                for c in found:
                    c["query"] = q
                all_candidates.extend(found)
                print(f"  q={q!r} → {len(found)} results")
                time.sleep(0.6)
        elif source == "pexels":
            print("  skipping: pexels adapter not implemented in v0.1")
        else:
            print(f"  skipping: adapter '{source}' not implemented in v0.1")

    print()
    print(f"Total candidates before dedup: {len(all_candidates)}")
    all_candidates = dedup_candidates(all_candidates)
    print(f"After dedup: {len(all_candidates)}")
    print()

    # Score
    for c in all_candidates:
        c["fit_score"], c["reason"] = score_candidate(c, brief)
    all_candidates.sort(key=lambda x: x["fit_score"], reverse=True)

    target = brief.get("variants", 5)
    keep = min(len(all_candidates), target * 2)
    shortlist = all_candidates[:keep]

    print(f"Shortlist (top {keep}):")
    for i, c in enumerate(shortlist, 1):
        print(f"  {i:>2}. [{c['source']}] {c['fit_score']:.2f}  {c.get('description', '')[:70]}")
        print(f"       {c.get('reason', '')}")
    print()

    # Download (skip firecrawl since it doesn't have direct image URLs in this path)
    candidates_dir = PROJECT_ROOT / "assets" / project / "candidates" / section
    candidates_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading shortlist to", candidates_dir.relative_to(PROJECT_ROOT))
    for i, c in enumerate(shortlist, 1):
        if not c.get("download_url"):
            print(f"  {i:>2}. [{c['source']}] skip — no direct image URL")
            continue
        ext = ".jpg"
        if c["source"] == "unsplash":
            ext = ".jpg"
        filename = f"{i:02d}-{c['source']}-{c['source_id']}{ext}"
        dest = candidates_dir / filename
        ok = download(c["download_url"], dest)
        c["file"] = filename if ok else None
        print(f"  {i:>2}. [{c['source']}] {'ok' if ok else 'FAIL'}  →  {filename}")

    print()

    # Write metadata
    metadata_dir = PROJECT_ROOT / "assets" / project / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_dir / f"{section}.json"
    metadata = {
        "section": section,
        "brief_path": str(brief_path.relative_to(PROJECT_ROOT)),
        "fetched_at": now_iso(),
        "queries": queries,
        "sources_used": [s for s in sources if s in {"unsplash", "firecrawl"}],
        "total_found": len(all_candidates),
        "candidates": shortlist,
        "approval": {
            "status": "candidates_ready",
            "approved": [],
            "rejected": [],
            "decided_at": None,
            "by": None,
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))
    print(f"Metadata written: {metadata_path.relative_to(PROJECT_ROOT)}")
    print()
    print("Done. Next step: review candidates (Figma review frame or in-chat pick).")
    return 0


def rescore(project: str, section: str) -> int:
    """Re-score candidates in an existing metadata file without calling any API."""
    briefs_dir = PROJECT_ROOT / "assets" / project / "briefs"
    metadata_dir = PROJECT_ROOT / "assets" / project / "metadata"
    brief_path = briefs_dir / f"{section}.json"
    metadata_path = metadata_dir / f"{section}.json"

    if not brief_path.exists():
        print(f"ERROR: brief not found: {brief_path}", file=sys.stderr)
        return 2
    if not metadata_path.exists():
        print(f"ERROR: no existing metadata at {metadata_path}", file=sys.stderr)
        return 2

    brief = json.loads(brief_path.read_text())
    meta = json.loads(metadata_path.read_text())
    candidates = meta.get("candidates") or []

    if not candidates:
        print("No candidates in metadata to re-score.", file=sys.stderr)
        return 1

    print(f"=== Re-scoring {len(candidates)} candidates for {project}/{section} ===")
    print(f"Subject keywords from brief: {extract_subject_keywords(brief)}")
    print(f"People filter active: {_brief_forbids_people(brief)}")
    print()

    changed = 0
    for c in candidates:
        old_score = c.get("fit_score")
        new_score, new_reason = score_candidate(c, brief)
        c["fit_score"] = new_score
        c["reason"] = new_reason
        if old_score != new_score:
            changed += 1

    # Re-rank
    candidates.sort(key=lambda x: x["fit_score"], reverse=True)
    meta["candidates"] = candidates
    meta["rescored_at"] = now_iso()

    metadata_path.write_text(json.dumps(meta, indent=2))

    print(f"Re-scored {len(candidates)} candidates ({changed} changed).")
    print()
    print("New ranking (top 15):")
    for i, c in enumerate(candidates[:15], 1):
        desc = (c.get("description") or "")[:70]
        print(f"  {i:>2}. [{c['source']}] {c['fit_score']:.2f}  {desc}")
        print(f"       {c.get('reason', '')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="project id (matches assets/<project>/)")
    ap.add_argument("--section", required=True, help="section id (matches briefs/<section>.json)")
    ap.add_argument("--rescore", action="store_true",
                    help="Re-score existing candidates in metadata without any API calls.")
    args = ap.parse_args()
    if args.rescore:
        return rescore(args.project, args.section)
    return run(args.project, args.section)


if __name__ == "__main__":
    sys.exit(main())
