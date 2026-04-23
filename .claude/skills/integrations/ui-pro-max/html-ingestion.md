# HTML ingestion

Use generated HTML, JSX, or similar UI code from UI Pro Max as upstream structure guidance.

## Purpose
Convert code structure into a clean Figma layout model before execution.

## Parse into layout intent
Interpret code using these mappings:

- div, section, main, aside, header, footer → frames
- nested containers → nested auto layout frames
- h1-h6 → text layers with heading roles
- p, span, small → text layers with body/label roles
- button, a styled as button → component candidates
- input, select, textarea → form component candidates
- img, svg, picture → image/media layers or icon candidates

## Layout interpretation
- flex-row → horizontal auto layout
- flex-col → vertical auto layout
- gap-* → item spacing
- p-* / px-* / py-* → frame padding
- justify-* → distribution intent
- items-* → alignment intent

## Rules
- do not treat HTML as final pixel-perfect truth
- preserve hierarchy and grouping from code
- convert utility classes into design-system-friendly structure
- prefer auto layout over absolute positioning
- identify repeated structures as component candidates
