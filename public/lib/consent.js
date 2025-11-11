/**
 * Consent Management Library
 * Handles cookie consent and analytics gating for GDPR compliance
 */

const CONSENT_COOKIE_NAME = 'fs_consent';
const CONSENT_VERSION = 'v1';
const CONSENT_EXPIRY_DAYS = 365;

/**
 * Consent categories
 */
export const ConsentCategories = {
  NECESSARY: 'necessary',
  PREFERENCES: 'preferences',
  ANALYTICS: 'analytics',
  MARKETING: 'marketing',
};

/**
 * Get current consent preferences
 * @returns {Object} Consent object with categories
 */
export function getConsent() {
  const cookie = getCookie(CONSENT_COOKIE_NAME);
  if (!cookie) {
    return null;
  }

  try {
    const [version, ...categories] = cookie.split('.');
    if (version !== CONSENT_VERSION) {
      return null;
    }

    return {
      version,
      necessary: true, // Always true
      preferences: categories.includes(ConsentCategories.PREFERENCES),
      analytics: categories.includes(ConsentCategories.ANALYTICS),
      marketing: categories.includes(ConsentCategories.MARKETING),
      timestamp: Date.now(),
    };
  } catch (e) {
    console.error('Failed to parse consent cookie:', e);
    return null;
  }
}

/**
 * Save consent preferences
 * @param {Object} preferences - Object with boolean values for each category
 */
export function saveConsent(preferences) {
  const categories = [CONSENT_VERSION];

  // Necessary is always included
  categories.push(ConsentCategories.NECESSARY);

  if (preferences.preferences) {
    categories.push(ConsentCategories.PREFERENCES);
  }
  if (preferences.analytics) {
    categories.push(ConsentCategories.ANALYTICS);
  }
  if (preferences.marketing) {
    categories.push(ConsentCategories.MARKETING);
  }

  const cookieValue = categories.join('.');
  setCookie(CONSENT_COOKIE_NAME, cookieValue, CONSENT_EXPIRY_DAYS);

  // Trigger analytics initialization if consent is given
  if (preferences.analytics) {
    initAnalytics();
  }

  // Dispatch custom event for other scripts to react
  window.dispatchEvent(
    new CustomEvent('consentUpdated', {
      detail: preferences,
    })
  );

  console.log('✅ Consent saved:', preferences);
}

/**
 * Check if a specific category is consented
 * @param {string} category - Category to check
 * @returns {boolean}
 */
export function hasConsent(category) {
  const consent = getConsent();
  if (!consent) {
    return false;
  }
  return consent[category] === true;
}

/**
 * Clear all consent preferences
 */
export function clearConsent() {
  deleteCookie(CONSENT_COOKIE_NAME);
  console.log('🗑️ Consent cleared');
}

/**
 * Initialize analytics if consent is given
 */
function initAnalytics() {
  if (!hasConsent(ConsentCategories.ANALYTICS)) {
    console.log('⚠️ Analytics blocked: No consent');
    return;
  }

  // Initialize Google Analytics (example)
  // Only loads if analytics consent is given
  console.log('📊 Analytics initialized');

  // Example: Load Google Analytics
  // window.dataLayer = window.dataLayer || [];
  // function gtag(){dataLayer.push(arguments);}
  // gtag('js', new Date());
  // gtag('config', 'G-XXXXXXXXXX');
}

/**
 * Cookie utility functions
 */
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

function setCookie(name, value, days) {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function deleteCookie(name) {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

/**
 * Check if consent banner should be shown
 * @returns {boolean}
 */
export function shouldShowConsentBanner() {
  return getConsent() === null;
}

// Initialize analytics on load if consent already exists
if (typeof window !== 'undefined') {
  const consent = getConsent();
  if (consent && consent.analytics) {
    initAnalytics();
  }
}
