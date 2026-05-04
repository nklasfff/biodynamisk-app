/*
 * Onboarding — 3-skærms stemningssætter der vises ved første besøg.
 *
 * Hver skærm har et fuldskærms-billede som baggrund og en kort tekst
 * placeret over. Brugeren tapper sig gennem de tre skærme — eller kan
 * springe over med et lille link i hjørnet.
 *
 * Når sekvensen er gennemført eller sprunget over, gemmes en flag i
 * localStorage så onboarding ikke vises igen.
 *
 * Inkluderes på index.html (hjemskærmen). Kører kun ved første launch.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'biodynamisk-onboarding-vist';

  var SKAERME = [
    {
      billede: 'onboard_1.png',
      tekst: 'velkommen'
    },
    {
      billede: 'onboard_2.png',
      tekst: 'En model er en levende proces.<br>Principperne er den røde tråd — udtrykkene varierer fra behandler til behandler, fra skole til skole.'
    },
    {
      billede: 'onboard_3.png',
      tekst: 'træd ind, når du er klar'
    }
  ];

  var state = {
    overlay: null,
    aktivIndex: 0,
    keydownHandler: null,
    touchStartX: null,
    touchStartY: null
  };

  function harSetOnboarding() {
    try {
      return localStorage.getItem(STORAGE_KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function gemSetOnboarding() {
    try {
      localStorage.setItem(STORAGE_KEY, '1');
    } catch (e) {}
  }

  function bygOverlay() {
    if (state.overlay) return state.overlay;

    var overlay = document.createElement('div');
    overlay.className = 'onboarding';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Velkommen');

    overlay.innerHTML =
      '<div class="onboarding-billede"></div>' +
      '<div class="onboarding-overlay-shade"></div>' +
      '<button class="onboarding-spring" type="button">spring over</button>' +
      '<div class="onboarding-indhold">' +
        '<p class="onboarding-tekst"></p>' +
      '</div>' +
      '<div class="onboarding-bund">' +
        '<button class="onboarding-tilbage" type="button" aria-label="Forrige">‹</button>' +
        '<div class="onboarding-progress"></div>' +
        '<button class="onboarding-naeste" type="button">videre ›</button>' +
      '</div>';

    document.body.appendChild(overlay);

    overlay.querySelector('.onboarding-spring').addEventListener('click', luk);
    overlay.querySelector('.onboarding-naeste').addEventListener('click', naeste);
    overlay.querySelector('.onboarding-tilbage').addEventListener('click', tilbage);

    overlay.addEventListener('touchstart', onTouchStart, { passive: true });
    overlay.addEventListener('touchend', onTouchEnd, { passive: true });

    state.overlay = overlay;
    return overlay;
  }

  function onTouchStart(e) {
    if (!e.touches || !e.touches.length) return;
    state.touchStartX = e.touches[0].clientX;
    state.touchStartY = e.touches[0].clientY;
  }

  function onTouchEnd(e) {
    if (state.touchStartX === null) return;
    var t = (e.changedTouches && e.changedTouches[0]) || null;
    if (!t) { state.touchStartX = null; return; }
    var dx = t.clientX - state.touchStartX;
    var dy = t.clientY - state.touchStartY;
    state.touchStartX = null;
    state.touchStartY = null;
    if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy)) return;
    if (dx < 0) naeste();
    else tilbage();
  }

  function render() {
    var overlay = state.overlay;
    if (!overlay) return;

    var i = state.aktivIndex;
    var skaerm = SKAERME[i];
    var sidste = i === SKAERME.length - 1;

    var billedeEl = overlay.querySelector('.onboarding-billede');
    billedeEl.style.backgroundImage = "url('" + skaerm.billede + "')";

    // Fade i tekst-skift
    var tekstEl = overlay.querySelector('.onboarding-tekst');
    tekstEl.classList.remove('onboarding-tekst-vist');
    void tekstEl.offsetWidth;
    tekstEl.innerHTML = skaerm.tekst;
    tekstEl.classList.add('onboarding-tekst-vist');

    // Progress
    var progressEl = overlay.querySelector('.onboarding-progress');
    var dots = '';
    for (var k = 0; k < SKAERME.length; k++) {
      dots += '<span class="onboarding-dot' + (k === i ? ' aktiv' : '') + '"></span>';
    }
    progressEl.innerHTML = dots;

    // Navigation
    var tilbageBtn = overlay.querySelector('.onboarding-tilbage');
    var naesteBtn = overlay.querySelector('.onboarding-naeste');
    tilbageBtn.style.visibility = i > 0 ? 'visible' : 'hidden';
    naesteBtn.textContent = sidste ? 'træd ind' : 'videre ›';

    // Sidste skærm: skjul "spring over" — det er nu unødvendigt
    var springEl = overlay.querySelector('.onboarding-spring');
    springEl.style.visibility = sidste ? 'hidden' : 'visible';
  }

  function naeste() {
    if (state.aktivIndex >= SKAERME.length - 1) {
      luk();
      return;
    }
    state.aktivIndex++;
    render();
  }

  function tilbage() {
    if (state.aktivIndex <= 0) return;
    state.aktivIndex--;
    render();
  }

  function aabn() {
    var overlay = bygOverlay();
    state.aktivIndex = 0;
    document.body.classList.add('onboarding-aaben');
    overlay.classList.add('aaben');
    render();

    state.keydownHandler = function (e) {
      if (e.key === 'Escape') { e.preventDefault(); luk(); }
      else if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); naeste(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); tilbage(); }
    };
    document.addEventListener('keydown', state.keydownHandler);
  }

  function luk() {
    gemSetOnboarding();
    var overlay = state.overlay;
    if (!overlay) return;
    overlay.classList.remove('aaben');
    document.body.classList.remove('onboarding-aaben');
    if (state.keydownHandler) {
      document.removeEventListener('keydown', state.keydownHandler);
      state.keydownHandler = null;
    }
    // Fjern fra DOM efter fade-ud
    setTimeout(function () {
      if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
      state.overlay = null;
    }, 500);
  }

  // Eksporter til debug/manuelt brug — fx hvis brugeren vil se onboarding igen
  window.Onboarding = {
    aabn: aabn,
    luk: luk,
    nulstil: function () {
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
    }
  };

  // Auto-init: vis onboarding ved første besøg
  function init() {
    if (harSetOnboarding()) return;
    aabn();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
