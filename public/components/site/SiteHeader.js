/**
 * SiteHeader Component
 * Reusable header with FloodSight branding, navigation, and CTA
 */

export function createSiteHeader() {
  return `
    <header id="top" class="site-header" role="banner" aria-label="Main">
      <div class="container">
        <div class="brand">
          <a class="brand__link" href="/" aria-label="FloodSight home">
            <svg class="brand__logo" width="32" height="32" viewBox="0 0 24 24" role="img" aria-label="FloodSight logo">
              <path fill="currentColor" d="M12 3c3 3.6 6 5.4 9 5.4-1.8 3-4.2 5.4-9 12C7.2 13.8 4.8 11.4 3 8.4 6 8.4 9 6.6 12 3z"/>
            </svg>
            <span class="brand__name">FloodSight</span>
          </a>
        </div>
        <nav class="nav" aria-label="Primary">
          <ul class="nav__list">
            <li><a href="/dashboard.html">Dashboard</a></li>
            <li><a href="#alerts">Alerts</a></li>
            <li><a href="/#features">Features</a></li>
            <li><a href="/#pricing">Pricing</a></li>
            <li><a href="#about">About</a></li>
          </ul>
        </nav>
        <div class="cta">
          <a class="btn btn--primary" href="#create-alert">Create Alert</a>
        </div>
      </div>
    </header>
  `;
}

/**
 * Initialize the header (if needed for dynamic behavior)
 */
export function initSiteHeader() {
  // Add any interactive behavior here (e.g., mobile menu toggle)
  console.log('SiteHeader initialized');
}

