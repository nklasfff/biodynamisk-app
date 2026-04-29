/* ============================================
   Dagens Draw — daglig hilsen fra korpus
   ============================================
   En kort daglig hilsen trukket algoritmisk fra bogens materiale.
   Caches pr. dag i localStorage, lærer over tid hvilke typer
   brugeren dvæler ved.

   Storage-skema (localStorage["biodynamisk-daglig-draw"]):
   {
     version: 1,
     history: [{date: "2026-04-29", id: "...", reaction: "sidder"|"send"|"ikke-nu"|null}],
     sidder: ["id1", "id2", ...],          // kronologisk samling
     typeStats: {                            // til personalisering
       biodynamisk: {sidder: n, send: n, ikkeNu: n},
       blechschmidt: {...},
       perspektiv: {...}
     }
   }
*/

(function () {
  'use strict';

  const STORAGE_KEY = 'biodynamisk-daglig-draw';
  const STORAGE_VERSION = 2;  // bumpet ved skema-migration til kategori/mikrotekster
  const POOL_URL = 'content/daglig-draw/mikrotekster.json';

  // Kategori → kapitel/sektion. Den nye mikrotekster.json har ikke
  // laes_mere som felt, så vi udleder URL'en fra kategori.
  const KATEGORI_LAES_MERE = {
    'princip': 'kapitel.html?id=den-biodynamiske-model',
    'blechschmidt': 'kapitel.html?id=blechschmidts-principper',
    'perspektiv': 'kapitel.html?id=de-syv-perspektiver',
    'egenskab': 'kapitel.html?id=de-otte-essentielle-egenskaber',
    'zone': 'zoner.html',
    'stadie': 'stadier.html'
  };

  function getLaesMere(item) {
    return KATEGORI_LAES_MERE[item.kategori] || null;
  }

  // ----- Storage -----

  function loadStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultStorage();
      const parsed = JSON.parse(raw);
      if (parsed.version !== STORAGE_VERSION) return defaultStorage();
      return parsed;
    } catch (e) {
      return defaultStorage();
    }
  }

  function defaultStorage() {
    return {
      version: STORAGE_VERSION,
      history: [],
      sidder: [],
      typeStats: {}
    };
  }

  function saveStorage(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // localStorage unavailable — degrade gracefully
    }
  }

  // ----- Date helpers -----

  function todayKey() {
    const d = new Date();
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }

  function daysAgo(dateKey) {
    const today = new Date(todayKey());
    const then = new Date(dateKey);
    const ms = today - then;
    return Math.floor(ms / (1000 * 60 * 60 * 24));
  }

  function formatDanishDate(dateKey) {
    const months = ['januar', 'februar', 'marts', 'april', 'maj', 'juni',
      'juli', 'august', 'september', 'oktober', 'november', 'december'];
    const d = new Date(dateKey);
    return d.getDate() + '. ' + months[d.getMonth()];
  }

  // ----- Algoritme: vægt og udvælgelse -----

  function computeWeight(item, state) {
    let weight = 1;

    // Udelukket: set sidste 7 dage
    const recent7 = state.history.filter(h => daysAgo(h.date) <= 7);
    if (recent7.some(h => h.id === item.id)) return 0;

    // Aldrig set: vægt × 3
    const everSeen = state.history.some(h => h.id === item.id);
    if (!everSeen) {
      weight *= 3;
    } else {
      // Set tidligere — find seneste forekomst
      const lastSeen = state.history
        .filter(h => h.id === item.id)
        .reduce((latest, h) => (!latest || h.date > latest.date) ? h : latest, null);

      if (lastSeen) {
        const gap = daysAgo(lastSeen.date);

        // Set for 30+ dage siden: vægt × 2
        if (gap > 30) weight *= 2;

        // "Sidder" markeret tidligere og 14+ dage siden: vægt × 1.5
        if (lastSeen.reaction === 'sidder' && gap >= 14) weight *= 1.5;

        // "Ikke nu" markeret indenfor 30 dage: vægt × 0.3
        if (lastSeen.reaction === 'ikke-nu' && gap < 30) weight *= 0.3;
      }
    }

    // Samme kategori som i går: vægt × 0.2 (rotation)
    const yesterday = state.history.find(h => daysAgo(h.date) === 1);
    if (yesterday) {
      const yPool = window.__dailyDrawPool;
      const yItem = yPool && yPool.find(p => p.id === yesterday.id);
      if (yItem && yItem.kategori === item.kategori) weight *= 0.2;
    }

    // Personalisering: favorit-kategori efter 5+ reaktioner: vægt × 1.3
    const stats = state.typeStats[item.kategori];
    if (stats) {
      const total = (stats.sidder || 0) + (stats.send || 0) + (stats.ikkeNu || 0);
      if (total >= 5) {
        const sidderRate = (stats.sidder || 0) / total;
        if (sidderRate > 0.5) weight *= 1.3;
      }
    }

    return weight;
  }

  function pickWeighted(pool, state) {
    const weighted = pool.map(item => ({
      item,
      weight: computeWeight(item, state)
    }));

    const total = weighted.reduce((sum, w) => sum + w.weight, 0);
    if (total <= 0) {
      // Fallback: pure random hvis alt er udelukket
      return pool[Math.floor(Math.random() * pool.length)];
    }

    let r = Math.random() * total;
    for (const w of weighted) {
      r -= w.weight;
      if (r <= 0) return w.item;
    }
    return weighted[weighted.length - 1].item;
  }

  function getOrCreateTodaysDraw(pool, state) {
    const today = todayKey();
    const existing = state.history.find(h => h.date === today);
    if (existing) {
      const item = pool.find(p => p.id === existing.id);
      if (item) return { item, reaction: existing.reaction };
    }

    const item = pickWeighted(pool, state);
    state.history.push({ date: today, id: item.id, reaction: null });
    saveStorage(state);
    return { item, reaction: null };
  }

  // ----- Reaktionshåndtering -----

  function recordReaction(reaction, item, state) {
    const today = todayKey();
    const entry = state.history.find(h => h.date === today);
    if (entry) {
      const previous = entry.reaction;
      entry.reaction = reaction;

      // Opdater kategori-stats (rul tilbage hvis tidligere reaktion var sat)
      state.typeStats[item.kategori] = state.typeStats[item.kategori] ||
        { sidder: 0, send: 0, ikkeNu: 0 };
      const stats = state.typeStats[item.kategori];

      if (previous) {
        const k = mapReactionToStatKey(previous);
        if (k && stats[k] > 0) stats[k]--;
      }
      const newKey = mapReactionToStatKey(reaction);
      if (newKey) stats[newKey] = (stats[newKey] || 0) + 1;

      // Opdater sidder-samling
      if (reaction === 'sidder') {
        if (!state.sidder.find(s => s.id === item.id && s.date === today)) {
          state.sidder.push({ id: item.id, date: today });
        }
      } else {
        // Hvis brugeren skifter væk fra "sidder" i dag, fjern fra samling
        state.sidder = state.sidder.filter(
          s => !(s.id === item.id && s.date === today)
        );
      }
    }
    saveStorage(state);
  }

  function mapReactionToStatKey(reaction) {
    if (reaction === 'sidder') return 'sidder';
    if (reaction === 'send') return 'send';
    if (reaction === 'ikke-nu') return 'ikkeNu';
    return null;
  }

  // ----- DOM rendering -----

  function renderCard(slot, item, reaction, state) {
    const dateLabel = formatDanishDate(todayKey());
    const laesMere = getLaesMere(item);

    slot.innerHTML = `
      <article class="daglig-draw" data-reaction="${reaction || ''}">
        <header class="daglig-draw-header">
          <span class="daglig-draw-type">${escapeHtml(item.kategori_label)}</span>
          <span class="daglig-draw-date">${escapeHtml(dateLabel)}</span>
        </header>

        <h3 class="daglig-draw-navn">${escapeHtml(item.navn)}</h3>

        <p class="daglig-draw-evokation">${escapeHtml(item.evokation)}</p>

        <div class="daglig-draw-symbol" aria-hidden="true">✦</div>

        <p class="daglig-draw-invitation">${escapeHtml(item.invitation)}</p>

        ${laesMere ? `
          <a class="daglig-draw-laes-mere" href="${escapeAttr(laesMere)}">Læs mere</a>
        ` : ''}

        <div class="daglig-draw-actions" role="group" aria-label="Reaktion på dagens draw">
          <button class="daglig-draw-btn" data-reaction="sidder"
            aria-pressed="${reaction === 'sidder'}">
            <span aria-hidden="true">♡</span> sidder hos mig
          </button>
          <button class="daglig-draw-btn" data-reaction="send"
            aria-pressed="${reaction === 'send'}">
            send videre <span aria-hidden="true">→</span>
          </button>
          <button class="daglig-draw-btn daglig-draw-btn-quiet" data-reaction="ikke-nu"
            aria-pressed="${reaction === 'ikke-nu'}">
            ikke nu
          </button>
        </div>

        <a class="daglig-draw-samling-link" href="samling.html">
          Min samling${state.sidder.length > 0 ? ` <span class="daglig-draw-samling-count">${state.sidder.length}</span>` : ''}
        </a>
      </article>
    `;

    // Wire up buttons
    const buttons = slot.querySelectorAll('.daglig-draw-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const newReaction = btn.dataset.reaction;
        // Toggle: hvis allerede valgt, fjern reaktionen
        const currentReaction = slot.querySelector('.daglig-draw').dataset.reaction;
        const finalReaction = currentReaction === newReaction ? null : newReaction;
        recordReaction(finalReaction, item, state);
        renderCard(slot, item, finalReaction, state);
      });
    });
  }

  // ----- Util -----

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(str) {
    return escapeHtml(str);
  }

  // ----- Bootstrap -----

  async function init() {
    const slot = document.getElementById('daglig-draw-slot');
    if (!slot) return;

    try {
      const res = await fetch(POOL_URL, { cache: 'no-cache' });
      if (!res.ok) throw new Error('Kunne ikke indlæse daglig-draw.json');
      const data = await res.json();
      const pool = data.mikrotekster || [];
      if (pool.length === 0) return;

      // Eksponér pool globalt så computeWeight kan slå op i går
      window.__dailyDrawPool = pool;

      const state = loadStorage();
      const { item, reaction } = getOrCreateTodaysDraw(pool, state);

      renderCard(slot, item, reaction, state);
    } catch (e) {
      console.warn('Daglig draw kunne ikke initialiseres:', e);
      slot.innerHTML = '';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
