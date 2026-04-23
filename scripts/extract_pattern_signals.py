#!/usr/bin/env python3
"""
Extract structured design patterns from raw inspiration screenshots.

Pipeline:
    1. Walk inspiration/<project>/ for screenshot.png files
    2. Segment each screenshot into horizontal regions (whitespace-aware)
    3. Score each region with pixel heuristics (fast, free)
    4. Shortlist regions with heuristic score >= HEURISTIC_GATE
    5. Optionally grade shortlisted regions with a Claude vision call
    6. Promote regions with combined score >= PROMOTE_GATE to pattern-library/candidates/

Raw screenshots are never treated as patterns — only extracted regions are.

Usage:
    # heuristic pre-filter only (fast, free)
    python3 scripts/extract_pattern_signals.py --project symnera-website

    # heuristic + vision grading (needs ANTHROPIC_API_KEY in .env)
    python3 scripts/extract_pattern_signals.py --project symnera-website --vision

    # smoke-test against existing (noisy) corpus — DOES NOT treat output as quality
    python3 scripts/extract_pattern_signals.py --project symnera-website --input-dir candidates --smoke-test
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageFilter, ImageStat

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# ---- thresholds (tuned for 1440–1920px wide full-page screenshots) ----
MIN_REGION_HEIGHT = 260
NAV_MAX_HEIGHT = 120
FOOTER_MIN_Y_RATIO = 0.85
WHITESPACE_GUTTER_MIN_ROWS = 18
WHITESPACE_VAR_THRESHOLD = 8.0   # grayscale variance per row below this = "gutter"

HEURISTIC_GATE = 0.45             # advance to vision stage
PROMOTE_GATE = 0.70               # promote to pattern-library/candidates/

ANTHROPIC_VISION_MODEL = "claude-sonnet-4-6"
OPENAI_VISION_MODEL = "gpt-4o"
VISION_MAX_IMAGE_DIM = 1568       # Anthropic recommendation — works fine for OpenAI too


# ========== data classes ==========

@dataclass
class Region:
    name: str
    x: int
    y: int
    w: int
    h: int
    image: Image.Image = field(repr=False)

    @property
    def bbox(self) -> list[int]:
        return [self.x, self.y, self.w, self.h]


@dataclass
class HeuristicFeatures:
    contrast_ratio: float
    edge_density: float
    color_variance: float
    whitespace_ratio: float
    content_density: float
    aspect: float
    tension: float
    focal_point: float
    palette_top: list[str]
    low_signal_flags: list[str]


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


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*[int(max(0, min(255, c))) for c in rgb])


# ========== segmentation ==========

def find_gutters(gray: np.ndarray) -> list[tuple[int, int]]:
    """
    Find runs of near-empty rows (variance below threshold).
    Returns list of (start_y, end_y) gutter spans.
    """
    row_var = gray.var(axis=1)
    is_gutter = row_var < WHITESPACE_VAR_THRESHOLD
    gutters: list[tuple[int, int]] = []
    start = None
    for y, g in enumerate(is_gutter):
        if g and start is None:
            start = y
        elif not g and start is not None:
            if y - start >= WHITESPACE_GUTTER_MIN_ROWS:
                gutters.append((start, y))
            start = None
    if start is not None and len(is_gutter) - start >= WHITESPACE_GUTTER_MIN_ROWS:
        gutters.append((start, len(is_gutter)))
    return gutters


def segment_image(im: Image.Image) -> list[Region]:
    """Whitespace-aware horizontal segmentation."""
    gray = np.asarray(im.convert("L"))
    H, W = gray.shape

    gutters = find_gutters(gray)

    # Build region bands from gutter midpoints
    cut_ys = [0]
    for g_start, g_end in gutters:
        cut_ys.append((g_start + g_end) // 2)
    cut_ys.append(H)
    cut_ys = sorted(set(cut_ys))

    # First pass: collect all bands that pass minimum height
    raw: list[tuple[int, int, int, Image.Image]] = []
    for i in range(len(cut_ys) - 1):
        y0, y1 = cut_ys[i], cut_ys[i + 1]
        h = y1 - y0
        if h < MIN_REGION_HEIGHT:
            # keep nav-sized top strip even if below MIN_REGION_HEIGHT so it can be filtered as nav
            if i == 0 and NAV_MAX_HEIGHT >= h >= 30:
                raw.append((y0, y1, h, im.crop((0, y0, W, y1))))
            continue
        raw.append((y0, y1, h, im.crop((0, y0, W, y1))))

    # Second pass: label by position within the kept set
    regions: list[Region] = []
    last_idx = len(raw) - 1
    for idx, (y0, y1, h, crop) in enumerate(raw):
        if idx == 0 and h <= NAV_MAX_HEIGHT:
            name = "nav"
        elif idx == 0 or (idx == 1 and regions and regions[-1].name == "nav"):
            name = "hero"
        elif idx == last_idx and y1 / H >= FOOTER_MIN_Y_RATIO:
            name = "footer"
        else:
            name = "band"
        regions.append(Region(name=name, x=0, y=y0, w=W, h=h, image=crop))

    return regions


# ========== heuristic features ==========

def compute_features(region: Region) -> HeuristicFeatures:
    im = region.image
    rgb = np.asarray(im.convert("RGB"))
    gray = np.asarray(im.convert("L"))
    H, W = gray.shape

    # edge density — PIL FIND_EDGES → grayscale pixel count above threshold
    edges = np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES))
    edge_density = float((edges > 24).sum()) / max(edges.size, 1)

    # color variance — std across RGB channels, averaged
    color_variance = float(rgb.reshape(-1, 3).std(axis=0).mean())

    # contrast ratio — luminance p95 / max(p05, 1)
    lum = gray.astype(np.float32)
    p05, p95 = np.percentile(lum, 5), np.percentile(lum, 95)
    contrast_ratio = float(p95 / max(p05, 1.0))

    # whitespace ratio — fraction of pixels within 3% of dominant background
    bg_rgb = _dominant_color(rgb)
    diff = np.abs(rgb.astype(np.int16) - np.array(bg_rgb, dtype=np.int16))
    whitespace_mask = (diff.max(axis=2) < 8)
    whitespace_ratio = float(whitespace_mask.mean())
    content_density = 1.0 - whitespace_ratio

    aspect = W / max(H, 1)

    # tension — std of edge density across 2x2 quadrants (higher = more varied)
    qh, qw = H // 2, W // 2
    quads = [
        edges[:qh, :qw], edges[:qh, qw:],
        edges[qh:, :qw], edges[qh:, qw:],
    ]
    quad_edge = [float((q > 24).mean()) for q in quads]
    tension = float(np.std(quad_edge))
    focal_point = float(max(quad_edge) / max(np.mean(quad_edge), 1e-6))

    # palette — 5 dominant colors (quantize to 16 levels)
    palette = _top_palette(rgb, k=5)

    # low-signal flags
    flags: list[str] = []
    if aspect > 8 and region.y == 0 and H <= NAV_MAX_HEIGHT:
        flags.append("nav_like")
    if region.name == "footer" or (aspect > 6 and H < 280):
        flags.append("footer_like")
    if content_density < 0.08:
        flags.append("near_empty")
    if _looks_uniform_grid(edges):
        flags.append("uniform_grid")
    if H < MIN_REGION_HEIGHT:
        flags.append("too_short")

    return HeuristicFeatures(
        contrast_ratio=round(contrast_ratio, 3),
        edge_density=round(edge_density, 4),
        color_variance=round(color_variance, 2),
        whitespace_ratio=round(whitespace_ratio, 3),
        content_density=round(content_density, 3),
        aspect=round(aspect, 3),
        tension=round(tension, 4),
        focal_point=round(focal_point, 3),
        palette_top=[rgb_to_hex(c) for c in palette],
        low_signal_flags=flags,
    )


def _dominant_color(rgb: np.ndarray) -> tuple[int, int, int]:
    small = rgb[::8, ::8].reshape(-1, 3)
    q = (small // 16) * 16
    vals, counts = np.unique(q, axis=0, return_counts=True)
    top = vals[np.argmax(counts)]
    return tuple(int(c) for c in top)


def _top_palette(rgb: np.ndarray, k: int = 5) -> list[tuple[int, int, int]]:
    small = rgb[::8, ::8].reshape(-1, 3)
    q = (small // 16) * 16
    vals, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)[:k]
    return [tuple(int(c) for c in vals[i]) for i in order]


def _looks_uniform_grid(edges: np.ndarray) -> bool:
    """Cheap test: column-wise edge sum has very low variance vs mean → repetitive grid."""
    col_sum = (edges > 24).sum(axis=0).astype(np.float32)
    if col_sum.mean() < 2:
        return False
    ratio = col_sum.std() / max(col_sum.mean(), 1e-6)
    return ratio < 0.35


# ========== heuristic scoring ==========

def norm(x: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (x - lo) / (hi - lo)))


def heuristic_score(f: HeuristicFeatures, region_name: str) -> float:
    # hard kills
    if "nav_like" in f.low_signal_flags:
        return 0.0
    if "near_empty" in f.low_signal_flags:
        return 0.02
    if "too_short" in f.low_signal_flags:
        return 0.05

    # base score
    score = (
        0.30 * norm(f.contrast_ratio, 1.2, 10.0)
        + 0.22 * norm(f.edge_density, 0.01, 0.18)
        + 0.18 * norm(f.color_variance, 12.0, 70.0)
        + 0.18 * norm(f.tension, 0.005, 0.08)
        + 0.12 * norm(f.focal_point, 1.1, 2.2)
    )

    # soft penalties
    if "uniform_grid" in f.low_signal_flags:
        score *= 0.6
    if "footer_like" in f.low_signal_flags or region_name == "footer":
        score *= 0.3

    return round(max(0.0, min(1.0, score)), 3)


# ========== vision scoring ==========

VISION_RUBRIC = """You are a senior design director reviewing a cropped region of a webpage.

Grade this region against the brand brief below, then output ONLY a JSON object
matching this exact structure (no prose, no markdown fences):

{
  "score_vision": <float 0..1>,
  "signals": {
    "typography": {
      "scale": "small" | "medium" | "large" | "extreme" | "mixed",
      "alignment": "left" | "centered" | "right" | "left_offset" | "justified",
      "density": "tight" | "normal" | "sparse"
    },
    "composition": {
      "symmetry": "symmetrical" | "asymmetrical",
      "dominant": "text" | "image" | "mixed" | "negative_space",
      "balance": "left-heavy" | "right-heavy" | "centered" | "top-heavy" | "bottom-heavy"
    },
    "contrast": "high" | "medium" | "low",
    "rhythm": "repetitive" | "structured" | "loose" | "none"
  },
  "region_guess": "hero" | "band" | "feature-grid" | "testimonial" | "pricing" | "cta" | "footer" | "unknown",
  "insight": "<one or two sentences: what makes this region interesting or useful>",
  "avoid": ["<case where this pattern should NOT be used>", "..."],
  "tags": ["editorial", "dark", "grounded", ...]
}

Scoring rubric for score_vision:
- 0.9–1.0: strong editorial pattern — clear focal point, confident typography, intentional asymmetry or deliberate structure, fits the brand brief
- 0.7–0.89: solid pattern with one weak axis (hierarchy OR rhythm OR balance)
- 0.5–0.69: competent but generic; would not stand out in a portfolio
- 0.3–0.49: template-ish; boring
- 0.0–0.29: navigation, footer, cookie banner, empty band, repetitive card grid, or broken layout

BRAND BRIEF:
"""


def _downscale_for_vision(im: Image.Image) -> bytes:
    w, h = im.size
    scale = min(1.0, VISION_MAX_IMAGE_DIM / max(w, h))
    if scale < 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---- OpenAI strict JSON schema (mirrors workflow/pattern-schema.json signals) ----
_OPENAI_JSON_SCHEMA = {
    "name": "pattern_signals",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["score_vision", "signals", "region_guess", "insight", "avoid", "tags"],
        "properties": {
            "score_vision": {"type": "number"},
            "signals": {
                "type": "object",
                "additionalProperties": False,
                "required": ["typography", "composition", "contrast", "rhythm"],
                "properties": {
                    "typography": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["scale", "alignment", "density"],
                        "properties": {
                            "scale": {"type": "string",
                                      "enum": ["small", "medium", "large", "extreme", "mixed"]},
                            "alignment": {"type": "string",
                                          "enum": ["left", "centered", "right", "left_offset", "justified"]},
                            "density": {"type": "string",
                                        "enum": ["tight", "normal", "sparse"]},
                        },
                    },
                    "composition": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["symmetry", "dominant", "balance"],
                        "properties": {
                            "symmetry": {"type": "string",
                                         "enum": ["symmetrical", "asymmetrical"]},
                            "dominant": {"type": "string",
                                         "enum": ["text", "image", "mixed", "negative_space"]},
                            "balance": {"type": "string",
                                        "enum": ["left-heavy", "right-heavy", "centered",
                                                 "top-heavy", "bottom-heavy"]},
                        },
                    },
                    "contrast": {"type": "string", "enum": ["high", "medium", "low"]},
                    "rhythm": {"type": "string",
                               "enum": ["repetitive", "structured", "loose", "none"]},
                },
            },
            "region_guess": {"type": "string",
                             "enum": ["hero", "band", "feature-grid", "testimonial",
                                      "pricing", "cta", "footer", "unknown"]},
            "insight": {"type": "string"},
            "avoid": {"type": "array", "items": {"type": "string"}},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
    },
}


def _vision_grade_anthropic(
    region: Region, brief_text: str, api_key: str, model: str
) -> Optional[dict]:
    png_bytes = _downscale_for_vision(region.image)
    b64 = base64.b64encode(png_bytes).decode("ascii")
    payload = {
        "model": model,
        "max_tokens": 800,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image",
                     "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                    {"type": "text", "text": VISION_RUBRIC + brief_text},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:300]
        print(f"    ! vision[anthropic] HTTP {e.code}: {err}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    ! vision[anthropic] error: {e}", file=sys.stderr)
        return None

    try:
        text = body["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
        return json.loads(text)
    except Exception as e:
        print(f"    ! vision[anthropic] parse error: {e}; raw={str(body)[:200]}", file=sys.stderr)
        return None


def _vision_grade_openai(
    region: Region, brief_text: str, api_key: str, model: str
) -> Optional[dict]:
    png_bytes = _downscale_for_vision(region.image)
    b64 = base64.b64encode(png_bytes).decode("ascii")
    payload = {
        "model": model,
        "max_tokens": 800,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": VISION_RUBRIC + brief_text},
                ],
            }
        ],
        "response_format": {"type": "json_schema", "json_schema": _OPENAI_JSON_SCHEMA},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:300]
        print(f"    ! vision[openai] HTTP {e.code}: {err}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    ! vision[openai] error: {e}", file=sys.stderr)
        return None

    try:
        text = body["choices"][0]["message"]["content"].strip()
        return json.loads(text)
    except Exception as e:
        print(f"    ! vision[openai] parse error: {e}; raw={str(body)[:200]}", file=sys.stderr)
        return None


def vision_grade_region(
    region: Region,
    brief_text: str,
    api_key: str,
    backend: str,
    model: Optional[str] = None,
) -> Optional[dict]:
    if backend == "openai":
        return _vision_grade_openai(region, brief_text, api_key, model or OPENAI_VISION_MODEL)
    return _vision_grade_anthropic(region, brief_text, api_key, model or ANTHROPIC_VISION_MODEL)


# ========== brief loading ==========

def load_brief_text(project: str) -> str:
    brief_path = PROJECT_ROOT / "inspiration" / project / "briefs" / "brand.json"
    if not brief_path.exists():
        return f"(no brief found at {brief_path})"
    brief = json.loads(brief_path.read_text())
    brand = brief.get("brand", {})
    lines = [
        f"- name: {brand.get('name')}",
        f"- industry: {brand.get('industry')}",
        f"- primary color: {brand.get('colors', {}).get('primary')}",
        f"- accent color: {brand.get('colors', {}).get('accent')}",
        f"- aesthetic tags: {', '.join(brief.get('aesthetic', []))}",
        f"- patterns wanted: {', '.join(brief.get('patterns_wanted', []))}",
        f"- avoid: {', '.join(brief.get('avoid', []))}",
    ]
    return "\n".join(lines)


# ========== main ==========

def run(
    project: str,
    input_dir_name: str,
    use_vision: bool,
    vision_backend: str,
    smoke_test: bool,
    limit: Optional[int],
) -> int:
    env = load_env(ENV_FILE)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    project_dir = PROJECT_ROOT / "inspiration" / project
    input_root = project_dir / input_dir_name
    segments_root = project_dir / "segments"
    segments_root.mkdir(parents=True, exist_ok=True)

    pattern_dir = PROJECT_ROOT / "pattern-library" / "candidates"
    pattern_dir.mkdir(parents=True, exist_ok=True)

    if not input_root.exists():
        print(f"ERROR: input dir not found: {input_root}", file=sys.stderr)
        return 2

    screenshots = sorted(input_root.glob("*/screenshot.png"))
    if not screenshots:
        print(f"ERROR: no screenshot.png under {input_root}", file=sys.stderr)
        return 2
    if limit:
        screenshots = screenshots[:limit]

    print(f"Input:     {input_root}  ({len(screenshots)} screenshots)")
    print(f"Segments:  {segments_root}")
    print(f"Patterns:  {pattern_dir}")
    print(f"Vision:    {'on (' + vision_backend + ')' if use_vision else 'off'}")
    if smoke_test:
        print("Mode:      SMOKE-TEST (output is validation, not quality inspiration)")

    brief_text = load_brief_text(project)
    api_key: Optional[str] = None
    if use_vision:
        env_var = "OPENAI_API_KEY" if vision_backend == "openai" else "ANTHROPIC_API_KEY"
        api_key = os.environ.get(env_var)
        if not api_key:
            print(f"ERROR: --vision set with backend={vision_backend} but {env_var} "
                  f"missing in .env", file=sys.stderr)
            return 2

    summary = {
        "generated_at": now_iso(),
        "project": project,
        "input_dir": str(input_root.relative_to(PROJECT_ROOT)),
        "use_vision": use_vision,
        "smoke_test": smoke_test,
        "counts": {"screenshots": len(screenshots), "regions": 0, "shortlisted": 0, "promoted": 0},
        "results": [],
    }

    for sp in screenshots:
        cand_id = sp.parent.name
        print(f"\n── {cand_id}")
        meta_path = sp.parent / "metadata.json"
        cand_meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        source = cand_meta.get("source", "unknown")
        source_url = cand_meta.get("url", "")
        source_title = cand_meta.get("title", "")

        try:
            im = Image.open(sp).convert("RGB")
        except Exception as e:
            print(f"  ! cannot open {sp}: {e}")
            continue

        regions = segment_image(im)
        print(f"  {len(regions)} regions after segmentation")
        summary["counts"]["regions"] += len(regions)

        cand_seg_dir = segments_root / cand_id
        cand_seg_dir.mkdir(parents=True, exist_ok=True)
        seg_manifest = []

        for i, r in enumerate(regions):
            seg_name = f"{i:02d}-{r.name}"
            seg_path = cand_seg_dir / f"{seg_name}.png"
            r.image.save(seg_path, format="PNG", optimize=True)

            f = compute_features(r)
            h_score = heuristic_score(f, r.name)

            seg_entry = {
                "index": i,
                "name": r.name,
                "bbox": r.bbox,
                "segment_image": str(seg_path.relative_to(PROJECT_ROOT)),
                "heuristic_score": h_score,
                "features": asdict(f),
                "vision": None,
                "promoted": False,
            }

            if h_score >= HEURISTIC_GATE:
                summary["counts"]["shortlisted"] += 1
                print(f"    [{i:02d}] {r.name:<8} h={h_score:.3f}  {f.low_signal_flags or ''}  → shortlist")

                vision_obj: Optional[dict] = None
                if use_vision:
                    vision_obj = vision_grade_region(r, brief_text, api_key, vision_backend)
                    time.sleep(2.0)

                v_score = vision_obj.get("score_vision") if vision_obj else None
                weighted = (
                    round(0.4 * h_score + 0.6 * v_score, 3)
                    if (v_score is not None)
                    else round(h_score, 3)
                )
                seg_entry["vision"] = vision_obj
                seg_entry["weighted_score"] = weighted

                if weighted >= PROMOTE_GATE:
                    pattern = build_pattern(
                        candidate_id=cand_id,
                        source=source,
                        source_url=source_url,
                        source_title=source_title,
                        captured_at=cand_meta.get("retrieved_at"),
                        region=r,
                        features=f,
                        h_score=h_score,
                        v_obj=vision_obj,
                        weighted=weighted,
                        seg_path=seg_path,
                        raw_screenshot_path=sp,
                    )
                    write_pattern(pattern, pattern_dir, seg_path)
                    seg_entry["promoted"] = True
                    summary["counts"]["promoted"] += 1
                    print(f"         ✓ promote weighted={weighted:.3f} id={pattern['id']}")
                else:
                    print(f"         · below PROMOTE_GATE weighted={weighted:.3f}")
            else:
                print(f"    [{i:02d}] {r.name:<8} h={h_score:.3f}  {f.low_signal_flags or ''}  → skip")

            seg_manifest.append(seg_entry)

        (cand_seg_dir / "_segments.json").write_text(
            json.dumps(
                {
                    "candidate_id": cand_id,
                    "source": source,
                    "source_url": source_url,
                    "raw_screenshot": str(sp.relative_to(PROJECT_ROOT)),
                    "segments": seg_manifest,
                },
                indent=2,
            )
        )
        summary["results"].append(
            {"candidate_id": cand_id, "source": source, "regions": len(regions), "segments": seg_manifest}
        )

    (project_dir / "metadata" / "extraction.json").write_text(json.dumps(summary, indent=2))
    c = summary["counts"]
    print("\n── Summary")
    print(f"  screenshots: {c['screenshots']}")
    print(f"  regions:     {c['regions']}")
    print(f"  shortlisted: {c['shortlisted']}   (heuristic >= {HEURISTIC_GATE})")
    print(f"  promoted:    {c['promoted']}   (weighted >= {PROMOTE_GATE})")
    return 0


def build_pattern(
    *,
    candidate_id: str,
    source: str,
    source_url: str,
    source_title: str,
    captured_at: Optional[str],
    region: Region,
    features: HeuristicFeatures,
    h_score: float,
    v_obj: Optional[dict],
    weighted: float,
    seg_path: Path,
    raw_screenshot_path: Path,
) -> dict:
    region_label = (v_obj or {}).get("region_guess") or region.name
    style_tag = "editorial"
    if v_obj and "tags" in v_obj and v_obj["tags"]:
        style_tag = re.sub(r"[^a-z0-9]+", "-", v_obj["tags"][0].lower()).strip("-") or "editorial"
    pid_hash = sha1_short(f"{candidate_id}:{region.y}:{region.h}", 6)
    pid = f"pattern_{region_label}_{style_tag}_{pid_hash}"

    signals_default = {
        "typography": {"scale": "medium", "alignment": "left", "density": "normal"},
        "composition": {"symmetry": "asymmetrical", "dominant": "mixed", "balance": "centered"},
        "contrast": "medium",
        "rhythm": "structured",
    }
    signals = (v_obj or {}).get("signals") or signals_default

    return {
        "id": pid,
        "source": source,
        "source_url": source_url,
        "source_title": source_title,
        "captured_at": captured_at,
        "extracted_at": now_iso(),
        "region": region_label,
        "bbox": region.bbox,
        "segment_image": str(seg_path.relative_to(PROJECT_ROOT)),
        "raw_screenshot": str(raw_screenshot_path.relative_to(PROJECT_ROOT)),
        "pattern_layer": "visual_language",
        "score": weighted,
        "score_breakdown": {
            "heuristic": h_score,
            "vision": (v_obj or {}).get("score_vision"),
            "weighted": weighted,
        },
        "features_heuristic": asdict(features),
        "signals": signals,
        "insight": (v_obj or {}).get("insight") or (
            f"Heuristic-only signal: contrast={features.contrast_ratio:.1f}, "
            f"edge_density={features.edge_density:.3f}, tension={features.tension:.3f}."
        ),
        "avoid": (v_obj or {}).get("avoid") or [],
        "tags": (v_obj or {}).get("tags") or [],
    }


def write_pattern(pattern: dict, pattern_dir: Path, seg_path: Path) -> None:
    pattern_dir.mkdir(parents=True, exist_ok=True)
    pid = pattern["id"]
    json_path = pattern_dir / f"{pid}.json"
    png_path = pattern_dir / f"{pid}.png"
    json_path.write_text(json.dumps(pattern, indent=2))
    try:
        # copy cropped region next to pattern JSON
        Image.open(seg_path).save(png_path, format="PNG", optimize=True)
    except Exception as e:
        print(f"    ! could not copy segment image: {e}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument(
        "--input-dir",
        default="raw",
        help="Subdir under inspiration/<project>/ to scan. Defaults to 'raw'; "
             "use 'candidates' for the legacy/smoke-test corpus.",
    )
    p.add_argument("--vision", action="store_true",
                   help="Run vision-LLM grading on shortlisted regions")
    p.add_argument("--vision-backend", choices=["anthropic", "openai"], default="anthropic",
                   help="Which vision API to use. Reads ANTHROPIC_API_KEY or OPENAI_API_KEY "
                        "from .env accordingly.")
    p.add_argument("--smoke-test", action="store_true", help="Mark this run as a smoke-test (annotates summary)")
    p.add_argument("--limit", type=int, default=None, help="Only process first N screenshots")
    args = p.parse_args()

    return run(
        project=args.project,
        input_dir_name=args.input_dir,
        use_vision=args.vision,
        vision_backend=args.vision_backend,
        smoke_test=args.smoke_test,
        limit=args.limit,
    )


if __name__ == "__main__":
    sys.exit(main())
