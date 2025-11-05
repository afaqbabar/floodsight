#!/usr/bin/env node

/**
 * Build Metadata Generator
 * Generates health.json and version.txt with build information
 */

import { writeFileSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
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
const assetsDir = join(rootDir, 'public', 'assets');
try {
  mkdirSync(assetsDir, { recursive: true });
} catch (err) {
  // Directory might already exist, that's fine
}

// Write health.json
const healthJsonPath = join(assetsDir, 'health.json');
writeFileSync(healthJsonPath, JSON.stringify(metadata, null, 2), 'utf8');
console.log('✅ Generated:', healthJsonPath);

// Write version.txt (one-liner for easy curl checks)
const versionText = `${metadata.app} | commit:${metadata.commit.slice(0, 7)} | tag:${metadata.tag} | built:${metadata.builtAt}`;
const versionTxtPath = join(rootDir, 'public', 'version.txt');
writeFileSync(versionTxtPath, versionText + '\n', 'utf8');
console.log('✅ Generated:', versionTxtPath);

console.log('📦 Build metadata:', metadata);

