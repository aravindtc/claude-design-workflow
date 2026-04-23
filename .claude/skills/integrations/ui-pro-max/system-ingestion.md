# System ingestion

Read UI Pro Max design system files as upstream guidance.

## Source priority
1. design-system/[project-name]/pages/[page-name].md
2. design-system/[project-name]/MASTER.md

## Extract and normalize
From the available file(s), extract:

### Colors
Map raw colors into semantic token candidates such as:
- color.background.primary
- color.background.surface
- color.text.primary
- color.text.secondary
- color.action.primary
- color.border.default

### Typography
Map typography recommendations into role-based styles such as:
- text.heading.xl
- text.heading.l
- text.body.m
- text.body.s
- text.label.m

### Spacing
Normalize spacing into a repeatable scale.
Prefer a 4pt or 8pt system rather than one-off values.

### Radius, borders, shadows
Normalize repeated visual values into token candidates.

## Rules
- do not preserve raw values as final system names
- prefer semantic naming over presentation naming
- page-level overrides take precedence over MASTER.md
- do not create tokens for one-off usage unless explicitly required
