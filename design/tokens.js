/**
 * Design tokens imported from Figma
 * Auto-generated - do not edit manually
 * Run `npm run tokens:apply` to regenerate
 */

import tokensData from './figma-tokens.json';

export const tokens = tokensData;

/**
 * Generate CSS custom properties from design tokens
 * @returns {string} CSS variables string
 */
export function generateCSSVariables() {
  const cssVars = [];
  
  // Colors
  Object.entries(tokens.color).forEach(([key, { value }]) => {
    cssVars.push(`  --color-${key}: ${value};`);
  });
  
  // Radius
  Object.entries(tokens.radius).forEach(([key, { value }]) => {
    cssVars.push(`  --radius-${key}: ${value};`);
  });
  
  // Fonts
  Object.entries(tokens.font).forEach(([key, { value }]) => {
    cssVars.push(`  --font-${key}: ${value};`);
  });
  
  // Font sizes
  Object.entries(tokens.fontSize).forEach(([key, { value }]) => {
    cssVars.push(`  --font-size-${key}: ${value};`);
  });
  
  // Spacing
  Object.entries(tokens.spacing).forEach(([key, { value }]) => {
    cssVars.push(`  --spacing-${key}: ${value};`);
  });
  
  // Shadows
  Object.entries(tokens.shadow).forEach(([key, { value }]) => {
    cssVars.push(`  --shadow-${key}: ${value};`);
  });
  
  return cssVars.join('\n');
}

export default tokens;

