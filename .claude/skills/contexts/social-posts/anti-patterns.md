# Social Post Anti-Patterns

Things that consistently produce weak or broken social post designs.

## Layout anti-patterns

**Scattered text** — date top-left, headline center, offer bottom-right, CTA somewhere else.
Fix: group all copy into one anchored zone.

**Dead center with no tension** — everything centered with equal spacing above and below.
Fix: use asymmetric placement with a deliberate anchor (upper third or lower third).

**Too many accent shapes** — three bars, two corner blocks, a rule, and a badge.
Fix: reduce to one or two accent elements that earn their place by supporting hierarchy.

**Text trapped against the edge** — less than 40px margin, especially on mobile-crop-sensitive sides.
Fix: enforce minimum 48px safe padding on all edges.

**Image and text competing for the same zone** — busy image behind unprotected text.
Fix: add overlay, move text, or crop the image to a quieter section.

**Equal weight everywhere** — headline, offer, CTA all same size and prominence.
Fix: establish clear size/weight hierarchy: headline > secondary > CTA.

**Image distortion** — image resized with different x/y scaling, stretched or squashed subject.
Fix: always maintain aspect ratio, or crop symmetrically.

---

## Color anti-patterns

**Brand color on everything** — accent color applied to header, background, rule, button, and icon.
Fix: use brand color in one or two places only, let it pop.

**Low opacity as minimalism** — reducing opacity of existing elements instead of simplifying structure.
Fix: simplify through removal, spacing, and grouping — not transparency.

**White text on light background after color swap** — changing background to light and forgetting to update text color.
Fix: always check text fills when changing background fills.

**CTA disappears after dark mode swap** — dark button on dark background.
Fix: in dark mode, make CTA button a brand accent color or white.

**Too many hues** — three or more distinct colors competing in the frame.
Fix: one background, one accent, one text palette. Maximum.

---

## CTA / button text anti-patterns

**Left-aligned text inside a pill or rounded button** — text appears shifted left, button looks broken.
Fix: load the font, set `textAlignHorizontal = "CENTER"`, resize text container to full button width, position at `btnX, btnY + (btnH - textH) / 2`.

**Text container narrower than the button** — even if centered numerically, the visual text appears off-center.
Fix: always set text container width = button width.

**Text rotation not matching button rotation** — text and button drift apart visually when either is rotated.
Fix: always set `textNode.rotation = btnNode.rotation` after positioning.

**Assuming the font style string** — `loadFontAsync({ family: "X", style: "Bold" })` fails silently if the style doesn't exist.
Fix: always call `listAvailableFontsAsync()` first and find the exact style string before loading.

---

## Figma execution anti-patterns

**Resizing text containers without checking child text** — container grows but text stays clipped or overflows.
Fix: also resize child text nodes to match.

**Moving elements by feel without calculating overlaps** — two elements accidentally sharing y-space.
Fix: always compute `bottom = y + height` and ensure `nextElement.y >= bottom + gap`.

**Using opacity to hide elements instead of positioning** — opacity=0 elements still occupy space in some layouts.
Fix: move hidden elements off-frame (x = -9999) or keep opacity approach only for non-layout elements.

**Cloning and immediately editing without checking IDs** — assuming child IDs based on source order.
Fix: always inspect cloned frame children before editing, or use name-based lookups.
