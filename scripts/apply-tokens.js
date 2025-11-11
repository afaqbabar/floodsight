/**
 * Apply design tokens to CSS
 * This script generates CSS variables from figma-tokens.json
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');

// Read tokens
const tokensPath = join(rootDir, 'design', 'figma-tokens.json');
const tokens = JSON.parse(readFileSync(tokensPath, 'utf-8'));

// Generate CSS variables
let cssVars = ':root {\n  /* Design Tokens - Auto-generated from figma-tokens.json */\n';

// Colors
cssVars += '\n  /* Colors */\n';
Object.entries(tokens.color).forEach(([key, { value }]) => {
  cssVars += `  --color-${key}: ${value};\n`;
});

// Radius
cssVars += '\n  /* Border Radius */\n';
Object.entries(tokens.radius).forEach(([key, { value }]) => {
  cssVars += `  --radius-${key}: ${value};\n`;
});

// Fonts
cssVars += '\n  /* Fonts */\n';
Object.entries(tokens.font).forEach(([key, { value }]) => {
  cssVars += `  --font-${key}: ${value};\n`;
});

// Font sizes
cssVars += '\n  /* Font Sizes */\n';
Object.entries(tokens.fontSize).forEach(([key, { value }]) => {
  cssVars += `  --font-size-${key}: ${value};\n`;
});

// Spacing
cssVars += '\n  /* Spacing */\n';
Object.entries(tokens.spacing).forEach(([key, { value }]) => {
  cssVars += `  --spacing-${key}: ${value};\n`;
});

// Shadows
cssVars += '\n  /* Shadows */\n';
Object.entries(tokens.shadow).forEach(([key, { value }]) => {
  cssVars += `  --shadow-${key}: ${value};\n`;
});

cssVars += '}\n';

// Write to a separate tokens CSS file
const tokensOutputPath = join(rootDir, 'public', 'assets', 'css', 'tokens.css');
writeFileSync(tokensOutputPath, cssVars);

console.log('✅ Design tokens applied to', tokensOutputPath);
console.log('   Import this file in your main CSS or HTML.');
