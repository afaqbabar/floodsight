/**
 * FloodSight main entry point
 */

import { initSmoothScroll, initActiveNavLinks, initHeaderShadow, initMobileNav } from './nav.js';
import { initSignupForm } from './forms.js';
import { initCodeCopy, updateYear } from './utils.js';

// Initialize all modules when DOM is ready
function init() {
  // Navigation
  initSmoothScroll();
  initActiveNavLinks();
  initHeaderShadow();
  initMobileNav();

  // Forms
  initSignupForm();

  // Utilities
  initCodeCopy();
  updateYear();
}

// Run on DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
