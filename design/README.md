# Design Tokens

This directory contains the design tokens for the FloodSight application.

## Files

- **figma-tokens.json**: The source of truth for all design tokens. These are synced from Figma.
- **tokens.js**: JavaScript module that exports the tokens for use in build scripts.
- **tokens.ts**: TypeScript version (future implementation)

## Usage

### Applying Tokens

Run the following command to regenerate CSS variables from the design tokens:

```bash
npm run tokens:apply
```

This will update `/public/assets/css/tokens.css` with the latest token values.

### Using Tokens in CSS

The tokens are available as CSS custom properties:

```css
.my-element {
  color: var(--color-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
  font-family: var(--font-body);
}
```

## Token Categories

- **color**: Brand colors, backgrounds, foregrounds
- **radius**: Border radius values
- **font**: Font family definitions
- **fontSize**: Text size scale
- **spacing**: Spacing scale
- **shadow**: Box shadow definitions

## Dark Mode

Dark mode variants are automatically applied via:

- `.dark` class on the root element
- `prefers-color-scheme: dark` media query
