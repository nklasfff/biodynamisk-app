/*
 * Refleksions-rum — fuldskærms-overlay der viser ét refleksionsspørgsmål ad gangen.
 *
 * Brug:
 *   RefleksionsRum.aabn({
 *     spoergsmaal: ['Har du oplevet …?', 'Hvordan adskilte …?'],
 *     kilde: 'Dynamisk stilhed'   // valgfri — vises diskret som kontekst
 *   });
 *
 * Hjælper:
 *   RefleksionsRum.splitMarkdown(markdown)
 *     → tager rå markdown fra '## Til refleksion'-sektionen og returnerer
 *       et array af spørgsmål (afsnits-baseret split).
 *
 * Render-hjælper:
 *   RefleksionsRum.triggerHTML({ spoergsmaal, kilde, label })
 *     → genererer HTML for "Gå til refleksion"-knappen som siderne kan indsætte.
 *
 * Komponenten er genbrugelig — én singleton overlay deles mellem alle sider.
 */
(function () {
  'use strict';

  // Split markdown-indhold til en liste af spørgsmål.
  // Hvert ikke-tomt afsnit (adskilt af blank linje) bliver ét spørgsmål.
  // Stripper ledende ### overskrifter, så subsections som
  // '### Refleksioner over øvelsen' ikke bliver til et spørgsmål.
  function splitMarkdown(markdown) {
    if (!markdown) return [];
    return markdown
      .split(/\n\s*\n/)
      .map(function (afsnit) { return afsnit.trim(); })
      .filter(function (afsnit) {
        if (!afsnit) return false;
        // Skip rene ###-overskrifter (én linje der kun er en markdown-heading)
        if (/^#{1,6}\s+.+$/.test(afsnit) && afsnit.indexOf('\n') === -1) return false;
        return true;
      })
      .map(function (afsnit) {
        // Hvis afsnit starter med en heading-linje fulgt af mere tekst,
        // fjern selve heading-linjen og behold resten
        return afsnit.replace(/^#{1,6}\s+.*\n+/, '').trim();
      })
      .filter(function (afsnit) { return afsnit.length > 0; });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Tæl samlet antal spørgsmål på tværs af grupper
  function antalIGrupper(grupper) {
    var n = 0;
    for (var i = 0; i < grupper.length; i++) {
      n += (grupper[i].spoergsmaal || []).length;
    }
    return n;
  }

  // Generér HTML for en "Gå til refleksion"-trigger som sider kan indsætte
  // i deres render-output. Klik-handleren læser data-attributter og åbner overlayet.
  //
  // Accepterer enten:
  //   { spoergsmaal: ['q1', 'q2'], kilde: 'X' }    — flad liste
  //   { grupper: [{ titel, spoergsmaal: [...] }] } — gruppe-baseret med skiftende overskrift
  function triggerHTML(opts) {
    opts = opts || {};
    var label = opts.label || 'Gå til refleksion';

    var antal = 0;
    var dataAttrs = '';
    if (opts.grupper && opts.grupper.length) {
      antal = antalIGrupper(opts.grupper);
      if (!antal) return '';
      dataAttrs = 'data-grupper="' + escapeHtml(JSON.stringify(opts.grupper)) + '"';
    } else {
      var spoergsmaal = opts.spoergsmaal || [];
      if (!spoergsmaal.length) return '';
      antal = spoergsmaal.length;
      dataAttrs =
        'data-spoergsmaal="' + escapeHtml(JSON.stringify(spoergsmaal)) + '" ' +
        'data-kilde="' + escapeHtml(opts.kilde || '') + '"';
    }

    var meta = 'giv dig tid — lad svarene vise sig af sig selv';

    return (
      '<button class="refleksion-trigger" type="button" ' + dataAttrs + ' ' +
        'onclick="RefleksionsRum.aabnFraTrigger(this)">' +
        '<span class="refleksion-trigger-rune" aria-hidden="true">◆</span>' +
        '<span class="refleksion-trigger-label">' + escapeHtml(label) + '</span>' +
        '<span class="refleksion-trigger-meta">' + escapeHtml(meta) + '</span>' +
      '</button>'
    );
  }

  // Singleton-state for overlayet
  var state = {
    overlay: null,
    aktivIndex: 0,
    spoergsmaal: [],
    kilde: '',
    forrigScroll: 0,
    keydownHandler: null,
    touchStartX: null,
    touchStartY: null,
    skiftRetning: 'frem' // 'frem' | 'tilbage' — for animation
  };

  function bygOverlay() {
    if (state.overlay) return state.overlay;

    var overlay = document.createElement('div');
    overlay.className = 'refleksions-rum';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Refleksion');
    overlay.innerHTML = (
      '<div class="refleksions-rum-indhold">' +
        '<div class="refleksions-rum-kilde"></div>' +
        '<div class="refleksions-rum-rune" aria-hidden="true">◆</div>' +
        '<div class="refleksions-rum-tekst-wrap">' +
          '<p class="refleksions-rum-tekst"></p>' +
        '</div>' +
        '<div class="refleksions-rum-progress"></div>' +
        '<div class="refleksions-rum-nav">' +
          '<button class="refleksions-rum-tilbage" type="button">‹ Forrige</button>' +
          '<button class="refleksions-rum-naeste" type="button">Næste ›</button>' +
          '<button class="refleksions-rum-luk" type="button" aria-label="Luk refleksion">luk</button>' +
        '</div>' +
      '</div>'
    );

    document.body.appendChild(overlay);

    overlay.querySelector('.refleksions-rum-luk').addEventListener('click', luk);
    overlay.querySelector('.refleksions-rum-naeste').addEventListener('click', naeste);
    overlay.querySelector('.refleksions-rum-tilbage').addEventListener('click', tilbage);

    // Klik på baggrund (uden for indholdet) lukker
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) luk();
    });

    // Swipe-håndtering på selve indholds-blokken
    var indhold = overlay.querySelector('.refleksions-rum-indhold');
    indhold.addEventListener('touchstart', onTouchStart, { passive: true });
    indhold.addEventListener('touchend', onTouchEnd, { passive: true });

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
    // Kræv tydelig vandret swipe
    if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy)) return;
    if (dx < 0) naeste();
    else tilbage();
  }

  function render() {
    var overlay = state.overlay;
    if (!overlay) return;

    var antal = state.spoergsmaal.length;
    var i = state.aktivIndex;
    var item = state.spoergsmaal[i] || { tekst: '', gruppeTitel: '' };
    var tekst = item.tekst;
    var overskrift = item.gruppeTitel || state.kilde;

    var kildeEl = overlay.querySelector('.refleksions-rum-kilde');
    if (overskrift) {
      kildeEl.textContent = overskrift;
      kildeEl.style.display = '';
    } else {
      kildeEl.textContent = '';
      kildeEl.style.display = 'none';
    }

    var tekstEl = overlay.querySelector('.refleksions-rum-tekst');

    // Marked-parse for at understøtte fed/kursiv inline; men strip ydre <p>
    // så vi kan styre typografi 100% via CSS.
    var html;
    if (typeof marked !== 'undefined' && marked.parse) {
      html = marked.parse(tekst);
      // Hvis der kun er ét <p>...</p>, strip det
      var match = html.match(/^\s*<p>([\s\S]*?)<\/p>\s*$/);
      if (match) html = match[1];
    } else {
      html = escapeHtml(tekst);
    }

    // Animation: fade ud, skift tekst, fade ind
    var wrap = overlay.querySelector('.refleksions-rum-tekst-wrap');
    wrap.classList.remove('refleksions-rum-fade-in', 'refleksions-rum-slide-frem', 'refleksions-rum-slide-tilbage');
    // Force reflow så animation kan trigges igen
    void wrap.offsetWidth;
    tekstEl.innerHTML = html;
    wrap.classList.add(
      'refleksions-rum-fade-in',
      state.skiftRetning === 'tilbage' ? 'refleksions-rum-slide-tilbage' : 'refleksions-rum-slide-frem'
    );

    // Progress dots
    var progress = overlay.querySelector('.refleksions-rum-progress');
    var dots = '';
    for (var k = 0; k < antal; k++) {
      dots += '<span class="refleksions-rum-dot' + (k === i ? ' aktiv' : '') + '"></span>';
    }
    progress.innerHTML = dots;
    progress.style.display = antal > 1 ? '' : 'none';

    // Navigation
    var tilbageBtn = overlay.querySelector('.refleksions-rum-tilbage');
    var naesteBtn = overlay.querySelector('.refleksions-rum-naeste');
    tilbageBtn.style.visibility = i > 0 ? 'visible' : 'hidden';
    naesteBtn.style.visibility = (antal > 0 && i < antal - 1) ? 'visible' : 'hidden';
  }

  function naeste() {
    if (state.aktivIndex >= state.spoergsmaal.length - 1) return;
    state.skiftRetning = 'frem';
    state.aktivIndex++;
    render();
  }

  function tilbage() {
    if (state.aktivIndex <= 0) return;
    state.skiftRetning = 'tilbage';
    state.aktivIndex--;
    render();
  }

  // Normaliser input til en flad liste af { tekst, gruppeTitel }
  function normaliser(opts) {
    var liste = [];
    if (opts.grupper && opts.grupper.length) {
      opts.grupper.forEach(function (g) {
        var sp = g.spoergsmaal || [];
        sp.forEach(function (s) {
          liste.push({ tekst: s, gruppeTitel: g.titel || '' });
        });
      });
    } else if (opts.spoergsmaal && opts.spoergsmaal.length) {
      opts.spoergsmaal.forEach(function (s) {
        liste.push({ tekst: s, gruppeTitel: '' });
      });
    }
    return liste;
  }

  function aabn(opts) {
    opts = opts || {};
    var liste = normaliser(opts);
    if (!liste.length) return;

    var overlay = bygOverlay();

    state.spoergsmaal = liste;
    state.kilde = opts.kilde || '';
    state.aktivIndex = 0;
    state.skiftRetning = 'frem';
    state.forrigScroll = window.scrollY || 0;

    // Lås body-scroll
    document.body.classList.add('refleksions-rum-aaben');

    overlay.classList.add('aaben');
    render();

    // ESC og piletaster
    state.keydownHandler = function (e) {
      if (e.key === 'Escape') { e.preventDefault(); luk(); }
      else if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); naeste(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); tilbage(); }
    };
    document.addEventListener('keydown', state.keydownHandler);
  }

  function luk() {
    var overlay = state.overlay;
    if (!overlay) return;
    overlay.classList.remove('aaben');
    document.body.classList.remove('refleksions-rum-aaben');
    if (state.keydownHandler) {
      document.removeEventListener('keydown', state.keydownHandler);
      state.keydownHandler = null;
    }
    // Behold scroll-position (vi har ikke ændret den, men body-låsen kan
    // forsinke scroll-restoration på iOS — så vi sætter eksplicit)
    window.scrollTo(0, state.forrigScroll);
  }

  // Hjælper til onclick fra trigger-knap
  function aabnFraTrigger(el) {
    try {
      var grupperRaw = el.getAttribute('data-grupper');
      if (grupperRaw) {
        aabn({ grupper: JSON.parse(grupperRaw) });
        return;
      }
      var sp = JSON.parse(el.getAttribute('data-spoergsmaal') || '[]');
      var kilde = el.getAttribute('data-kilde') || '';
      aabn({ spoergsmaal: sp, kilde: kilde });
    } catch (err) {
      console.error('RefleksionsRum: kunne ikke parse spørgsmål', err);
    }
  }

  window.RefleksionsRum = {
    aabn: aabn,
    luk: luk,
    aabnFraTrigger: aabnFraTrigger,
    splitMarkdown: splitMarkdown,
    triggerHTML: triggerHTML
  };
})();
