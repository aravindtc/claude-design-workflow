# AI Aurora Glass

> A futuristic glassmorphism style layered over shifting aurora gradients. Designed for AI products, developer tools, and tech-forward brands that want to feel cutting-edge without being cold. Depth through translucency, not shadow.

---

## Variation Axes

| Axis | Range | Default |
|------|-------|---------|
| Gradient Intensity | Subtle wash ↔ Vivid aurora | Moderate |
| Glass Opacity | Nearly transparent ↔ Frosted | Frosted |
| Blur Strength | Light haze (8px) ↔ Deep frost (24px) | 16px |
| Glow | None ↔ Ambient color bleed | Subtle glow |
| Motion | Static ↔ Animated gradients | Static (CSS only) |

---

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Aurora Green | `#00D4AA` | Primary accent, active states |
| Aurora Violet | `#7C3AED` | Secondary accent, gradients |
| Aurora Blue | `#0EA5E9` | Links, info states |
| Aurora Pink | `#EC4899` | Highlights, notifications |
| Background | `#0B0F1A` | Deep dark base |
| Surface Glass | `rgba(255, 255, 255, 0.06)` | Card/container fill |
| Surface Glass Hover | `rgba(255, 255, 255, 0.10)` | Elevated/hover state |
| Border Glass | `rgba(255, 255, 255, 0.12)` | Glass edge borders |
| Text Primary | `#F1F5F9` | Headings, primary content |
| Text Secondary | `#94A3B8` | Body, descriptions |
| Text Muted | `#64748B` | Metadata, timestamps |

**Palette Notes:** Background must stay dark (`< #1A`) for glass layers to read. Aurora colors are for accents only — never use them as flat background fills. The palette is additive: colors glow against the dark base.

### Aurora Gradient

```css
.aurora-bg {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(0, 212, 170, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(124, 58, 237, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 80%, rgba(14, 165, 233, 0.10) 0%, transparent 50%),
    #0B0F1A;
}
```

---

## Typography

- **Heading Font:** Inter
- **Body Font:** Inter
- **Mono Font:** JetBrains Mono (code blocks, data, metrics)
- **Mood:** Clean, technical, precise, modern
- **Google Fonts:** [Inter + JetBrains Mono](https://fonts.google.com/share?selection.family=Inter:wght@300;400;500;600;700|JetBrains+Mono:wght@400;500;600)

**CSS Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | `2.25rem` / `36px` | 700 | 1.2 |
| H2 | `1.5rem` / `24px` | 600 | 1.3 |
| H3 | `1.125rem` / `18px` | 600 | 1.4 |
| Body | `0.9375rem` / `15px` | 400 | 1.6 |
| Caption | `0.8125rem` / `13px` | 400 | 1.5 |
| Mono/Data | `0.875rem` / `14px` | 500 (JetBrains) | 1.5 |

---

## Glass Language

### Core Glass Effect

```css
.glass {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
}
```

### Glass Hierarchy

| Layer | Background Alpha | Blur | Border Alpha | Usage |
|-------|-----------------|------|-------------|-------|
| Surface | `0.06` | `16px` | `0.12` | Cards, panels |
| Elevated | `0.10` | `20px` | `0.15` | Modals, popovers |
| Inset | `0.03` | `8px` | `0.08` | Input fields, nested containers |
| Nav | `0.08` | `24px` | `0.10` | Top nav, sidebars |

### Glow Effects

```css
/* Accent glow — use sparingly on focus/active states */
.glow-green {
  box-shadow: 0 0 20px rgba(0, 212, 170, 0.15),
              0 0 60px rgba(0, 212, 170, 0.05);
}

.glow-violet {
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.15),
              0 0 60px rgba(124, 58, 237, 0.05);
}
```

---

## Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `4px` | Tight inline gaps |
| `--space-sm` | `8px` | Icon gaps, badge padding |
| `--space-md` | `16px` | Card padding, form gaps |
| `--space-lg` | `24px` | Section inner padding |
| `--space-xl` | `40px` | Between major sections |
| `--space-2xl` | `64px` | Hero/feature spacing |

---

## Component Patterns

### Buttons

```css
.btn-primary {
  background: linear-gradient(135deg, #00D4AA, #0EA5E9);
  color: #0B0F1A;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9375rem;
  border: none;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-primary:hover {
  box-shadow: 0 0 24px rgba(0, 212, 170, 0.25);
  transform: translateY(-1px);
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.06);
  color: #F1F5F9;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 200ms ease;
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.10);
  border-color: rgba(255, 255, 255, 0.20);
}
```

### Cards

```css
.card {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 24px;
  transition: all 250ms ease;
  cursor: pointer;
}

.card:hover {
  background: rgba(255, 255, 255, 0.10);
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### Inputs

```css
.input {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px 16px;
  color: #F1F5F9;
  font-size: 0.9375rem;
  backdrop-filter: blur(8px);
  transition: all 200ms ease;
}

.input:focus {
  border-color: rgba(0, 212, 170, 0.5);
  box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
  outline: none;
}

.input::placeholder {
  color: #64748B;
}
```

### Status Badges

```css
.badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.badge-success {
  background: rgba(0, 212, 170, 0.15);
  color: #00D4AA;
  border: 1px solid rgba(0, 212, 170, 0.25);
}

.badge-info {
  background: rgba(14, 165, 233, 0.15);
  color: #0EA5E9;
  border: 1px solid rgba(14, 165, 233, 0.25);
}
```

---

## Anti-Patterns

- No flat opaque backgrounds on cards — always use translucent glass
- No white or light page backgrounds — the aurora needs a dark canvas
- No heavy box-shadows as the primary depth cue — use blur + border instead
- No thick borders (`> 1px`) — glass edges are always delicate
- No emoji as icons — use Lucide or Heroicons (outline style)
- No saturated aurora colors as text color on dark backgrounds (contrast issues)
- No glass-on-glass stacking beyond 2 layers (readability degrades)
- No animated gradients without `prefers-reduced-motion` fallback

---

## Best For

- AI/ML product dashboards
- Developer tools and CLIs with web UIs
- SaaS analytics platforms
- Crypto/Web3 interfaces
- Tech startup landing pages
- API documentation portals
