/*
 * Til toppen — diskret centreret link i bunden af lange sider.
 *
 * Viser sig kun når dokumentet er væsentligt højere end viewporten
 * (mindst 1.4×). Indsættes inline i bunden af containeren, lige før
 * bottom-nav, så det får luftig vertikal afstand til både indhold ovenfor
 * og navigation nedenfor.
 *
 * Ved tap: smooth scroll til toppen.
 */
(function () {
  'use strict';

  var TROESKEL_HOEJDE = 1.4; // dokument skal være 1.4× viewport

  var btn = null;

  function byg() {
    if (btn) return;
    btn = document.createElement('button');
    btn.className = 'til-toppen';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Tilbage til toppen');
    btn.innerHTML =
      '<span class="til-toppen-tekst">tilbage til toppen</span>' +
      ' ' +
      '<span class="til-toppen-pil" aria-hidden="true">↑</span>';
    btn.addEventListener('click', function () {
      if (window.scrollTo) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      }
    });
  }

  function maaVises() {
    var dokHoejde = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight
    );
    return dokHoejde > window.innerHeight * TROESKEL_HOEJDE;
  }

  function indsaet() {
    if (!btn) byg();
    if (btn.parentNode) return; // allerede indsat
    // Indsæt lige før bottom-nav hvis den findes — ellers i bunden af body
    var nav = document.querySelector('.bottom-nav');
    if (nav && nav.parentNode) {
      nav.parentNode.insertBefore(btn, nav);
    } else {
      document.body.appendChild(btn);
    }
  }

  function fjern() {
    if (btn && btn.parentNode) {
      btn.parentNode.removeChild(btn);
    }
  }

  function tjek() {
    if (!document.body) return;
    if (maaVises()) indsaet();
    else fjern();
  }

  // Initial check + flere efter dynamisk render (sider rendrer indhold via fetch)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tjek);
  } else {
    tjek();
  }
  window.addEventListener('load', tjek);
  window.addEventListener('resize', tjek, { passive: true });
  setTimeout(tjek, 800);
  setTimeout(tjek, 2000);
})();
