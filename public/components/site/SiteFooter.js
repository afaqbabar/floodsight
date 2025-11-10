/**
 * SiteFooter Component
 * Footer with legal links and cookie settings
 */

export function createSiteFooter() {
  return `
    <footer class="site-footer" role="contentinfo">
      <div class="container">
        <div class="footer__grid">
          <div class="footer__copy">
            <p class="small" style="margin: 0;">© ${new Date().getFullYear()} FloodSight. All rights reserved.</p>
          </div>
          <nav class="footer__nav" aria-label="Footer">
            <ul>
              <li><a href="/impressum.html">Impressum</a></li>
              <li><a href="/privacy.html">Privacy</a></li>
              <li><a href="/cookies.html">Cookies</a></li>
              <li><a href="#cookie-settings" class="js-cookie-settings">Cookie Settings</a></li>
            </ul>
          </nav>
        </div>
      </div>
    </footer>
  `;
}

/**
 * Initialize footer interactions
 */
export function initSiteFooter() {
  // Handle cookie settings button click
  const cookieSettingsBtn = document.querySelector('.js-cookie-settings');
  if (cookieSettingsBtn) {
    cookieSettingsBtn.addEventListener('click', (e) => {
      e.preventDefault();
      // This will be connected to the CookieBanner in Phase 3
      if (window.showCookieSettings) {
        window.showCookieSettings();
      } else {
        console.log('Cookie settings dialog will be available in Phase 3');
      }
    });
  }
}

