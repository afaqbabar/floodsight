import { resolve } from 'node:path';

export default {
  root: 'public',         // HTML files now in public/ directory
  base: './',             // keep relative paths for nginx or any hosting
  publicDir: false,       // disable default public handling since we're using it as root
  build: {
    outDir: '../dist',    // output relative to public/ (back to repo root then dist)
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'public/index.html'),
        impressum: resolve(__dirname, 'public/impressum.html'),
        privacy: resolve(__dirname, 'public/privacy.html'),
        terms: resolve(__dirname, 'public/terms.html'),
        security: resolve(__dirname, 'public/security.html'),
        thanks: resolve(__dirname, 'public/thanks.html'),
        '404': resolve(__dirname, 'public/404.html'),
        'verify-assets': resolve(__dirname, 'public/verify-assets.html'),
        'google5b12900a10441c99': resolve(__dirname, 'public/google5b12900a10441c99.html')
      }
    }
  },
  server: {
    port: 5173,
    open: false
  }
};

