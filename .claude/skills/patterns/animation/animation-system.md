# Animation System (Framer Motion)

Guidelines for interaction and motion design using Framer Motion.

## Principles

- Motion should support meaning, not decoration
- Prefer subtle over excessive
- Use motion to guide attention and hierarchy
- Respect user expectations and performance

## Allowed Patterns

### 1. Entrance animations
- Fade + slight translate
- Staggered children
- Duration: 0.3–0.6s

### 2. Hover interactions
- Scale (1.02–1.05)
- Subtle elevation
- Color transitions

### 3. Scroll-based animations
- Reveal on scroll
- Parallax for backgrounds (subtle only)
- Section transitions

### 4. Micro-interactions
- Button feedback
- Card hover
- Toggle states

## Parallax Rules

- Use only for background or large sections
- Never on text readability layers
- Keep movement subtle (10–30px max)
- Avoid on mobile if performance drops

## Avoid

- Excessive bouncing
- Long durations (>800ms)
- Distracting motion loops
- Animation on every element

## Accessibility

- Respect `prefers-reduced-motion`
- Ensure content is readable without animation
