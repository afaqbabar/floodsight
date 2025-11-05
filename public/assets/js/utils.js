/**
 * Utility functions
 */

import { qs } from './dom.js';

/**
 * Initialize copy-to-clipboard for code samples
 */
export function initCodeCopy() {
  const code = qs('.code-sample');
  if (!code) return;

  const copyBtn = document.createElement('button');
  copyBtn.className = 'btn btn--ghost';
  copyBtn.textContent = 'Copy';
  copyBtn.style.float = 'right';

  copyBtn.addEventListener('click', async () => {
    try {
      const text = code.innerText.trim();
      await navigator.clipboard.writeText(text);
      copyBtn.textContent = 'Copied!';
      setTimeout(() => (copyBtn.textContent = 'Copy'), 1200);
    } catch (_) {
      // Clipboard API not available
    }
  });

  code.parentElement?.insertBefore(copyBtn, code);
}

/**
 * Update footer year dynamically
 */
export function updateYear() {
  const el = qs('[data-year]');
  if (el) el.textContent = new Date().getFullYear().toString();
}

