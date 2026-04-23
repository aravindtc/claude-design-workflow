# Community Organic Minimal

> A warm, approachable style built around organic shapes, generous whitespace, and earthy tones. Designed for community-driven brands, wellness platforms, and social spaces that prioritize human connection over flashy UI.

---

## Variation Axes

| Axis | Range | Default |
|------|-------|---------|
| Warmth | Cool neutral ↔ Warm earth | Warm earth |
| Density | Airy/spacious ↔ Compact | Airy |
| Roundness | Soft rounded ↔ Pill/circular | Soft rounded |
| Texture | Flat ↔ Subtle grain | Subtle grain |
| Illustration | None ↔ Hand-drawn accents | Light accents |

---

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#5B7553` | Headings, primary actions — muted sage green |
| Secondary | `#D4A574` | Accents, tags, highlights — warm terracotta |
| Background | `#FAF7F2` | Page background — warm off-white |
| Surface | `#FFFFFF` | Cards, elevated containers |
| Text Primary | `#2C2C2C` | Body text — soft black, never pure `#000` |
| Text Secondary | `#6B6B6B` | Captions, metadata |
| Border | `#E8E2D9` | Dividers, card borders — warm gray |
| Accent | `#C4785B` | Notifications, badges — burnt sienna |

**Palette Notes:** No saturated primaries. Every color should feel like it could exist in nature. Avoid neon, electric blue, or pure black.

---

## Typography

- **Heading Font:** DM Serif Display
- **Body Font:** DM Sans
- **Mood:** Friendly, readable, editorial, grounded
- **Google Fonts:** [DM Serif Display + DM Sans](https://fonts.google.com/share?selection.family=DM+Sans:wght@300;400;500;600;700|DM+Serif+Display:wght@400)

**CSS Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | `2.5rem` / `40px` | 400 (serif) | 1.2 |
| H2 | `1.875rem` / `30px` | 400 (serif) | 1.3 |
| H3 | `1.25rem` / `20px` | 600 (sans) | 1.4 |
| Body | `1rem` / `16px` | 400 (sans) | 1.6 |
| Caption | `0.875rem` / `14px` | 400 (sans) | 1.5 |
| Label | `0.75rem` / `12px` | 500 (sans) | 1.4 |

---

## Shape Language

- **Border Radius:** `12px` default, `20px` for cards, `999px` for pills/avatars
- **Corners:** Always rounded — no sharp edges
- **Icons:** Outlined stroke style (Lucide preferred), 1.5px stroke weight
- **Avatars:** Always circular
- **Dividers:** Use spacing over visible lines where possible; when needed, `1px solid #E8E2D9`

---

## Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `4px` | Tight inline gaps |
| `--space-sm` | `8px` | Icon-to-label, tag padding |
| `--space-md` | `16px` | Card inner padding |
| `--space-lg` | `28px` | Section inner padding |
| `--space-xl` | `48px` | Between sections |
| `--space-2xl` | `72px` | Hero breathing room |

**Spacing Note:** Err on the side of more whitespace. Content should breathe. Cramped layouts break the organic feel.

---

## Component Patterns

### Buttons

```css
.btn-primary {
  background: #5B7553;
  color: white;
  padding: 12px 28px;
  border-radius: 999px;
  font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  transition: all 200ms ease;
  cursor: pointer;
  border: none;
}

.btn-primary:hover {
  background: #4A6344;
  transform: translateY(-1px);
}

.btn-secondary {
  background: transparent;
  color: #5B7553;
  border: 1.5px solid #5B7553;
  padding: 12px 28px;
  border-radius: 999px;
  font-weight: 500;
  transition: all 200ms ease;
  cursor: pointer;
}
```

### Cards

```css
.card {
  background: #FFFFFF;
  border: 1px solid #E8E2D9;
  border-radius: 20px;
  padding: 28px;
  transition: box-shadow 200ms ease;
  cursor: pointer;
}

.card:hover {
  box-shadow: 0 8px 24px rgba(91, 117, 83, 0.08);
}
```

### Tags / Chips

```css
.tag {
  background: #F3EDE4;
  color: #5B7553;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}
```

---

## Texture & Background

- **Background Grain:** Optional subtle noise texture at 3-5% opacity over `#FAF7F2`
- **Illustrations:** Minimal line-art or hand-drawn SVG accents (stems, leaves, abstract curves)
- **Photography:** Warm-toned, natural light, candid over posed
- **Shadows:** Very subtle — `0 2px 8px rgba(0,0,0,0.04)` max for resting state

---

## Anti-Patterns

- No sharp 0px border-radius on visible elements
- No saturated/neon colors
- No dense data tables (use cards or lists instead)
- No heavy drop shadows
- No dark mode by default (this style is inherently light)
- No emoji as icons
- No all-caps headings (sentence case only)

---

## Best For

- Community platforms, forums, social feeds
- Wellness, sustainability, lifestyle brands
- Creator/artist portfolios
- Newsletter landing pages
- Non-profit and education sites
