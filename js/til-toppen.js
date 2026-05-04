/*
 * Til toppen — diskret floating knap der lader brugeren scrolle hurtigt
 * tilbage til toppen på lange sider.
 *
 * Knappen vises kun når:
 *   - dokumentet er væsentligt højere end viewporten (mindst 1.4×)
 *   - brugeren har scrollet > 400px ned
 *
 * Ved tap: smooth scroll til toppen.
 *
 * Auto-init på alle sider der inkluderer scriptet.
 */
(function () {
  'use strict';

  var TROESKEL_SCROLL = 400;
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
      '<span class="til-toppen-pil" aria-hidden="true">↑</span>';
    btn.addEventListener('click', function () {
      if (window.scrollTo) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
      }
    });
    document.body.appendChild(btn);
  }

  function maaVises() {
    var dokHoejde = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight
    );
    return dokHoejde > window.innerHeight * TROESKEL_HOEJDE;
  }

  function tjek() {
    if (!document.body) return;
    if (!maaVises()) {
      if (btn) btn.classList.remove('synlig');
      return;
    }
    byg();
    if ((window.scrollY || window.pageYOffset) > TROESKEL_SCROLL) {
      btn.classList.add('synlig');
    } else {
      btn.classList.remove('synlig');
    }
  }

  // Throttled scroll-handler via rAF
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      tjek();
      ticking = false;
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });

  // Initial check + flere efter dynamisk render
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tjek);
  } else {
    tjek();
  }
  window.addEventListener('load', tjek);
  // Sider rendrer indhold asynkront via fetch — re-tjek efter de typiske
  // tidspunkter hvor indholdet er klart
  setTimeout(tjek, 800);
  setTimeout(tjek, 2000);
})();
