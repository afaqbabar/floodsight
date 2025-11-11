/**
 * Navigation module: smooth scroll, active links, mobile toggle, header effects
 */

import { qs, qsa } from './dom.js';

/**
 * Initialize smooth scrolling for anchor links
 */
export function initSmoothScroll() {
  qsa('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = qs(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.pushState(null, '', id);
    });
  });
}

/**
 * Highlight active nav link based on scroll position
 */
export function initActiveNavLinks() {
  const navLinks = qsa('.nav__list a[href^="#"]').map((el) => ({
    el,
    id: el.getAttribute('href'),
  }));
  const sections = navLinks.map(({ id }) => ({ id, el: qs(id) })).filter((s) => s.el);

  const setActive = () => {
    const fromTop = window.scrollY + 100;
    let current = null;
    for (const s of sections) {
      const top = s.el.offsetTop;
      if (fromTop >= top) current = s.id;
    }
    navLinks.forEach(({ el, id }) => {
      if (id === current) el.classList.add('is-active');
      else el.classList.remove('is-active');
    });
  };

  window.addEventListener('scroll', setActive, { passive: true });
  setActive();
}

/**
 * Add shadow to header when scrolled
 */
export function initHeaderShadow() {
  const header = qs('.site-header');
  if (!header) return;

  const setShadow = () => {
    header.classList.toggle('has-shadow', window.scrollY > 8);
  };

  window.addEventListener('scroll', setShadow, { passive: true });
  setShadow();
}

/**
 * Initialize mobile navigation toggle
 */
export function initMobileNav() {
  const nav = qs('.nav');
  const cta = qs('.cta');
  const header = qs('.site-header');

  if (!nav || !cta || !header) return;

  const btn = document.createElement('button');
  btn.className = 'btn btn--ghost nav-toggle';
  btn.setAttribute('aria-label', 'Toggle navigation');
  btn.setAttribute('aria-expanded', 'false');
  btn.textContent = 'Menu';

  const headerGrid = header.querySelector('.container');
  if (headerGrid) headerGrid.insertBefore(btn, cta);

  const toggleNav = () => {
    const open = btn.getAttribute('aria-expanded') === 'true';
    const next = !open;
    btn.setAttribute('aria-expanded', String(next));
    if (window.matchMedia('(max-width: 640px)').matches) {
      nav.style.display = next ? 'block' : 'none';
    }
  };

  btn.addEventListener('click', toggleNav);

  const syncNav = () => {
    if (window.matchMedia('(max-width: 640px)').matches) {
      nav.style.display = 'none';
      btn.style.display = 'inline-flex';
    } else {
      nav.style.display = '';
      btn.style.display = 'none';
      btn.setAttribute('aria-expanded', 'false');
    }
  };

  window.addEventListener('resize', syncNav);
  syncNav();
}
