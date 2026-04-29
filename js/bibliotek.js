/* ============================================
   Bibliotek — gennemse de 60 mikrotekster
   ============================================
   Statisk visning. Filter efter kategori og simpel
   substring-søgning på navn + evokation + invitation.
*/

(function () {
  'use strict';

  const POOL_URL = 'content/daglig-draw/mikrotekster.json';

  const KATEGORIER = [
    { id: 'all',          label: 'Alle' },
    { id: 'princip',      label: 'Principper' },
    { id: 'blechschmidt', label: 'Blechschmidt' },
    { id: 'perspektiv',   label: 'Perspektiver' },
    { id: 'egenskab',     label: 'Egenskaber' },
    { id: 'zone',         label: 'Zoner' },
    { id: 'stadie',       label: 'Stadier' }
  ];

  let pool = [];
  let currentKategori = 'all';
  let currentQuery = '';
  let appEl = null;

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function filterAndRender() {
    const q = currentQuery.toLowerCase().trim();

    let items = pool.slice();

    if (currentKategori !== 'all') {
      items = items.filter(x => x.kategori === currentKategori);
    }

    if (q) {
      items = items.filter(x => {
        const haystack = [
          x.navn || '',
          x.evokation || '',
          x.invitation || ''
        ].join(' ').toLowerCase();
        return haystack.includes(q);
      });
    }

    // Bevar rækkefølgen som de står i mikrotekster.json
    // (først princip, så blechschmidt, så perspektiv, osv.)
    const orden = ['princip','blechschmidt','perspektiv','egenskab','zone','stadie'];
    items.sort((a, b) => {
      const ia = orden.indexOf(a.kategori);
      const ib = orden.indexOf(b.kategori);
      if (ia !== ib) return ia - ib;
      return 0;
    });

    renderList(items);
  }

  function renderChips() {
    return `
      <div class="bibliotek-chips" role="group" aria-label="Filtrer efter kategori">
        ${KATEGORIER.map(k => {
          const active = currentKategori === k.id ? 'bibliotek-chip-active' : '';
          const count = k.id === 'all' ? pool.length :
            pool.filter(p => p.kategori === k.id).length;
          return `<button class="bibliotek-chip ${active}" data-kategori="${escapeHtml(k.id)}">
            ${escapeHtml(k.label)} <span class="bibliotek-chip-count">${count}</span>
          </button>`;
        }).join('')}
      </div>
    `;
  }

  function renderSearch() {
    return `
      <div class="bibliotek-search">
        <input type="search" id="bibliotek-search-input" class="bibliotek-search-input"
          placeholder="S&oslash;g i mikrotekster..."
          value="${escapeHtml(currentQuery)}"
          autocomplete="off">
      </div>
    `;
  }

  function renderItem(item) {
    return `
      <article class="bibliotek-item">
        <p class="bibliotek-item-kategori">${escapeHtml(item.kategori_label || '')}</p>
        <h2 class="bibliotek-item-navn">${escapeHtml(item.navn || '')}</h2>
        <p class="bibliotek-item-evokation">${escapeHtml(item.evokation || '')}</p>
        ${item.invitation ? `
          <div class="bibliotek-item-symbol" aria-hidden="true">✦</div>
          <p class="bibliotek-item-invitation">${escapeHtml(item.invitation)}</p>
        ` : ''}
      </article>
    `;
  }

  function renderList(items) {
    const listSlot = document.getElementById('bibliotek-list');
    if (!listSlot) return;

    if (items.length === 0) {
      listSlot.innerHTML = `
        <p class="bibliotek-empty">Ingen mikrotekster matcher.</p>
      `;
      return;
    }

    listSlot.innerHTML = items.map(renderItem).join('');
  }

  function renderShell() {
    appEl.innerHTML = `
      ${renderChips()}
      ${renderSearch()}
      <div id="bibliotek-list" class="bibliotek-list"></div>
    `;

    // Wire chips
    appEl.querySelectorAll('.bibliotek-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        currentKategori = chip.dataset.kategori;
        renderShell();
        filterAndRender();
      });
    });

    // Wire search
    const searchInput = document.getElementById('bibliotek-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        currentQuery = searchInput.value;
        filterAndRender();
      });
    }

    filterAndRender();
  }

  async function init() {
    appEl = document.getElementById('bibliotek-app');
    if (!appEl) return;

    try {
      const res = await fetch(POOL_URL, { cache: 'no-cache' });
      if (!res.ok) throw new Error('Kunne ikke indlæse mikrotekster.json');
      const data = await res.json();
      pool = data.mikrotekster || [];

      if (pool.length === 0) {
        appEl.innerHTML = `<p class="bibliotek-empty">Ingen mikrotekster fundet.</p>`;
        return;
      }

      renderShell();
    } catch (e) {
      console.warn('Bibliotek kunne ikke indlæses:', e);
      appEl.innerHTML = `<p class="bibliotek-empty">Bibliotek kunne ikke indl&aelig;ses.</p>`;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
