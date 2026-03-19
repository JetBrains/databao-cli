---
name: figma-design
description: Extract a Figma design system via the Figma MCP and generate a design-tokens.ts file plus a live styleguide page that displays all tokens.
---

# Figma Design System

Extract the full design system from Figma and materialise it as a typed token file and a visual styleguide page.

## Steps

### 1. Connect to Figma and read the style guide

Use the Figma MCP to connect to the design file. Ask for the file URL or node ID if not provided. Fetch:

- Color styles (fills, strokes, semantic aliases)
- Text styles (font families, sizes, weights, line heights)
- Effect styles (shadows, blurs)
- Grid/spacing definitions
- Component icons and image assets

### 2. Create `design-system/styles/design-tokens.ts`

Write a single TypeScript file that exports typed constant objects for every token category:

| Export | Contents |
|---|---|
| `colors` | Primary, secondary, neutral palettes; semantic tokens (error, warning, success, info) |
| `typography` | Font families, size scale, weight values, line height scale |
| `spacing` | Full spacing scale following Tailwind conventions (0, 0.5, 1, 1.5 … 96) |
| `borderRadius` | None, sm, md, lg, xl, full |
| `shadows` | Elevation levels (sm, md, lg, xl) with full box-shadow strings |
| `breakpoints` | sm, md, lg, xl, 2xl with pixel values |
| `icons` | Exported SVG paths or asset URLs for every icon in the file |
| `images` | Asset URLs or base64 strings for image assets |

All values must be derived directly from Figma — do not invent or approximate values.

### 3. Create the `design-system/styleguide` page

Build a page (framework-appropriate: React/Next.js page, Streamlit page, plain HTML, etc.) that visually renders all token categories:

- **Colors** — swatches with token name and hex value
- **Typography** — live text samples at each size/weight combination
- **Spacing** — visual ruler showing each spacing step with its value
- **Border radius** — boxes demonstrating each radius value
- **Shadows** — cards showing each elevation level
- **Breakpoints** — labelled reference table
- **Icons** — icon grid with names
- **Images** — thumbnail gallery with asset names

Register the page in the project's routing/navigation so it is reachable at `/design-system/styleguide`.

### 4. Verify tokens are complete

Cross-check the exported tokens against the Figma data:

- Every named color style in Figma has a corresponding token.
- Every text style has a corresponding typography token.
- No values were approximated — all numbers come from the Figma API response.

### 5. Lint and type-check

Run the project's lint and type-check commands (e.g. `make check`) and fix any issues in the generated files before considering the task done.

## Output structure

```
design-system/
  styles/
    design-tokens.ts      # All typed token exports
  styleguide/
    page.tsx              # (or equivalent) Visual styleguide page
```

Do NOT place any generated files in the project root.
