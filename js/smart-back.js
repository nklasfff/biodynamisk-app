// js/smart-back.js
// Smart back-knap: når brugeren ankommer til en detalje-side fra en ANDEN
// detalje-side (typisk via en relation-henvisning), bør tilbage-knappen
// føre tilbage dertil — ikke til den faste liste-side.
//
// Heuristik: hvis document.referrer er en intern side med `?id=` i URL'en,
// betragter vi den som "deep" og bruger history.back() med label "Tilbage".
// Ellers bevares den oprindelige back-btn (typisk pegende på en liste).

window.SmartBack = (function() {
  'use strict';

  function cameFromDeepPage() {
    const ref = document.referrer;
    if (!ref) return false;
    try {
      const url = new URL(ref);
      if (url.origin !== window.location.origin) return false;
      // Detalje-sider har et `?id=` parameter (begreb, zone, stadie, kapitel)
      // ELLER er rummene-helhed.html som er en dedikeret detalje-side
      const path = url.pathname.split('/').pop();
      if (path === 'rummene-helhed.html') return true;
      return url.searchParams.has('id');
    } catch (e) {
      return false;
    }
  }

  function apply() {
    if (!cameFromDeepPage()) return;
    const btn = document.querySelector('.back-btn');
    if (!btn) return;
    btn.textContent = '‹ Tilbage';
    btn.setAttribute('onclick', 'history.back(); return false;');
  }

  return { apply, cameFromDeepPage };
})();
