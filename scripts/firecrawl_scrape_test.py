#!/usr/bin/env python3
"""
Firecrawl /v1/scrape test — pulls a URL and extracts image references.

Usage:
    python3 scripts/firecrawl_scrape_test.py [url]

Default URL: first result from the earlier smoke test (iStock landing).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_URL = "https://www.istockphoto.com/photos/factory-aerial-view"


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


def firecrawl_scrape(api_key: str, url: str) -> dict:
    endpoint = "https://api.firecrawl.dev/v1/scrape"
    payload = json.dumps({
        "url": url,
        "formats": ["markdown", "links"],
        "onlyMainContent": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
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


IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMG_HTML_RE = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>', re.IGNORECASE)


def extract_images(body: dict) -> list[dict]:
    """Return a list of {url, alt, source_format} dicts."""
    images: list[dict] = []
    data = body.get("data") or {}
    md = data.get("markdown") or ""
    html = data.get("html") or ""
    links = data.get("links") or []

    for alt, url in IMG_MD_RE.findall(md):
        images.append({"url": url, "alt": alt, "source_format": "markdown"})

    for url in IMG_HTML_RE.findall(html):
        images.append({"url": url, "alt": None, "source_format": "html"})

    for link in links:
        if isinstance(link, str) and re.search(r"\.(jpg|jpeg|png|webp|gif|svg)(\?|$)", link, re.IGNORECASE):
            images.append({"url": link, "alt": None, "source_format": "links"})

    # Dedup by URL, preserving order
    seen = set()
    unique = []
    for img in images:
        u = img["url"]
        if u in seen:
            continue
        seen.add(u)
        unique.append(img)
    return unique


def main() -> int:
    env = load_env(ENV_FILE)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY not set.", file=sys.stderr)
        return 2

    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Target URL: {url}")
    print("Calling Firecrawl /v1/scrape …")

    result = firecrawl_scrape(api_key, url)
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

    if not isinstance(body, dict):
        print("Unexpected body type:", type(body).__name__)
        return 1

    data = body.get("data") or {}
    md_len = len(data.get("markdown") or "")
    html_len = len(data.get("html") or "")
    link_count = len(data.get("links") or [])
    meta = data.get("metadata") or {}

    print(f"success: {body.get('success')}")
    print(f"markdown chars: {md_len}")
    print(f"html chars:     {html_len}")
    print(f"links count:    {link_count}")
    print(f"title:          {meta.get('title', '(none)')}")
    print(f"description:    {(meta.get('description') or '')[:160]}")
    print()

    images = extract_images(body)
    print(f"Extracted {len(images)} unique image URL(s)")
    print("---")
    for i, img in enumerate(images[:20], 1):
        alt = img.get("alt") or ""
        print(f"{i:>2}. [{img['source_format']}] {img['url']}")
        if alt:
            print(f"    alt: {alt[:140]}")

    if len(images) > 20:
        print(f"… plus {len(images) - 20} more")

    dump_dir = PROJECT_ROOT / "assets" / "symnera-website" / "metadata" / "_cache" / "firecrawl"
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump_path = dump_dir / "scrape-test-response.json"
    dump_path.write_text(json.dumps(body, indent=2))
    print(f"\nFull response saved to: {dump_path.relative_to(PROJECT_ROOT)}")

    images_path = dump_dir / "scrape-test-images.json"
    images_path.write_text(json.dumps(images, indent=2))
    print(f"Extracted images JSON:  {images_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
