#!/usr/bin/env python3
"""
Unsplash /search/photos smoke test.

Usage:
    python3 scripts/unsplash_smoke_test.py [query]

Default query: "industrial factory aerial"
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


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


def unsplash_search(access_key: str, query: str, per_page: int = 10) -> dict:
    base = "https://api.unsplash.com/search/photos"
    qs = urllib.parse.urlencode({
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
    })
    req = urllib.request.Request(
        f"{base}?{qs}",
        headers={
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {access_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "body": json.loads(body),
                "rate_remaining": resp.headers.get("X-Ratelimit-Remaining"),
                "rate_limit": resp.headers.get("X-Ratelimit-Limit"),
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": e.reason,
            "body": e.read().decode("utf-8", errors="replace"),
        }
    except urllib.error.URLError as e:
        return {"status": 0, "error": str(e.reason), "body": None}


def main() -> int:
    env = load_env(ENV_FILE)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        print("ERROR: UNSPLASH_ACCESS_KEY not set.", file=sys.stderr)
        return 2

    query = " ".join(sys.argv[1:]) or "industrial factory aerial"
    print(f"Query: {query!r}")
    print(f"Auth:  key starts with {key[:6]}…, length {len(key)}")
    print("Calling Unsplash /search/photos …")

    result = unsplash_search(key, query, per_page=10)
    status = result.get("status")
    body = result.get("body")

    print(f"HTTP {status}")
    rl_rem = result.get("rate_remaining")
    rl_lim = result.get("rate_limit")
    if rl_rem or rl_lim:
        print(f"Rate limit: {rl_rem}/{rl_lim} remaining this hour")

    if status != 200:
        print("Error response:")
        print(result.get("error"))
        if body:
            if isinstance(body, str):
                print(body[:2000])
            else:
                print(json.dumps(body, indent=2)[:2000])
        return 1

    if not isinstance(body, dict):
        print("Unexpected body type:", type(body).__name__)
        return 1

    total = body.get("total", 0)
    total_pages = body.get("total_pages", 0)
    results = body.get("results") or []
    print(f"total results (across all pages): {total}")
    print(f"total pages: {total_pages}")
    print(f"returned this page: {len(results)}")
    print("---")
    for i, photo in enumerate(results, 1):
        desc = (
            photo.get("alt_description")
            or photo.get("description")
            or "(no description)"
        )
        user = photo.get("user", {})
        user_name = user.get("name") or "(unknown)"
        w, h = photo.get("width"), photo.get("height")
        likes = photo.get("likes", 0)
        print(f"{i:>2}. {desc[:90]}")
        print(f"    {photo['urls']['regular']}")
        print(f"    {w}x{h}  by {user_name}  ♥ {likes}")
        print()

    dump_dir = PROJECT_ROOT / "assets" / "symnera-website" / "metadata" / "_cache" / "unsplash"
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump_path = dump_dir / "smoke-test-response.json"
    dump_path.write_text(json.dumps(body, indent=2))
    print(f"Full response saved to: {dump_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
