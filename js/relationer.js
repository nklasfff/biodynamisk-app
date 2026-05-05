// js/relationer.js
// Indlæser relationer.json og rendrer "Hænger sammen med" + "Lever også i"
// nederst på begreb-, zone- og stadie-sider.
//
// `relationer.json` bruger korte ids (fx "dynamisk-stilhed", "s1-foerste-stadie").
// Filnavne og URL'er bruger nummererede ids (fx "01-dynamisk-stilhed", "01-foerste-stadie").
// Dette modul oversætter mellem de to og slår navne op til visning.

window.Relationer = (function() {
  'use strict';

  let cache = null;
  let promise = null;
  let laesvejCache = null;
  let laesvejPromise = null;

  // Begrebs-rækkefølge → nummerprefix i URL
  const BEGREB_NUMBERS = {
    'dynamisk-stilhed': '01',
    'breath-of-life': '02',
    'primary-respiration': '03',
    'midtlinjen': '04',
    'the-health': '05',
    'motion-present': '06',
    'fulcrum': '07',
    'stillpoints': '08',
    'transmutation': '09',
    'the-neutral': '10',
    'automatic-shifting': '11',
    'den-iboende-behandlingsplan': '12',
    'fluid-body': '13',
    'the-lesion-field': '14',
    'potency': '15',
    'ignition': '16',
    'axial-fluctuations': '17',
    'wholeness': '18'
  };

  // Visningsnavne — tro mod hvordan enheden hedder andre steder i appen
  const NAMES = {
    // Begreber
    'dynamisk-stilhed': 'Dynamisk Stilhed',
    'breath-of-life': 'Breath of Life',
    'primary-respiration': 'Primary Respiration',
    'midtlinjen': 'Midtlinjen',
    'the-health': 'The Health',
    'motion-present': 'Motion Present',
    'fulcrum': 'Fulcrum',
    'stillpoints': 'Stillpoints',
    'transmutation': 'Transmutation',
    'the-neutral': 'The Neutral',
    'automatic-shifting': 'Automatic Shifting',
    'den-iboende-behandlingsplan': 'Den Iboende Behandlingsplan',
    'fluid-body': 'Fluid Body',
    'the-lesion-field': 'The Lesion Field',
    'potency': 'Potency',
    'ignition': 'Ignition',
    'axial-fluctuations': 'Axial Fluctuations',
    'wholeness': 'Wholeness',
    // Zoner
    'a-fysisk-krop': 'Rum A — Den fysiske krop',
    'b-vaeskekrop': 'Rum B — Væskekroppen',
    'c-relationelt-felt': 'Rum C — Det relationelle felt',
    'd-primary-respiration': 'Rum D — The Long Tide',
    'e-dynamisk-stilhed': 'Rum E — Dynamisk Stilhed',
    // Kvaliteter (de 8 essentielle egenskaber)
    'k1-neutral-lytten': 'Egenskab 1 — Neutral lytten uden agenda',
    'k2-selvregulering': 'Egenskab 2 — Selvregulering af nervesystemet',
    'k3-sansning': 'Egenskab 3 — Sansning af den terapeutiske proces',
    'k4-taalmodighed-uvished': 'Egenskab 4 — Tålmodighed & uvished',
    'k5-helhedens-prioritering': 'Egenskab 5 — At mærke helhedens prioritering',
    'k6-synkron-bevaegelse': 'Egenskab 6 — Synkron bevægelse med kroppen',
    'k7-beroering': 'Egenskab 7 — Kvalitet i berøringen',
    'k8-rytme': 'Egenskab 8 — Sans for behandlingens rytme',
    // Stadier
    's1-foerste-stadie': '1. stadie',
    's2-andet-stadie': '2. stadie',
    's3-tredje-stadie': '3. stadie',
    's4-fjerde-stadie': '4. stadie',
    's5-femte-stadie': '5. stadie',
    // Øvelser
    'o1-the-neutral': 'Øvelse 1 — The Neutral',
    'o2-kroppens-egen-viden': 'Øvelse 2 — Kroppens egen viden',
    'o3-kroppens-dynamiske-landskaber': 'Øvelse 3 — Kroppens dynamiske landskaber',
    'o4-vejrtraekningen': 'Øvelse 4 — Vejrtrækningen'
  };

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // Konverter "01-dynamisk-stilhed" → "dynamisk-stilhed"
  function begrebFileIdToShortId(fileId) {
    return fileId.replace(/^\d+-/, '');
  }

  // Konverter "01-foerste-stadie" → "s1-foerste-stadie"
  function stadieFileIdToShortId(fileId) {
    const m = fileId.match(/^(\d+)-(.+)$/);
    if (!m) return fileId;
    return `s${parseInt(m[1], 10)}-${m[2]}`;
  }

  // Konverter "s1-foerste-stadie" → "01-foerste-stadie"
  function stadieShortIdToFileId(shortId) {
    const m = shortId.match(/^s(\d+)-(.+)$/);
    if (!m) return shortId;
    return `${String(m[1]).padStart(2, '0')}-${m[2]}`;
  }

  function relationToUrl(rel) {
    if (!rel || !rel.type || !rel.id) return null;
    if (rel.type === 'begreb') {
      const num = BEGREB_NUMBERS[rel.id];
      if (!num) return null;
      return `begreb.html?id=${num}-${rel.id}`;
    }
    if (rel.type === 'zone') {
      return `zone.html?id=${rel.id}`;
    }
    if (rel.type === 'stadie') {
      return `stadie.html?id=${stadieShortIdToFileId(rel.id)}`;
    }
    if (rel.type === 'kvalitet') {
      // De 8 egenskaber er ét kapitel — link dertil
      return `kapitel.html?id=de-otte-essentielle-egenskaber`;
    }
    if (rel.type === 'oevelse') {
      return `kapitel.html?id=de-fire-guidede-oevelser`;
    }
    return null;
  }

  function relationName(rel) {
    if (!rel || !rel.id) return '';
    return NAMES[rel.id] || rel.id;
  }

  async function load() {
    if (cache) return cache;
    if (promise) return promise;
    promise = fetch('relationer.json')
      .then(r => r.ok ? r.json() : {})
      .then(json => { cache = json; return json; })
      .catch(() => { cache = {}; return cache; });
    return promise;
  }

  async function getEntry(shortId) {
    const data = await load();
    return data[shortId] || null;
  }

  async function loadLaesveje() {
    if (laesvejCache) return laesvejCache;
    if (laesvejPromise) return laesvejPromise;
    laesvejPromise = fetch('laesveje.json')
      .then(r => r.ok ? r.json() : {})
      .then(json => { laesvejCache = json; return json; })
      .catch(() => { laesvejCache = {}; return laesvejCache; });
    return laesvejPromise;
  }

  async function getLaesvej(shortId) {
    const data = await loadLaesveje();
    return data[shortId] || null;
  }

  // Render prosa-invitation: konverter [navn](url) → <a href="url">navn</a>
  function renderLaesvejHTML(prose) {
    if (!prose || typeof prose !== 'string') return '';
    const linked = prose.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      (_, name, url) => `<a href="${url}">${escapeHtml(name)}</a>`
    );
    return `<aside class="laesvej"><p>${linked}</p></aside>`;
  }

  function renderHTML(entry) {
    if (!entry) return '';
    const sammen = Array.isArray(entry.haenger_sammen_med) ? entry.haenger_sammen_med : [];
    const lever = Array.isArray(entry.lever_ogsaa_i) ? entry.lever_ogsaa_i : [];
    if (sammen.length === 0 && lever.length === 0) return '';

    function listHTML(rels) {
      const items = rels.map(r => {
        const url = relationToUrl(r);
        const name = relationName(r);
        if (!url || !name) return '';
        const desc = r.kort_beskrivelse ? escapeHtml(r.kort_beskrivelse) : '';
        return `
          <li>
            <a class="relationer-card" href="${url}">
              <span class="relationer-card-name">${escapeHtml(name)}</span>
              ${desc ? `<span class="relationer-card-desc">${desc}</span>` : ''}
              <span class="relationer-card-arrow" aria-hidden="true">›</span>
            </a>
          </li>
        `;
      }).filter(Boolean).join('');
      return items ? `<ul class="relationer-list">${items}</ul>` : '';
    }

    let html = '<section class="relationer-section">';
    if (sammen.length > 0) {
      html += '<h3 class="relationer-heading">Hænger sammen med</h3>';
      html += listHTML(sammen);
    }
    if (lever.length > 0) {
      html += '<h3 class="relationer-heading">Lever også i</h3>';
      html += listHTML(lever);
    }
    html += '</section>';
    return html;
  }

  // Bekvemmeligheds-funktion: hent og render både relationer-indeks og læsevej
  // som ét HTML-uddrag, klar til at indsætte nederst på en detalje-side.
  async function renderForId(shortId) {
    const [entry, laesvej] = await Promise.all([
      getEntry(shortId),
      getLaesvej(shortId)
    ]);
    return renderHTML(entry) + renderLaesvejHTML(laesvej);
  }

  return {
    load,
    getEntry,
    getLaesvej,
    renderHTML,
    renderLaesvejHTML,
    renderForId,
    begrebFileIdToShortId,
    stadieFileIdToShortId
  };
})();
