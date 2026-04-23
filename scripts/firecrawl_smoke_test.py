#!/usr/bin/env python3
"""
Smoke test for Firecrawl retrieval.

Hits /v1/search with a hardcoded query. No dependencies beyond stdlib.
Loads FIRECRAWL_API_KEY from .env at the project root.

Usage:
    python3 scripts/firecrawl_smoke_test.py [query]

Default query: "industrial factory aerial minimal"
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env(path: Path) -> dict[str, str]:
    """Minimal .env parser — KEY=value lines, no quotes/export keyword."""
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


def firecrawl_search(api_key: str, query: str, limit: int = 10) -> dict:
    url = "https://api.firecrawl.dev/v1/search"
    payload = json.dumps({"query": query, "limit": limit}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return {"status": resp.status, "body": json.loads(body)}
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

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not set (checked .env and environment).", file=sys.stderr)
        return 2

    query = " ".join(sys.argv[1:]) or "industrial factory aerial minimal"
    print(f"Query: {query!r}")
    print(f"Auth:  key starts with {api_key[:6]}…, length {len(api_key)}")
    print("Calling Firecrawl /v1/search …")

    result = firecrawl_search(api_key, query, limit=5)
    status = result.get("status")
    body = result.get("body")

    print(f"HTTP {status}")

    if status != 200:
        print("Error response:")
        print(result.get("error"))
        if body:
            if isinstance(body, str):
                print(body[:2000])
            else:
                print(json.dumps(body, indent=2)[:2000])
        return 1

    # Success — summarize the result structure
    if isinstance(body, dict):
        success = body.get("success")
        data = body.get("data") or body.get("results") or []
        print(f"success: {success}")
        print(f"returned {len(data)} item(s)")
        print("---")
        for i, item in enumerate(data[:5], 1):
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("metadata", {}).get("title") or "(no title)"
            url = item.get("url") or item.get("link") or "(no url)"
            desc = (
                item.get("description")
                or item.get("snippet")
                or item.get("metadata", {}).get("description")
                or ""
            )
            print(f"{i:>2}. {title}")
            print(f"    {url}")
            if desc:
                print(f"    {desc[:180]}")
            print()
    else:
        print("Unexpected response shape; raw body:")
        print(json.dumps(body, indent=2)[:2000])

    # Also dump the full response for inspection
    dump_dir = PROJECT_ROOT / "assets" / "symnera-website" / "metadata" / "_cache" / "firecrawl"
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump_path = dump_dir / "smoke-test-response.json"
    dump_path.write_text(json.dumps(body, indent=2))
    print(f"Full response saved to: {dump_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
