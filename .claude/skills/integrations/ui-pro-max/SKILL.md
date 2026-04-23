# Skill: UI Pro Max → Figma integration

You convert UI Pro Max outputs into structured Figma systems and designs.

## Inputs
- design-system/[project-name]/MASTER.md
- design-system/[project-name]/pages/[page-name].md
- generated HTML UI
- component structures
- approved custom style profile (session or persistent), if available

## Outputs
- Figma variables
- reusable components
- structured frames using auto layout

## Workflow
1. Read design-system/[project-name]/MASTER.md first
2. Read page override if it exists at design-system/[project-name]/pages/[page-name].md
3. Read approved custom style profile if one exists
4. Read generated HTML or UI code if relevant
5. Normalize tokens into semantic design tokens
6. Pass token creation to the design-system skill
7. Pass layout conversion to the html-to-figma bridge
8. Pass final refinement to the appropriate context skill
9. Validate consistency before completion

## Custom style override

If a custom style exists (session or persistent):

- prioritize it over UI Pro Max style recommendations
- use UI Pro Max only for:
  - structure
  - accessibility
  - best practices

Do NOT override custom style with default styles.

## Rules
- do not blindly copy raw Tailwind values into Figma
- convert repeated values into semantic tokens
- preserve hierarchy from HTML
- use auto layout rather than manual positioning where possible
- treat UI Pro Max as upstream guidance, not final truth
