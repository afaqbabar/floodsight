#!/usr/bin/env node

/**
 * Build Metadata Generator
 * Generates health.json and version.txt with build information
 * Outputs to public/ folder so Vite includes them in dist/
 */

import { writeFileSync, mkdirSync } from 'fs';
import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');

// Build metadata
const metadata = {
  status: 'ok',
  app: 'floodsight',
  commit: process.env.GIT_SHA || process.env.GITHUB_SHA || '',
  tag: process.env.GIT_TAG || '',
  branch: process.env.GIT_BRANCH || 'main',
  image: process.env.IMAGE_REF || '',
  builtAt: new Date().toISOString()
};

// Ensure public/assets directory exists
const assetsDir = resolve(rootDir, 'public', 'assets');
mkdirSync(assetsDir, { recursive: true });

// Write health.json to public/assets/
const healthJsonPath = join(assetsDir, 'health.json');
writeFileSync(healthJsonPath, JSON.stringify(metadata, null, 2), 'utf8');
console.log('✅ Generated:', healthJsonPath);

// Write version.txt to public/
const versionText = `commit=${metadata.commit.slice(0, 7)} tag=${metadata.tag} builtAt=${metadata.builtAt}`;
const versionTxtPath = resolve(rootDir, 'public', 'version.txt');
writeFileSync(versionTxtPath, versionText + '\n', 'utf8');
console.log('✅ Generated:', versionTxtPath);

console.log('📦 Build metadata:', metadata);

