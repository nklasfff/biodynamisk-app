/* ============================================
   Bibliotek — gemte tekster fra Dagens Invitation
   ============================================
   Viser kun de invitationer brugeren selv har gemt.
   Læser fra window.BibliotekStore (localStorage).
*/

(function () {
  'use strict';

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

  function formatDanishDate(dateKey) {
    if (!dateKey) return '';
    const months = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun',
      'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
    const d = new Date(dateKey);
    if (isNaN(d.getTime())) return '';
    return d.getDate() + '. ' + months[d.getMonth()];
  }

  function renderItem(entry) {
    const s = entry.snapshot || {};
    return `
      <article class="bibliotek-item" data-id="${escapeHtml(entry.id)}">
        <header class="bibliotek-item-header">
          <span class="bibliotek-item-kategori">${escapeHtml(s.kategori_label || '')}</span>
          <span class="bibliotek-item-dato">gemt ${escapeHtml(formatDanishDate(entry.gemtDato))}</span>
        </header>
        <h2 class="bibliotek-item-navn">${escapeHtml(s.navn || '')}</h2>
        ${s.evokation ? `<p class="bibliotek-item-evokation">${escapeHtml(s.evokation)}</p>` : ''}
        ${s.invitation ? `
          <div class="bibliotek-item-symbol" aria-hidden="true">✦</div>
          <p class="bibliotek-item-invitation">${escapeHtml(s.invitation)}</p>
        ` : ''}
        <div class="bibliotek-item-actions">
          <button class="bibliotek-fjern-btn" data-id="${escapeHtml(entry.id)}" data-type="${escapeHtml(entry.type)}">
            Fjern fra bibliotek
          </button>
        </div>
      </article>
    `;
  }

  function renderTomtState() {
    return `
      <div class="bibliotek-empty">
        <p>Dit bibliotek er endnu tomt.</p>
        <p class="bibliotek-empty-hint">Når du møder en invitation du gerne vil have direkte adgang til, kan du gemme den herfra.</p>
        <a class="bibliotek-empty-link" href="dagens-invitation.html">Gå til dagens invitation</a>
      </div>
    `;
  }

  function render() {
    if (!appEl) return;
    if (!window.BibliotekStore) {
      appEl.innerHTML = `<p class="bibliotek-empty">Bibliotek kunne ikke indlæses.</p>`;
      return;
    }

    const liste = window.BibliotekStore.hent();

    if (liste.length === 0) {
      appEl.innerHTML = renderTomtState();
      return;
    }

    // Nyeste først
    const sorteret = liste.slice().sort((a, b) => {
      return (b.gemtDato || '').localeCompare(a.gemtDato || '');
    });

    appEl.innerHTML = `
      <p class="bibliotek-count">${sorteret.length} ${sorteret.length === 1 ? 'gemt tekst' : 'gemte tekster'}.</p>
      <div class="bibliotek-list">
        ${sorteret.map(renderItem).join('')}
      </div>
    `;

    // Wire fjern-knapper
    appEl.querySelectorAll('.bibliotek-fjern-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const type = btn.dataset.type;
        window.BibliotekStore.fjern(type, id);
        render();
      });
    });
  }

  function init() {
    appEl = document.getElementById('bibliotek-app');
    if (!appEl) return;
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
