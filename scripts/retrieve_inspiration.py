#!/usr/bin/env python3
"""
Inspiration capture pipeline (v0.2 — capture-only).

Loads a brand brief, generates queries, asks Firecrawl to search designer sites,
filters out listing/gallery/search URLs with per-source regex, scrapes the rest
with a full-page screenshot, and saves the raw capture.

DOES NOT score for design signal — that is scripts/extract_pattern_signals.py's
job against the rendered pixels. This script only decides which URLs are worth
scraping (URL-pattern filter + source authority) and writes the raw bytes.

Output layout:
    inspiration/<project>/raw/<candidate-id>/
        screenshot.png     # full-page screenshot
        page.md            # Firecrawl markdown
        preview.jpg        # og:image fallback
        metadata.json      # url, source, title, discovery_filter trace

Usage:
    python3 scripts/retrieve_inspiration.py --project symnera-website
    python3 scripts/retrieve_inspiration.py --project symnera-website --dry-run
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


# ========== source config ==========

SOURCE_DOMAINS = {
    "awwwards": "awwwards.com",
    "siteinspire": "siteinspire.com",
    "land-book": "land-book.com",
    "godly": "godly.website",
    "httpster": "httpster.net",
    "dribbble": "dribbble.com",
    "behance": "behance.net",
    "mobbin": "mobbin.com",
    "open_web": None,
}

SOURCE_AUTHORITY = {
    "awwwards": 1.00,
    "siteinspire": 0.95,
    "land-book": 0.90,
    "godly": 0.85,
    "mobbin": 0.80,
    "behance": 0.75,
    "httpster": 0.70,
    "dribbble": 0.65,
    "open_web": 0.50,
}

# Per-source URL filters. `prefer` = allowlist (URL must match at least one if
# any exist). `reject` = denylist (URL must not match any).
SOURCE_URL_FILTERS: dict[str, dict[str, list[re.Pattern[str]]]] = {
    "awwwards": {
        # individual showcase pages appear under /sites/<slug> or /inspiration/<slug>
        "prefer": [
            re.compile(r"awwwards\.com/sites/[^/?#]+/?$"),
            re.compile(r"awwwards\.com/inspiration/[^/?#]+/?$"),
        ],
        "reject": [
            re.compile(r"/websites/"), re.compile(r"/search"),
            re.compile(r"/blog"), re.compile(r"/jobs"), re.compile(r"/courses"),
            re.compile(r"/inspiration/?$"), re.compile(r"/inspiration_search/"),
            re.compile(r"/sotd"),
        ],
    },
    "siteinspire": {
        # individual showcase pages are /websites/<id> or /websites/<id>-<slug>
        "prefer": [re.compile(r"siteinspire\.com/websites/\d+")],
        "reject": [
            re.compile(r"siteinspire\.com/?$"),
            re.compile(r"/websites/?$"), re.compile(r"/websites/category"),
            re.compile(r"/page/"), re.compile(r"/categories"), re.compile(r"/styles"),
            re.compile(r"/profile/"),
        ],
    },
    "dribbble": {
        "prefer": [re.compile(r"dribbble\.com/shots/\d+")],
        "reject": [
            re.compile(r"/browse"), re.compile(r"/tags/"),
            re.compile(r"/search"), re.compile(r"/jobs"), re.compile(r"/goods"),
            re.compile(r"/designers"),
        ],
    },
    "behance": {
        "prefer": [re.compile(r"behance\.net/gallery/\d+")],
        "reject": [
            re.compile(r"/search"), re.compile(r"/galleries"),
            re.compile(r"/moodboards"), re.compile(r"/assets"),
        ],
    },
    "land-book": {
        # individual showcase URLs are top-level slugs like /acme-site-name
        "prefer": [re.compile(r"^https?://land-book\.com/[a-z0-9][a-z0-9-]{2,}/?$")],
        "reject": [
            re.compile(r"/tags/"), re.compile(r"/collections"),
            re.compile(r"/blog"), re.compile(r"/styles/"), re.compile(r"/pricing"),
            re.compile(r"/sign"), re.compile(r"/page/"),
        ],
    },
    "godly": {
        "prefer": [re.compile(r"godly\.website/inspiration/[a-z0-9-]+")],
        "reject": [
            re.compile(r"^https?://godly\.website/?$"),
            re.compile(r"/page/"), re.compile(r"/tag/"),
        ],
    },
    "httpster": {
        # httpster uses /website/<slug> for individual showcases
        "prefer": [re.compile(r"httpster\.net/website/[a-z0-9-]+")],
        "reject": [
            re.compile(r"^https?://(www\.)?httpster\.net/?$"),
            re.compile(r"/page/"), re.compile(r"/contact"),
            re.compile(r"/type/"), re.compile(r"/tag/"),
        ],
    },
    "mobbin": {
        "prefer": [re.compile(r"mobbin\.com/apps/[^/?#]+")],
        "reject": [
            re.compile(r"/search"), re.compile(r"/pricing"),
            re.compile(r"/categories/?$"), re.compile(r"/flows/?$"),
        ],
    },
    "open_web": {
        "prefer": [],
        "reject": [
            re.compile(r"/search"), re.compile(r"/tags/"),
            re.compile(r"\?page="), re.compile(r"/category/"),
        ],
    },
}


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


def slugify(s: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:max_len] or "item"


def http_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    payload: dict | None = None,
    timeout: int = 60,
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
        return 0, f"URLError: {e.reason}"


def http_download(url: str, dest: Path, timeout: int = 60) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ! download failed ({url[:70]}…): {e}", file=sys.stderr)
        return False


# ========== Firecrawl adapters ==========

def firecrawl_search(api_key: str, query: str, limit: int = 10) -> list[dict]:
    status, body = http_json(
        "https://api.firecrawl.dev/v1/search",
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"},
        payload={"query": query, "limit": limit},
    )
    if status != 200 or not isinstance(body, dict):
        print(f"  ! search failed [{status}] {str(body)[:200]}", file=sys.stderr)
        return []
    return body.get("data") or []


def firecrawl_scrape(api_key: str, url: str) -> dict | None:
    status, body = http_json(
        "https://api.firecrawl.dev/v1/scrape",
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"},
        payload={
            "url": url,
            "formats": ["markdown", "screenshot@fullPage"],
            "onlyMainContent": False,
            "waitFor": 1500,
        },
        timeout=120,
    )
    if status != 200 or not isinstance(body, dict):
        print(f"  ! scrape failed [{status}] {url[:70]}…", file=sys.stderr)
        return None
    return body.get("data") or None


# ========== URL filter ==========

def url_filter_decision(source: str, url: str) -> tuple[bool, str]:
    """
    Decide whether a discovered URL is worth scraping.

    Returns (accept, reason). `reason` is a short tag used for telemetry.
    """
    cfg = SOURCE_URL_FILTERS.get(source, SOURCE_URL_FILTERS["open_web"])

    for pat in cfg["reject"]:
        if pat.search(url):
            return False, f"rejected:{pat.pattern}"

    prefer = cfg.get("prefer", [])
    if prefer:
        if not any(p.search(url) for p in prefer):
            return False, "not_in_prefer_patterns"

    return True, "accepted"


# ========== query generation ==========

def build_queries(brief: dict) -> list[tuple[str, str]]:
    """Return list of (source, query) tuples biased toward individual showcase URLs."""
    aesthetic = brief.get("aesthetic", [])[:3]
    patterns = brief.get("patterns_wanted", [])[:3]
    aesthetic_str = " ".join(aesthetic) if aesthetic else ""
    top_pattern = patterns[0] if patterns else ""

    queries: list[tuple[str, str]] = []
    for source in brief.get("sources", []):
        domain = SOURCE_DOMAINS.get(source)
        suffix = f" site:{domain}" if domain else ""

        if source == "awwwards":
            # site-of-the-day pages sit under /sites/<slug>
            queries.append((source, f"{aesthetic_str} site of the day{suffix}"))
            queries.append((source, f"{aesthetic_str} {top_pattern} website{suffix}"))
        elif source == "siteinspire":
            queries.append((source, f"{aesthetic_str} website{suffix}"))
            queries.append((source, f"{aesthetic_str} {top_pattern}{suffix}"))
        elif source == "dribbble":
            queries.append((source, f"{aesthetic_str} landing page shot{suffix}"))
            queries.append((source, f"{aesthetic_str} {top_pattern} ui{suffix}"))
        elif source == "behance":
            queries.append((source, f"{aesthetic_str} web design project{suffix}"))
        elif source == "land-book":
            queries.append((source, f"{aesthetic_str} landing page{suffix}"))
            queries.append((source, f"{aesthetic_str} {top_pattern}{suffix}"))
        elif source == "godly":
            queries.append((source, f"{aesthetic_str} inspiration{suffix}"))
        elif source == "httpster":
            queries.append((source, f"{aesthetic_str} website{suffix}"))
        elif source == "mobbin":
            queries.append((source, f"{aesthetic_str} app{suffix}"))
        else:
            if aesthetic_str:
                queries.append((source, f"{aesthetic_str}{suffix}"))

    # dedupe preserving order
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for s, q in queries:
        key = (s, q.strip())
        if key in seen or not q.strip():
            continue
        seen.add(key)
        out.append((s, q.strip()))
    return out


# ========== main pipeline ==========

def parse_only_queries(raw: str) -> list[tuple[str, str]]:
    """
    Parse --only-queries raw string into (source, query) tuples.

    Format: pipe-separated entries. Each entry is "<source>:<query>" or plain
    "<query>" (source inferred from site:<domain> in the query, else 'open_web').
    """
    out: list[tuple[str, str]] = []
    for entry in raw.split("|"):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry and entry.split(":", 1)[0] in SOURCE_DOMAINS:
            source, query = entry.split(":", 1)
            out.append((source.strip(), query.strip()))
            continue
        # infer source from site: operator
        source = "open_web"
        m = re.search(r"site:([a-z0-9.\-]+)", entry)
        if m:
            for src, dom in SOURCE_DOMAINS.items():
                if dom and dom in m.group(1):
                    source = src
                    break
        out.append((source, entry))
    return out


def run(project: str, dry_run: bool, limit_per_source: int | None,
        only_queries: list[tuple[str, str]] | None = None) -> int:
    env = load_env(ENV_FILE)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
    if not firecrawl_key and not dry_run:
        print("ERROR: FIRECRAWL_API_KEY not set in .env", file=sys.stderr)
        return 2

    proj_dir = PROJECT_ROOT / "inspiration" / project
    brief_path = proj_dir / "briefs" / "brand.json"
    if not brief_path.exists():
        print(f"ERROR: brief not found at {brief_path}", file=sys.stderr)
        return 2
    brief = json.loads(brief_path.read_text())

    raw_dir = proj_dir / "raw"
    meta_dir = proj_dir / "metadata"
    raw_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    queries = only_queries if only_queries else build_queries(brief)
    if only_queries:
        print(f"Using {len(queries)} targeted queries (brief-derived queries skipped)")
    else:
        print(f"Generated {len(queries)} queries across {len({s for s,_ in queries})} sources")
    for s, q in queries:
        print(f"  [{s}] {q}")

    if dry_run:
        print("\nDry run — skipping search + scrape.")
        return 0

    per_source_limit = limit_per_source or brief.get("max_candidates_per_source", 5)

    # --- discovery ---
    urls_by_source: dict[str, list[tuple[str, dict]]] = {}
    for source, query in queries:
        print(f"\n→ searching: [{source}] {query}")
        results = firecrawl_search(firecrawl_key, query, limit=per_source_limit * 3)
        print(f"  got {len(results)} raw results")
        bucket = urls_by_source.setdefault(source, [])
        seen_urls = {u for u, _ in bucket}
        for r in results:
            u = r.get("url")
            if not u or u in seen_urls:
                continue
            bucket.append((u, r))
            seen_urls.add(u)
        time.sleep(1.0)

    # --- URL-pattern filter + scrape ---
    written = 0
    filter_summary: dict[str, int] = {}
    errors: list[dict] = []
    aggregate = {
        "generated_at": now_iso(),
        "brief": brief,
        "candidates": [],
        "discovery": {"total_raw": 0, "accepted": 0, "rejected": 0},
    }

    for source, pairs in urls_by_source.items():
        kept = 0
        for url, search_item in pairs:
            if kept >= per_source_limit:
                break

            aggregate["discovery"]["total_raw"] += 1
            accept, reason = url_filter_decision(source, url)
            filter_summary[reason] = filter_summary.get(reason, 0) + 1
            if not accept:
                print(f"  · filter[{source}] {reason}: {url[:80]}")
                aggregate["discovery"]["rejected"] += 1
                continue
            aggregate["discovery"]["accepted"] += 1

            slug = slugify(search_item.get("title") or urllib.parse.urlparse(url).path)
            h = sha1_short(url)
            folder = raw_dir / f"{source}-{slug}-{h}"
            if folder.exists() and (folder / "metadata.json").exists():
                print(f"  · skip (exists): {folder.name}")
                kept += 1
                continue

            print(f"\n→ scrape: [{source}] {url[:90]}")
            data = firecrawl_scrape(firecrawl_key, url)
            if not data:
                errors.append({"url": url, "source": source, "reason": "scrape failed"})
                continue

            md = data.get("markdown") or ""
            screenshot_url = data.get("screenshot") or data.get("fullPageScreenshot")
            fc_meta = data.get("metadata") or {}
            title = fc_meta.get("title") or search_item.get("title") or ""
            description = fc_meta.get("description") or search_item.get("description") or ""
            og_image = fc_meta.get("ogImage") or fc_meta.get("og:image")

            folder.mkdir(parents=True, exist_ok=True)
            (folder / "page.md").write_text(md[:200_000])

            shot_ok = False
            if screenshot_url:
                shot_ok = http_download(screenshot_url, folder / "screenshot.png")
            prev_ok = False
            if og_image:
                prev_ok = http_download(og_image, folder / "preview.jpg")

            m = {
                "id": f"{source}-{h}",
                "source": source,
                "url": url,
                "title": title,
                "description": description,
                "author": fc_meta.get("author") or None,
                "tags": fc_meta.get("keywords") or [],
                "og_image": og_image,
                "screenshot_saved": shot_ok,
                "preview_saved": prev_ok,
                "retrieved_at": now_iso(),
                "discovery_filter": {
                    "source_authority": SOURCE_AUTHORITY.get(source, 0.5),
                    "url_accept_reason": reason,
                },
            }
            (folder / "metadata.json").write_text(json.dumps(m, indent=2))
            aggregate["candidates"].append(m)
            print(f"  ✓ saved {folder.name}  shot={'y' if shot_ok else 'n'}")
            written += 1
            kept += 1
            time.sleep(1.0)

    aggregate["errors"] = errors
    aggregate["discovery"]["filter_summary"] = filter_summary
    (meta_dir / "inspiration.json").write_text(json.dumps(aggregate, indent=2))

    print(f"\nDone. {written} raw captures saved under {raw_dir.relative_to(PROJECT_ROOT)}.")
    print(f"Discovery: {aggregate['discovery']['accepted']} accepted / "
          f"{aggregate['discovery']['rejected']} rejected "
          f"from {aggregate['discovery']['total_raw']} raw results.")
    if filter_summary:
        print("Filter reasons:")
        for k, v in sorted(filter_summary.items(), key=lambda kv: -kv[1]):
            print(f"  {v:>3}  {k}")
    if errors:
        print(f"{len(errors)} scrape errors — see metadata/inspiration.json.")
    print("\nNext: run scripts/extract_pattern_signals.py to segment + grade.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--dry-run", action="store_true", help="Generate queries only; no API calls")
    p.add_argument("--per-source-limit", type=int, default=None,
                   help="Max accepted URLs to scrape per source (overrides brief).")
    p.add_argument("--only-queries", type=str, default=None,
                   help="Pipe-separated list of targeted queries to use instead of "
                        "brief-derived ones. Each entry: '<source>:<query>' or just "
                        "'<query with site:domain>'. Useful for 'more like X' runs.")
    args = p.parse_args()
    only = parse_only_queries(args.only_queries) if args.only_queries else None
    return run(args.project, args.dry_run, args.per_source_limit, only)


if __name__ == "__main__":
    sys.exit(main())
