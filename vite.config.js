import { resolve } from 'node:path';

export default {
  root: '.',              // project root is repository root
  base: './',             // keep relative paths for nginx or any hosting
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        impressum: resolve(__dirname, 'impressum.html'),
        privacy: resolve(__dirname, 'privacy.html'),
        terms: resolve(__dirname, 'terms.html'),
        security: resolve(__dirname, 'security.html'),
        thanks: resolve(__dirname, 'thanks.html'),
        '404': resolve(__dirname, '404.html'),
        'verify-assets': resolve(__dirname, 'verify-assets.html'),
        'google5b12900a10441c99': resolve(__dirname, 'google5b12900a10441c99.html')
      }
    }
  },
  server: {
    port: 5173,
    open: false
  }
};

