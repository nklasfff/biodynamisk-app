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

        // "Ikke nu" markeret indenfor 30 dage: vægt × 0.3
        if (lastSeen.reaction === 'ikke-nu' && gap < 30) weight *= 0.3;
      }

      // Koan-boost: hvis itemet er markeret som koan tidligere og 14+ dage siden
      const koanEntries = state.sidder.filter(s => s.id === item.id);
      if (koanEntries.length > 0) {
        const latestKoanDate = koanEntries.map(s => s.date).sort().pop();
        if (daysAgo(latestKoanDate) >= 14) weight *= 1.5;
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
  // Reaktioner ('send' | 'ikke-nu' | null) håndteres her.
  // Koan-status håndteres separat via toggleTodayKoan — uafhængigt af reaktioner.

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
    }
    saveStorage(state);
  }

  function mapReactionToStatKey(reaction) {
    if (reaction === 'send') return 'send';
    if (reaction === 'ikke-nu') return 'ikkeNu';
    return null;
  }

  // ----- Koan-håndtering (uafhængig af reactions) -----

  function harTodayKoan(state, itemId) {
    const today = todayKey();
    return state.sidder.some(s => s.id === itemId && s.date === today);
  }

  function toggleTodayKoan(state, item) {
    const today = todayKey();
    const idx = state.sidder.findIndex(s => s.id === item.id && s.date === today);
    state.typeStats[item.kategori] = state.typeStats[item.kategori] ||
      { sidder: 0, send: 0, ikkeNu: 0 };
    const stats = state.typeStats[item.kategori];
    if (idx >= 0) {
      state.sidder.splice(idx, 1);
      if (stats.sidder > 0) stats.sidder--;
    } else {
      state.sidder.push({ id: item.id, date: today });
      stats.sidder = (stats.sidder || 0) + 1;
    }
    saveStorage(state);
    return idx < 0; // true = nyligt tilføjet, false = fjernet
  }

  // ----- Send videre — del invitationen via Web Share API eller clipboard -----
  // Deler både selve teksten OG en URL til share.html.
  // I iMessage/Messenger/WhatsApp viser URL'en et lækkert preview-kort med
  // sol-illustrationen som og:image. I almindelig SMS ser man bare teksten + URL'en.

  function buildShareUrl(item) {
    // Byg en absolut URL til share.html?id=...
    const origin = window.location.origin;
    const path = window.location.pathname.replace(/[^/]*$/, ''); // mappe-del af stien
    return `${origin}${path}share.html?id=${encodeURIComponent(item.id)}`;
  }

  async function shareItem(item) {
    const url = buildShareUrl(item);
    // Bemærk: URL'en lægges INDE i teksten (ikke som separat url-felt) så vi
    // kontrollerer placeringen. ☼ er en typografisk sol-glyf der visuelt
    // adskiller invitationen fra link'et og dæmper det.
    const fuldTekst =
      `${item.navn}\n\n` +
      `${item.evokation}\n\n` +
      `— ${item.invitation}\n\n\n` +
      `☼\n\n` +
      `${url}`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Dagens invitation',
          text: fuldTekst
        });
        return true;
      } catch (e) {
        if (e.name === 'AbortError') return false; // bruger annullerede
        console.warn('Share fejlede:', e);
      }
    }

    // Fallback: kopier tekst til udklipsholder
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(fuldTekst);
        alert('Teksten er kopieret. Du kan nu indsætte den, hvor du vil.');
        return true;
      } catch (e) {
        console.warn('Clipboard fejlede:', e);
      }
    }

    alert('Deling er ikke tilgængelig på denne enhed.');
    return false;
  }

  // ----- DOM rendering -----

  function renderCard(slot, item, reaction, state) {
    const dateLabel = formatDanishDate(todayKey());
    const laesMere = getLaesMere(item);
    const erKoan = harTodayKoan(state, item.id);

    slot.innerHTML = `
      <article class="daglig-draw" data-reaction="${reaction || ''}" data-koan="${erKoan}">
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

        <div class="daglig-draw-actions" role="group" aria-label="Reaktion på dagens invitation">
          <button class="daglig-draw-btn" data-action="koan"
            aria-pressed="${erKoan}">
            <span aria-hidden="true">${erKoan ? '✓' : '♡'}</span>
            ${erKoan ? 'Dagens Levende Koan' : 'Dagens Levende Koan'}
          </button>
          <button class="daglig-draw-btn" data-action="send"
            aria-pressed="${reaction === 'send'}">
            send videre <span aria-hidden="true">→</span>
          </button>
          <button class="daglig-draw-btn daglig-draw-btn-quiet" data-action="ikke-nu"
            aria-pressed="${reaction === 'ikke-nu'}">
            ikke nu
          </button>
        </div>

        <p class="daglig-draw-samling-intro">
          Mine Koans er din egen skærm — her samler sig de invitationer du har markeret som Dagens Levende Koan, som et stille bibliotek af de hilsener der bliver siddende i dig.
        </p>

        <a class="daglig-draw-samling-link" href="samling.html">
          <span class="daglig-draw-samling-text">Se Mine Koans</span>
          ${state.sidder.length > 0 ? `<span class="daglig-draw-samling-count">${state.sidder.length}</span>` : ''}
          <span class="daglig-draw-samling-arrow" aria-hidden="true">›</span>
        </a>
      </article>
    `;

    // Wire Koan-toggle (uafhængig af reactions)
    const koanBtn = slot.querySelector('.daglig-draw-btn[data-action="koan"]');
    if (koanBtn) {
      koanBtn.addEventListener('click', () => {
        toggleTodayKoan(state, item);
        renderCard(slot, item, reaction, state);
      });
    }

    // Wire Send videre — deler via Web Share API + markerer reaktion
    const sendBtn = slot.querySelector('.daglig-draw-btn[data-action="send"]');
    if (sendBtn) {
      sendBtn.addEventListener('click', async () => {
        await shareItem(item);
        // Markér reaktion uanset om delingen lykkedes — det signalerer at brugeren har valgt at sende
        if (reaction !== 'send') {
          recordReaction('send', item, state);
          renderCard(slot, item, 'send', state);
        }
      });
    }

    // Wire Ikke nu — toggle reaktion
    const ikkeNuBtn = slot.querySelector('.daglig-draw-btn[data-action="ikke-nu"]');
    if (ikkeNuBtn) {
      ikkeNuBtn.addEventListener('click', () => {
        const newReaction = reaction === 'ikke-nu' ? null : 'ikke-nu';
        recordReaction(newReaction, item, state);
        renderCard(slot, item, newReaction, state);
      });
    }

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
