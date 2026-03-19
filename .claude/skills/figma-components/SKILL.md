---
name: figma-components
description: Build a fully functional UI component from a Figma design using the Figma MCP, including specifications, implementation, previews, and documentation.
---

# Figma Component Development

Generate a production-ready component from a Figma design file using the Figma MCP integration.

## Steps

### 1. Connect and verify Figma access

Use the Figma MCP to connect to the design file. Confirm access before proceeding.
Ask the user for the Figma file URL or node ID if not already provided.

### 2. Extract component data

Fetch all relevant data for the target component from Figma:

- Node tree and layout structure
- All variants and component sets
- Auto-layout and constraint rules

### 3. Document visual specifications

Record the following from the Figma data:

| Category | Details to capture |
|---|---|
| Dimensions | width, height, padding, margins |
| Typography | font family, size, weight, line-height |
| Colors | fills, strokes, gradients, opacity |
| Shape | border radius, shadows/elevation |
| Spacing | gaps, alignment, distribution |

### 4. Document behavioral specifications

- Interactive states: hover, active, focus, disabled
- Animations and transitions (duration, easing)
- Responsive behavior and breakpoints
- Accessibility: ARIA roles, labels, keyboard navigation

### 5. Implement the component

Build the component to match the Figma design exactly:

- Implement all variants defined in the Figma component set
- Add TypeScript interfaces for all props
- Cover all interactive states and transitions
- Ensure responsive behavior at defined breakpoints
- Handle edge cases and error states

Place implementation files under the appropriate source directory (e.g., `src/components/<ComponentName>/`). Do NOT place files in the project root.

### 6. Create preview showcases

Generate a preview file (e.g., `<ComponentName>.preview.tsx` or equivalent) that demonstrates:

- **Design tokens**: colors, typography, spacing, border-radius, shadows, animations used
- **Variants**: all component variants rendered side by side
- **Theme variations**: light/dark mode if applicable
- **Size variations**: small, medium, large if applicable
- **States**: interactive demo of hover, active, focus, disabled
- **Responsive**: behavior at different breakpoints

Add the preview as a tab on the existing components page rather than creating a standalone page.

### 7. Generate documentation

Create a `.txt` or `.md` documentation file for the component containing:

- Purpose and usage description
- Prop reference (name, type, default, description, constraints)
- Code examples for common use cases
- Accessibility notes
- Design token references

Place documentation in `docs/components/` or alongside the component source.

### 8. Write tests

Cover the component with unit or integration tests following project conventions
(see `write-tests` skill). Verify:

- Each variant renders without errors
- Interactive states apply correct styles/attributes
- Accessibility attributes are present
- Props validation and edge cases

Run `make test-cov-check` to confirm coverage meets the threshold.

## Output structure

```
src/components/<ComponentName>/
  index.tsx              # Main component implementation
  <ComponentName>.types.ts   # TypeScript interfaces/types
  <ComponentName>.preview.tsx  # Visual preview showcase
  <ComponentName>.test.tsx     # Tests

docs/components/
  <ComponentName>.md     # Usage documentation
```

## Execution order

1. **Fetch** — pull all component data from Figma via MCP
2. **Specify** — document visual and behavioral specs
3. **Build** — implement component with all variants and states
4. **Preview** — create visual showcase added to the components page
5. **Document** — write usage guide and prop reference
6. **Test** — write and run tests; verify coverage