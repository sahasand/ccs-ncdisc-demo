/* =============================================================================
   HF-1002-CL-101 — Workflow Demo : router + accessible tab/toolbar behavior.
   Vanilla JS, no dependencies. show()/showTbl() are global (inline onclick hooks).
   Accessibility: roving tabindex + manual activation (arrows move focus only;
   Enter / Space / click activate). Deep-linkable via hash. No build step.
   ============================================================================= */
(function () {
  'use strict';

  var prefersReduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function tabs()  { return Array.prototype.slice.call(document.querySelectorAll('.tab')); }
  function plates(){ return Array.prototype.slice.call(document.querySelectorAll('.tt')); }
  function tabFor(id){ return document.querySelector('.tab[aria-controls="' + id + '"]'); }

  /* ---- Section router ----------------------------------------------------- */
  function show(id, btn) {
    var sec = document.getElementById(id);
    if (!sec) return;

    document.querySelectorAll('section').forEach(function (s) { s.classList.remove('on'); });
    sec.classList.add('on');

    tabs().forEach(function (t) {
      var active = t.getAttribute('aria-controls') === id;
      t.classList.toggle('on', active);
      t.setAttribute('aria-selected', active ? 'true' : 'false');
      t.tabIndex = active ? 0 : -1;
    });

    if ('#' + id !== location.hash) {
      history.pushState(null, '', '#' + id);
    }
    window.scrollTo({ top: 0, behavior: (btn && !prefersReduced) ? 'smooth' : 'auto' });
  }

  /* ---- TFL plate switcher ------------------------------------------------- */
  function showTbl(num, btn) {
    document.querySelectorAll('pre.tfl').forEach(function (p) { p.style.display = 'none'; });
    var target = document.getElementById('tbl-' + num);
    if (target) target.style.display = 'block';

    plates().forEach(function (b) {
      var active = b === btn || b.getAttribute('data-tbl') === num;
      b.classList.toggle('on', active);
      b.setAttribute('aria-pressed', active ? 'true' : 'false');
      b.tabIndex = active ? 0 : -1;
    });
  }

  window.show = show;
  window.showTbl = showTbl;

  /* ---- Roving-tabindex keyboard nav (focus only; never auto-activates) ---- */
  function rove(items, e) {
    var i = items.indexOf(document.activeElement);
    if (i < 0) return;
    var n = null;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': n = items[(i + 1) % items.length]; break;
      case 'ArrowLeft':  case 'ArrowUp':   n = items[(i - 1 + items.length) % items.length]; break;
      case 'Home': n = items[0]; break;
      case 'End':  n = items[items.length - 1]; break;
      default: return;
    }
    e.preventDefault();
    items.forEach(function (it) { it.tabIndex = -1; });
    n.tabIndex = 0;
    n.focus();
  }

  function wireGroup(container, getItems) {
    if (!container) return;
    container.addEventListener('keydown', function (e) { rove(getItems(), e); });
  }

  /* ---- Init --------------------------------------------------------------- */
  function init() {
    // Own the scroll position; the section router always lands at the top.
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

    // Programmatic links open safely.
    document.querySelectorAll('a.dl').forEach(function (a) { a.rel = 'noopener noreferrer'; });

    // Progressive a11y: column scope on derived-data tables.
    document.querySelectorAll('.data thead th').forEach(function (th) {
      if (!th.hasAttribute('scope')) th.setAttribute('scope', 'col');
    });

    wireGroup(document.querySelector('[role="tablist"]'), tabs);
    wireGroup(document.querySelector('.ttabs'), plates);

    window.addEventListener('hashchange', function () {
      var id = location.hash.slice(1) || 'overview';
      if (document.getElementById(id)) show(id);
    });

    var id = location.hash.slice(1);
    if (id && document.getElementById(id)) {
      show(id);
      // Counter the browser's native fragment jump so the masthead stays in view.
      requestAnimationFrame(function () { window.scrollTo(0, 0); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
