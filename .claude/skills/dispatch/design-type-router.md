# Design Type Router

---

## Inspiration Engine Routing

If the user:
- provides visual inspiration
- mentions inspiration, references, moodboard
- or has a selected Figma frame with multiple images

Then:

1. Load /skills/inspiration-engine/*
2. Run:
   - asset-decomposition.md
   - cross-image-consolidation.md
   - creative-synthesis.md
   - approval-flow.md

3. Block all downstream generation until style approval is complete

After approval:
→ continue to Content Story phase

---

## Content Story Routing

After:
- inspiration extraction is complete
- style is approved

Then:

1. Load /skills/context/story/*

2. Ask the user for:
   - product / project description
   - target audience
   - primary goal
   - key actions
   - value proposition

3. STOP execution
4. WAIT for user input

Only after user input:
- build narrative
- build page structure
- draft content

Block all UI generation until content is complete

---

## Visual Direction Routing (NEW)

After:
- content is defined
- page structure is defined

Then:

1. Define composition intent for the page:

   - Where is the primary visual anchor? (hero)
   - Where should attention peak vs calm down?
   - Which sections are:
     - expressive
     - restrained

2. Define contrast strategy:

   - light vs dark sections
   - dense vs open sections
   - visual weight distribution

3. Define rhythm:

   - where pacing accelerates (dense content)
   - where it pauses (whitespace / minimal)

4. Define component expressiveness:

   - which components can be visually rich
   - which must remain minimal

5. Define anti-template guard:

   - avoid uniform section treatment
   - avoid repeated card grids unless justified

Output:
- visual rhythm map
- emphasis plan per section

Only after this:
→ proceed to visual assets and design system


---


## Visual Asset Routing (NEW)

After:
- content is defined
- page structure is defined

Then:

1. Load /skills/visual/asset-selection/*

2. For each section:
   - determine if imagery is needed
   - define image intent (what the image should communicate)
   - define image type:
     - photography
     - illustration
     - abstract
     - iconography

3. Generate:
   - image search queries
   - visual direction per section
   - placement strategy

4. Present to user:
   - list of image concepts / queries

5. WAIT for approval or refinement

Only after approval:
→ continue to design system and Figma build


---

## Design System Routing (CRITICAL LAYER)

After:
- style is approved
- content is defined

Then:

1. Load /skills/integrations/ui-pro-max/*
2. Translate style + content into a structured design system:

Must define:
- color tokens
- typography system
- spacing scale
- grid system
- layout rules
- component principles

This step is mandatory.

Do NOT build UI before system is defined.

---

## Figma Build Routing

After:
- design system is defined

Then:

Build in Figma using MCP with:

- Variables (colors, spacing, typography)
- Styles (text, effects, fills)
- Grid structure (columns, margins)
- Auto layout (no absolute positioning unless needed)
- Reusable components

---

## Responsive Routing (MANDATORY)

For all landing pages / websites:

You must:

- design desktop layout first
- adapt to tablet
- adapt to mobile

Ensure:
- layout reflows correctly
- spacing scales properly
- text remains readable
- no overlap or breakage

This is NOT optional.

---

## Animation Routing

If:
- marketing / landing page
- storytelling sections
- hero / transitions

Then:
- use /patterns/animation/*
- integrate framer-motion where appropriate

If:
- dashboard or data-heavy UI

Then:
- limit to micro-interactions

Always:
- prioritize clarity over motion

---

## Code Generation Routing

After:
- Figma design is approved

Then:

1. Generate code (HTML / Tailwind / React etc.)
2. Preserve:
   - layout
   - hierarchy
   - responsiveness
   - animation logic

---

## Final QA Routing

After:
- Figma OR code is generated

Then:

1. Run /skills/critique/final-visual-check.md

Check:
- responsive behavior
- spacing consistency
- variable/style usage
- grid alignment
- animation quality
- broken layout

Fix everything before completion

---

## Design System Governance Routing

After ANY of the following:
- a new major section is created
- a new screen is created
- a new component is introduced
- inspiration introduces a new visual treatment
- before final Figma completion
- before code generation

Then:

1. Load /skills/critique/design-system-governance.md
2. Run Design System Governance Scan
3. Compare new work against the current design system
4. Detect token, typography, component, layout, responsive, and style drift
5. For each finding, suggest one of:
   - reuse existing system
   - update component
   - add new token/component
   - reject/simplify
   - defer decision
6. PAUSE for user approval before changing the design system

No design system updates happen without user consent.

This routing is mandatory at every checkpoint above. Do not skip it to "save a turn" — drift caught late is far more expensive than drift caught at the section boundary.

---

## GLOBAL EXECUTION GUARD

No UI should be generated unless ALL are complete:

1. style is approved
2. content is defined
3. design system is created
4. responsive logic is applied

No final Figma delivery and no code generation may occur unless the Design System Governance Scan has run on the latest work and any approved updates have been applied.