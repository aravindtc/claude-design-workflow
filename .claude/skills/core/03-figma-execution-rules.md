# Figma Execution Rules

Rules for applying design changes via the Figma Plugin API (use_figma).

## Before touching any layers

1. Inspect the selected frame — get node ID, name, size, children
2. Run diagnosis (see `02-critique-framework.md`)
3. Plan each variation in writing before executing
4. Clone the source frame — never modify the original

## Cloning and positioning

- Clone the source with `.clone()`
- Place variations with consistent spacing (80px gap recommended)
- User specifies direction (right, below, etc.) — default is right
- Append clones to the page with `figma.currentPage.appendChild()`
- Name each clone clearly before editing

## Layer editing rules

**Allowed:**
- Move existing groups, frames, or text blocks
- Resize text containers (does not require font loading)
- Resize and reposition rectangles and shapes
- Add simple geometric blocks (Rectangle, Ellipse)
- Change fills on shapes and frames
- Change fills on text nodes (does not require font loading)
- Change opacity
- Reorder layers (insertChild)

**Requires font loading:**
- Changing `characters` (text content)
- Changing `fontSize`
- Changing `fontName`
- Changing `textStyleId`
- Always call `await figma.loadFontAsync({ family, style })` before these

**Avoid by default:**
- Modifying the original source frame
- Deep child inspection unless absolutely required
- Changing copy meaning
- Squashing or stretching images (preserve aspect ratio or use intentional crop)

## Spacing and position logic

- Calculate all element positions explicitly — never guess
- Verify no bounding boxes overlap before executing
- Use a consistent left margin (e.g., 60px) and right margin
- Anchor text to zones (top, middle, bottom) with deliberate gaps
- When stacking text elements, calculate each `bottom = y + height` and set `nextY = bottom + gap`

## Color rules

- All colors use 0–1 range: `{ r: 1, g: 0, b: 0 }` = red
- Fills are read-only arrays — always reassign: `node.fills = [{ type: "SOLID", color: {...} }]`
- Never mutate the fills array in place

## Page context

- Always call `await figma.setCurrentPageAsync(figma.root.children[0])` at the start of each script
- Page context resets between `use_figma` calls

## Return values

- Every script that creates or mutates nodes MUST return all affected node IDs
- Return structured objects: `{ createdNodeIds: [...], mutatedNodeIds: [...] }`
- Never use `figma.notify()` — it throws "not implemented"
- Never use `console.log()` for output — use `return`

## Button text rules

Button text must always be visually contained within its button shape. Never leave this to chance.

**Standard buttons:**
- Set text container width = button width
- Set text container x = button x
- Set text container y = button y + (button height − text height) / 2
- Set `textAlignHorizontal = "CENTER"` (requires font loading — always load the font first)
- Use `listAvailableFontsAsync()` to find the exact style string before calling `loadFontAsync()`

**Artistic / rotated buttons:**
- Apply the same rotation to both the button shape and its text node
- Text container must match button x, y, width exactly — do not offset it independently
- Never position text by feel — always derive coordinates from the button node's own x/y/width/height

**Font loading sequence for button text:**
```js
const fonts = await figma.listAvailableFontsAsync();
// find exact style for the font family, then:
await figma.loadFontAsync({ family: "FontFamily", style: "ExactStyle" });
textNode.textAlignHorizontal = "CENTER";
textNode.resize(btnNode.width, textNode.height);
textNode.x = btnNode.x;
textNode.y = btnNode.y + (btnNode.height - textNode.height) / 2;
textNode.rotation = btnNode.rotation;
```

**Never:**
- Leave text left-aligned inside a centered pill or rounded button
- Position text with an arbitrary x offset from the button
- Assume the font style string — always verify with `listAvailableFontsAsync()`

## Incremental execution

- Break complex operations across multiple `use_figma` calls
- Inspect first, then create, then apply changes
- Validate positions mathematically before submitting
