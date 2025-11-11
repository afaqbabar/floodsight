/* FloodSight JS: smooth scroll, mobile nav toggle, form validation */
(function () {
  const qs = (s, r = document) => r.querySelector(s);
  const qsa = (s, r = document) => Array.from(r.querySelectorAll(s));

  // ---- Smooth scrolling for in-page links ----
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

  // ---- Active nav link on scroll ----
  const navLinks = qsa('.nav__list a[href^="#"]').map((el) => ({
    el,
    id: el.getAttribute('href'),
  }));
  const sections = navLinks.map(({ id }) => ({ id, el: qs(id) })).filter((s) => s.el);

  const setActive = () => {
    const fromTop = window.scrollY + 100; // offset for sticky header
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

  // ---- Header shadow when scrolled ----
  const header = qs('.site-header');
  const setShadow = () => {
    if (!header) return;
    header.classList.toggle('has-shadow', window.scrollY > 8);
  };
  window.addEventListener('scroll', setShadow, { passive: true });
  setShadow();

  // ---- Mobile nav toggle (inserts a button on small screens) ----
  const nav = qs('.nav');
  const cta = qs('.cta');
  if (nav && cta) {
    const btn = document.createElement('button');
    btn.className = 'btn btn--ghost nav-toggle';
    btn.setAttribute('aria-label', 'Toggle navigation');
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = 'Menu';
    // Insert button before CTA on small screens
    const headerGrid = header?.querySelector('.container');
    if (headerGrid) headerGrid.insertBefore(btn, cta);

    const toggleNav = () => {
      const open = btn.getAttribute('aria-expanded') === 'true';
      const next = !open;
      btn.setAttribute('aria-expanded', String(next));
      // Inline style toggle to override small-screen CSS that hides .nav
      if (window.matchMedia('(max-width: 640px)').matches) {
        nav.style.display = next ? 'block' : 'none';
      }
    };

    btn.addEventListener('click', toggleNav);
    // Ensure correct initial state on load/resize
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

  // ---- Demo code: copy-to-clipboard for code sample (if present) ----
  const code = qs('.code-sample');
  if (code) {
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
        // Clipboard API not available or permission denied
      }
    });
    code.parentElement?.insertBefore(copyBtn, code);
  }

  // ---- Signup form: basic client-side validation ----
  const form = qs('#signup .form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      const name = qs('#name', form);
      const email = qs('#email', form);
      // Minimal checks
      const errors = [];
      const emailOk = /.+@.+\..+/.test(email.value.trim());
      if (!name.value.trim()) errors.push('Name is required.');
      if (!emailOk) errors.push('Please enter a valid email.');

      if (errors.length) {
        e.preventDefault();
        showFormNote('error', errors.join(' '));
        return;
      }

      // Optional: prevent actual submit during prototype
      // e.preventDefault();
      // await new Promise(r => setTimeout(r, 400));
      // showFormNote('success', 'Thanks! We\'ll be in touch soon.');
      // form.reset();
    });

    const showFormNote = (type, msg) => {
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
    };
  }
})();
