/**
 * Form validation and handling
 */

import { qs } from './dom.js';

/**
 * Initialize signup form validation
 */
export function initSignupForm() {
  const form = qs('#signup .form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const name = qs('#name', form);
    const email = qs('#email', form);

    const errors = [];
    const emailOk = /.+@.+\..+/.test(email.value.trim());
    if (!name.value.trim()) errors.push('Name is required.');
    if (!emailOk) errors.push('Please enter a valid email.');

    if (errors.length) {
      e.preventDefault();
      showFormNote(form, 'error', errors.join(' '));
      return;
    }

    // Form will submit to Formspree
  });
}

/**
 * Show form validation message
 */
function showFormNote(form, type, msg) {
  let note = qs('.form-note', form);
  if (!note) {
    note = document.createElement('div');
    note.className = 'form-note';
    note.style.marginTop = '8px';
    note.style.padding = '10px 12px';
    note.style.borderRadius = '10px';
    note.style.border = '1px solid var(--border)';
    note.style.background = type === 'error' ? '#3b1117' : '#12361f';
    form.appendChild(note);
  }
  note.textContent = msg;
}

