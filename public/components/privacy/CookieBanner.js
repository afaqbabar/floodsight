/**
 * CookieBanner Component
 * GDPR-compliant cookie consent banner with category selection
 */

import {
  getConsent,
  saveConsent,
  shouldShowConsentBanner,
  ConsentCategories,
} from '/lib/consent.js';

const bannerHTML = `
<div class="cookie-banner" id="cookie-banner" role="dialog" aria-labelledby="cookie-banner-title" aria-modal="true">
  <div class="cookie-banner__content">
    <div class="cookie-banner__header">
      <h2 id="cookie-banner-title" class="cookie-banner__title">Cookie Preferences</h2>
      <p class="cookie-banner__description">
        We use cookies to improve your experience and analyze site usage. 
        You can choose which types of cookies to allow.
      </p>
    </div>

    <div class="cookie-banner__categories">
      <!-- Necessary (always on) -->
      <label class="cookie-category">
        <div class="cookie-category__header">
          <input type="checkbox" checked disabled />
          <div>
            <strong>Necessary</strong>
            <p class="cookie-category__desc">Required for the site to function properly</p>
          </div>
        </div>
      </label>

      <!-- Preferences -->
      <label class="cookie-category">
        <div class="cookie-category__header">
          <input type="checkbox" id="consent-preferences" />
          <div>
            <strong>Preferences</strong>
            <p class="cookie-category__desc">Remember your settings and preferences</p>
          </div>
        </div>
      </label>

      <!-- Analytics -->
      <label class="cookie-category">
        <div class="cookie-category__header">
          <input type="checkbox" id="consent-analytics" />
          <div>
            <strong>Analytics</strong>
            <p class="cookie-category__desc">Help us understand how you use our site</p>
          </div>
        </div>
      </label>

      <!-- Marketing -->
      <label class="cookie-category">
        <div class="cookie-category__header">
          <input type="checkbox" id="consent-marketing" />
          <div>
            <strong>Marketing</strong>
            <p class="cookie-category__desc">Show relevant ads and content</p>
          </div>
        </div>
      </label>
    </div>

    <div class="cookie-banner__actions">
      <button class="btn btn--ghost" id="cookie-reject">Reject All</button>
      <button class="btn btn--ghost" id="cookie-save">Save Preferences</button>
      <button class="btn btn--primary" id="cookie-accept-all">Accept All</button>
    </div>

    <div class="cookie-banner__links">
      <a href="/privacy.html">Privacy Policy</a>
      <span>·</span>
      <a href="/cookies.html">Cookie Policy</a>
    </div>
  </div>
</div>
`;

/**
 * Show the cookie banner
 */
export function showCookieBanner() {
  // Check if banner already exists
  if (document.getElementById('cookie-banner')) {
    return;
  }

  // Inject banner HTML
  const container = document.createElement('div');
  container.innerHTML = bannerHTML;
  document.body.appendChild(container.firstElementChild);

  // Add event listeners
  document.getElementById('cookie-accept-all').addEventListener('click', handleAcceptAll);
  document.getElementById('cookie-reject').addEventListener('click', handleReject);
  document.getElementById('cookie-save').addEventListener('click', handleSave);

  console.log('🍪 Cookie banner displayed');
}

/**
 * Hide the cookie banner
 */
export function hideCookieBanner() {
  const banner = document.getElementById('cookie-banner');
  if (banner) {
    banner.style.display = 'none';
    setTimeout(() => banner.remove(), 300);
  }
}

/**
 * Handle "Accept All" button
 */
function handleAcceptAll() {
  saveConsent({
    necessary: true,
    preferences: true,
    analytics: true,
    marketing: true,
  });
  hideCookieBanner();
}

/**
 * Handle "Reject All" button
 */
function handleReject() {
  saveConsent({
    necessary: true,
    preferences: false,
    analytics: false,
    marketing: false,
  });
  hideCookieBanner();
}

/**
 * Handle "Save Preferences" button
 */
function handleSave() {
  const preferences = document.getElementById('consent-preferences').checked;
  const analytics = document.getElementById('consent-analytics').checked;
  const marketing = document.getElementById('consent-marketing').checked;

  saveConsent({
    necessary: true,
    preferences,
    analytics,
    marketing,
  });
  hideCookieBanner();
}

/**
 * Initialize cookie banner (show if needed)
 */
export function initCookieBanner() {
  if (shouldShowConsentBanner()) {
    // Small delay to ensure page is fully loaded
    setTimeout(() => {
      showCookieBanner();
    }, 500);
  }
}

/**
 * Expose showCookieBanner globally for "Change cookie settings" link
 */
if (typeof window !== 'undefined') {
  window.showCookieSettings = showCookieBanner;
}
