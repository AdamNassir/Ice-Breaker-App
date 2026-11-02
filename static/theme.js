/* One persistent, user-controlled color theme across player, presenter and local editor. */
(() => {
  'use strict';
  const key = 'icebreaker:theme';
  function apply(value) {
    const midnight = value === 'midnight';
    document.documentElement.dataset.theme = midnight ? 'midnight' : 'light';
    document.querySelectorAll('.theme-toggle').forEach(button => {
      button.setAttribute('aria-pressed', String(midnight));
      button.setAttribute('aria-label', midnight ? 'Switch to light mode' : 'Switch to midnight mode');
      button.textContent = midnight ? 'Light mode' : 'Midnight mode';
    });
  }
  let initial = 'light';
  try { initial = localStorage.getItem(key) || 'light'; } catch { /* privacy mode */ }
  apply(initial);
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.querySelectorAll('.theme-toggle').forEach(button => {
      button.addEventListener('click', () => {
        const next = document.documentElement.dataset.theme === 'midnight' ? 'light' : 'midnight';
        try { localStorage.setItem(key, next); } catch { /* private mode */ }
        apply(next);
      });
    });
  });
  window.addEventListener('storage', event => { if (event.key === key) apply(event.newValue); });
})();
