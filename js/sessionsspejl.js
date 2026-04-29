/* ============================================
   Sessionsspejl — stille refleksion mellem sessioner
   ============================================
   Et reflektionsværktøj for behandleren. IKKE en journal om klienten —
   et spejl af behandlerens egen tilstedeværelse i mødet.

   Storage-skema (localStorage["biodynamisk-sessionsspejl"]):
   {
     version: 1,
     hasSeenOnboarding: bool,
     clients: [{ id, alias, created }],
     sessions: [{
       id, clientId|null, date,
       zones: ["A","B"],   // 1-2 stk
       quality: "neutral-lytten",
       kropTekst: "",
       bevaegelseTekst: "",
       overraskelseTekst: ""
     }]
   }
*/

(function () {
  'use strict';

  const STORAGE_KEY = 'biodynamisk-sessionsspejl';
  const STORAGE_VERSION = 1;
  const MIKROTEKSTER_URL = 'content/daglig-draw/mikrotekster.json';
  const ORDBOG_URL = 'content/daglig-draw/resonans-ordbog.json';
  const GENKLANGE_MAX = 3;

  // Genklange-data — loades async i init(), bruges af computeResonance
  let mikrotekster = [];
  let resonansOrdbog = {};

  // ----- Statiske data: zoner og kvaliteter -----

  const ZONES = [
    { id: 'A', label: 'Zone A · Den fysiske krop' },
    { id: 'B', label: 'Zone B · Væskekroppen' },
    { id: 'C', label: 'Zone C · Det relationelle felt' },
    { id: 'D', label: 'Zone D · Primary Respiration' },
    { id: 'E', label: 'Zone E · Dynamisk Stilhed' }
  ];

  const QUALITIES = [
    { id: 'neutral-lytten', label: 'Neutral lytten' },
    { id: 'selvregulering', label: 'Selvregulering af nervesystemet' },
    { id: 'sansning-af-proces', label: 'Sansning af den terapeutiske proces' },
    { id: 'taalmodighed-uvished', label: 'Tålmodighed og uvished' },
    { id: 'helhedens-prioritering', label: 'Helhedens prioritering' },
    { id: 'synkron-bevaegelse', label: 'Synkron bevægelse' },
    { id: 'kvalitet-i-beroeringen', label: 'Kvalitet i berøringen' },
    { id: 'sans-for-rytme', label: 'Sans for rytme' }
  ];

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
      hasSeenOnboarding: false,
      clients: [],
      sessions: []
    };
  }

  function saveStorage(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // localStorage unavailable — degrade gracefully
    }
  }

  // ----- Util -----

  function uuid() {
    if (window.crypto && window.crypto.randomUUID) {
      return window.crypto.randomUUID();
    }
    return 'id-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
  }

  function todayKey() {
    const d = new Date();
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }

  function formatDanishDate(dateKey) {
    const months = ['januar', 'februar', 'marts', 'april', 'maj', 'juni',
      'juli', 'august', 'september', 'oktober', 'november', 'december'];
    const d = new Date(dateKey);
    return d.getDate() + '. ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function clientById(state, id) {
    if (!id) return null;
    return state.clients.find(c => c.id === id) || null;
  }

  function aliasFor(state, clientId) {
    const c = clientById(state, clientId);
    return c ? c.alias : null;
  }

  function zoneLabel(id) {
    const z = ZONES.find(z => z.id === id);
    return z ? z.label : id;
  }

  function qualityLabel(id) {
    const q = QUALITIES.find(q => q.id === id);
    return q ? q.label : id;
  }

  // ----- Genklange (resonans-motor) -----
  // Gennemsøger fri-tekst for stamme-former fra resonans-ordbogen.
  // Substring-match — så "tålmod" matcher tålmodig, tålmodighed,
  // utålmodighed, utålmodigt osv. Returnerer top N matches sorteret
  // efter score (antal stamme-former der peger på samme mikrotekst).

  function computeResonance(text) {
    if (!text || !resonansOrdbog) return [];
    const stems = Object.keys(resonansOrdbog);
    if (stems.length === 0) return [];

    const lower = String(text).toLowerCase();
    // Splitter teksten i ord til at vise tilbage hvilke ord der matched
    const userWords = lower.split(/[\s.,;:!?()\-—'"\[\]\/]+/).filter(Boolean);

    const matches = {}; // id -> { score, words: Set }

    for (const stem of stems) {
      if (!lower.includes(stem)) continue;
      // Find præcist hvilke af brugerens ord der indeholder denne stamme
      const triggeringWords = userWords.filter(w => w.includes(stem));

      const ids = resonansOrdbog[stem] || [];
      for (const id of ids) {
        if (!matches[id]) {
          matches[id] = { score: 0, words: new Set() };
        }
        matches[id].score++;
        triggeringWords.forEach(w => matches[id].words.add(w));
      }
    }

    return Object.entries(matches)
      .map(([id, m]) => ({
        id,
        score: m.score,
        words: Array.from(m.words).sort()
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, GENKLANGE_MAX);
  }

  function renderResonanceCards(text) {
    const matches = computeResonance(text);
    if (matches.length === 0) return '';
    if (!mikrotekster || mikrotekster.length === 0) return '';

    const cards = matches.map(m => {
      const mt = mikrotekster.find(x => x.id === m.id);
      if (!mt) return '';
      const wordsHtml = m.words.length > 0
        ? `<p class="ss-genklang-words"><span class="ss-genklang-symbol" aria-hidden="true">✦</span> du n&aelig;vnte: ${m.words.map(w => `<em>${escapeHtml(w)}</em>`).join(', ')}</p>`
        : '';
      return `
        <article class="ss-genklang">
          <p class="ss-genklang-kategori">${escapeHtml(mt.kategori_label || '')}</p>
          <h3 class="ss-genklang-navn">${escapeHtml(mt.navn || '')}</h3>
          <p class="ss-genklang-evokation">${escapeHtml(mt.evokation || '')}</p>
          ${wordsHtml}
        </article>
      `;
    }).join('');

    return `
      <section class="ss-genklange">
        <p class="ss-genklange-label">GENKLANGE</p>
        <p class="ss-genklange-tagline">det du skrev rummer ord fra bogens vokabular</p>
        ${cards}
      </section>
    `;
  }

  function combinedFreeText(entry) {
    return [entry.kropTekst, entry.bevaegelseTekst, entry.overraskelseTekst]
      .filter(Boolean)
      .join(' ');
  }

  // ----- App-state og DOM-mounting -----

  let state = null;
  let appEl = null;

  // Draft for new entry — held i hukommelsen mens wizard er aktiv
  let draft = null;
  let currentStep = 0;
  let filterClientId = 'all';

  function setState(newState) {
    state = newState;
    saveStorage(state);
  }

  function render() {
    if (!appEl) return;

    if (!state.hasSeenOnboarding) {
      renderOnboarding();
    } else if (draft !== null) {
      renderEntryFlow();
    } else {
      renderList();
    }
  }

  // ----- View: Onboarding -----

  function renderOnboarding() {
    appEl.innerHTML = `
      <section class="ss-onboarding">
        <div class="ss-onboarding-symbol" aria-hidden="true">✦</div>
        <p class="ss-onboarding-text">Sessionsspejl er ikke en journal for klienten — men for dig.</p>
        <p class="ss-onboarding-text">Et stille sted hvor du kan vende tilbage til det øjeblik der lige var, og spørge: Hvor levede arbejdet? Hvad blev jeg bedt om at bringe? Hvad bevægede sig i mig?</p>
        <p class="ss-onboarding-text">Over tid begynder mønstre at vise sig — ikke om klienterne, men om dig som behandler. Hvor du naturligt arbejder. Hvilke kvaliteter der oftest kalder på dig. Hvad du selv stadig modnes i.</p>
        <p class="ss-onboarding-text ss-onboarding-text-quiet">Indførslerne bliver hos dig. De forlader aldrig din enhed.</p>
        <button class="ss-btn ss-btn-primary" id="ss-onboarding-begin">Begynd</button>
      </section>
    `;

    document.getElementById('ss-onboarding-begin').addEventListener('click', () => {
      state.hasSeenOnboarding = true;
      setState(state);
      render();
    });
  }

  // ----- View: Liste / tom -----

  function renderList() {
    const total = state.sessions.length;

    if (total === 0) {
      appEl.innerHTML = `
        <section class="ss-empty">
          <p class="ss-empty-text">Du har endnu ikke lavet en indførsel.</p>
          <button class="ss-btn ss-btn-primary" id="ss-start-first">Lav første indførsel</button>
        </section>
      `;
      document.getElementById('ss-start-first').addEventListener('click', startNewEntry);
      return;
    }

    // Filter chips kun hvis der findes klienter
    let filterHtml = '';
    if (state.clients.length > 0) {
      const chipAll = filterClientId === 'all' ? 'ss-chip-active' : '';
      const chipNone = filterClientId === 'none' ? 'ss-chip-active' : '';
      filterHtml = `
        <div class="ss-filter-chips" role="group" aria-label="Filtrer indførsler">
          <button class="ss-chip ${chipAll}" data-filter="all">Alle <span class="ss-chip-count">${total}</span></button>
          ${state.clients.map(c => {
            const active = filterClientId === c.id ? 'ss-chip-active' : '';
            const count = state.sessions.filter(s => s.clientId === c.id).length;
            return `<button class="ss-chip ${active}" data-filter="${escapeHtml(c.id)}">${escapeHtml(c.alias)} <span class="ss-chip-count">${count}</span></button>`;
          }).join('')}
          <button class="ss-chip ${chipNone}" data-filter="none">Uden alias <span class="ss-chip-count">${state.sessions.filter(s => !s.clientId).length}</span></button>
        </div>
      `;
    }

    // Filter sessions
    let visible = state.sessions.slice();
    if (filterClientId === 'none') {
      visible = visible.filter(s => !s.clientId);
    } else if (filterClientId !== 'all') {
      visible = visible.filter(s => s.clientId === filterClientId);
    }
    // Nyeste først
    visible.sort((a, b) => (b.date + b.id).localeCompare(a.date + a.id));

    const listHtml = visible.length === 0 ? `
      <p class="ss-empty-text ss-empty-text-quiet">Ingen indførsler matcher filtret.</p>
    ` : visible.map(s => renderListItem(s)).join('');

    appEl.innerHTML = `
      <section class="ss-list-section">
        <button class="ss-btn ss-btn-primary ss-btn-block" id="ss-start-new">Ny indførsel</button>
        ${filterHtml}
        <ul class="ss-list">${listHtml}</ul>
      </section>
    `;

    document.getElementById('ss-start-new').addEventListener('click', startNewEntry);

    appEl.querySelectorAll('.ss-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        filterClientId = chip.dataset.filter;
        render();
      });
    });

    appEl.querySelectorAll('.ss-list-item').forEach(item => {
      item.addEventListener('click', () => {
        showEntryDetail(item.dataset.id);
      });
    });
  }

  function renderListItem(s) {
    const alias = aliasFor(state, s.clientId);
    const zonesText = (s.zones || []).map(zoneLabel).join(', ') || '';
    const qualityText = qualityLabel(s.quality) || '';
    const meta = [zonesText, qualityText].filter(Boolean).join(' · ');

    // Find første ikke-tomme tekst som hint
    const firstText = s.kropTekst || s.bevaegelseTekst || s.overraskelseTekst || '';
    const hint = firstText ? firstText.slice(0, 110) + (firstText.length > 110 ? '…' : '') : '';

    return `
      <li class="ss-list-item" data-id="${escapeHtml(s.id)}" tabindex="0" role="button">
        <div class="ss-list-item-header">
          <span class="ss-list-item-date">${escapeHtml(formatDanishDate(s.date))}</span>
          ${alias ? `<span class="ss-list-item-alias">${escapeHtml(alias)}</span>` : ''}
        </div>
        ${meta ? `<p class="ss-list-item-meta">${escapeHtml(meta)}</p>` : ''}
        ${hint ? `<p class="ss-list-item-hint">${escapeHtml(hint)}</p>` : ''}
      </li>
    `;
  }

  // ----- View: Entry detail -----

  function showEntryDetail(id) {
    const s = state.sessions.find(s => s.id === id);
    if (!s) return;

    const alias = aliasFor(state, s.clientId);
    const zonesText = (s.zones || []).map(zoneLabel).join(', ');

    const resonanceHtml = renderResonanceCards(combinedFreeText(s));

    appEl.innerHTML = `
      <section class="ss-detail">
        <button class="ss-btn-text" id="ss-detail-back">‹ Tilbage til listen</button>

        <header class="ss-detail-header">
          <span class="ss-detail-date">${escapeHtml(formatDanishDate(s.date))}</span>
          ${alias ? `<span class="ss-detail-alias">${escapeHtml(alias)}</span>` : ''}
        </header>

        ${zonesText ? `
          <div class="ss-detail-block">
            <p class="ss-detail-label">Hvor levede dagens arbejde?</p>
            <p class="ss-detail-value">${escapeHtml(zonesText)}</p>
          </div>
        ` : ''}

        ${s.quality ? `
          <div class="ss-detail-block">
            <p class="ss-detail-label">Hvilken kvalitet blev du bedt om at bringe?</p>
            <p class="ss-detail-value">${escapeHtml(qualityLabel(s.quality))}</p>
          </div>
        ` : ''}

        ${s.kropTekst ? `
          <div class="ss-detail-block">
            <p class="ss-detail-label">Hvad mærkede du i din egen krop?</p>
            <p class="ss-detail-value ss-detail-prose">${escapeHtml(s.kropTekst).replace(/\n/g, '<br>')}</p>
          </div>
        ` : ''}

        ${s.bevaegelseTekst ? `
          <div class="ss-detail-block">
            <p class="ss-detail-label">Hvad bevægede sig — og hvad blev?</p>
            <p class="ss-detail-value ss-detail-prose">${escapeHtml(s.bevaegelseTekst).replace(/\n/g, '<br>')}</p>
          </div>
        ` : ''}

        ${s.overraskelseTekst ? `
          <div class="ss-detail-block">
            <p class="ss-detail-label">Hvad overraskede dig?</p>
            <p class="ss-detail-value ss-detail-prose">${escapeHtml(s.overraskelseTekst).replace(/\n/g, '<br>')}</p>
          </div>
        ` : ''}
      </section>
      ${resonanceHtml}
    `;

    document.getElementById('ss-detail-back').addEventListener('click', () => {
      render();
    });
  }

  // ----- New entry flow -----

  function startNewEntry() {
    draft = {
      clientId: null,
      newAlias: '',
      zones: [],
      quality: null,
      kropTekst: '',
      bevaegelseTekst: '',
      overraskelseTekst: ''
    };
    currentStep = 0; // 0 = client picker, 1-5 = questions, 6 = saved
    render();
  }

  function cancelEntry() {
    if (!confirm('Forlad denne indførsel? Det du har skrevet bliver ikke gemt.')) return;
    draft = null;
    currentStep = 0;
    render();
  }

  function saveDraftToCurrentStep() {
    // Persist whatever is in the active inputs to draft, so we can navigate back/forth
    const stepEl = document.querySelector('[data-ss-step]');
    if (!stepEl) return;
    const step = parseInt(stepEl.dataset.ssStep, 10);

    if (step === 0) {
      // Client picker handled directly via clicks; nothing to persist here
    } else if (step === 1) {
      const checked = Array.from(stepEl.querySelectorAll('input[name="zone"]:checked'))
        .map(c => c.value);
      draft.zones = checked;
    } else if (step === 2) {
      const sel = stepEl.querySelector('input[name="quality"]:checked');
      draft.quality = sel ? sel.value : null;
    } else if (step === 3) {
      const ta = stepEl.querySelector('textarea');
      if (ta) draft.kropTekst = ta.value;
    } else if (step === 4) {
      const ta = stepEl.querySelector('textarea');
      if (ta) draft.bevaegelseTekst = ta.value;
    } else if (step === 5) {
      const ta = stepEl.querySelector('textarea');
      if (ta) draft.overraskelseTekst = ta.value;
    }
  }

  function renderEntryFlow() {
    if (currentStep === 6) {
      renderEntrySaved();
      return;
    }
    if (currentStep === 0) {
      renderClientPicker();
    } else {
      renderQuestion(currentStep);
    }
  }

  function renderClientPicker() {
    const newAliasShown = draft.newAlias !== '';

    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="0">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>

        <p class="ss-flow-progress">Før vi begynder</p>
        <p class="ss-flow-indledning">Et alias er kun for dig — fx initialer eller en kode du selv giver mening.</p>
        <h2 class="ss-flow-spoergsmaal">Hvem var i mødet?</h2>

        <div class="ss-client-list">
          ${state.clients.map(c => `
            <button class="ss-client-btn ${draft.clientId === c.id ? 'ss-client-btn-active' : ''}"
                    data-id="${escapeHtml(c.id)}">${escapeHtml(c.alias)}</button>
          `).join('')}
          <button class="ss-client-btn ss-client-btn-add" id="ss-client-add">+ Nyt alias</button>
        </div>

        <div class="ss-client-new ${newAliasShown ? '' : 'ss-hidden'}" id="ss-client-new-wrap">
          <input type="text" id="ss-client-new-input" class="ss-input" placeholder="Fx 'K1' eller initialer"
                 maxlength="20" value="${escapeHtml(draft.newAlias)}">
          <button class="ss-btn ss-btn-secondary" id="ss-client-new-save">Tilføj</button>
        </div>

        <p class="ss-flow-hjaelp">Du kan også springe over og lave indførslen uden alias.</p>

        <div class="ss-flow-actions">
          <button class="ss-btn ss-btn-secondary" id="ss-flow-skip">Spring over</button>
          <button class="ss-btn ss-btn-primary" id="ss-flow-next" ${draft.clientId ? '' : 'disabled'}>Næste</button>
        </div>
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);

    appEl.querySelectorAll('.ss-client-btn[data-id]').forEach(btn => {
      btn.addEventListener('click', () => {
        draft.clientId = btn.dataset.id;
        renderClientPicker();
      });
    });

    document.getElementById('ss-client-add').addEventListener('click', () => {
      draft.newAlias = ' ';
      renderClientPicker();
      const input = document.getElementById('ss-client-new-input');
      if (input) input.focus();
    });

    const newSave = document.getElementById('ss-client-new-save');
    if (newSave) {
      newSave.addEventListener('click', () => {
        const input = document.getElementById('ss-client-new-input');
        const alias = (input.value || '').trim();
        if (!alias) return;
        const id = uuid();
        state.clients.push({ id, alias, created: todayKey() });
        setState(state);
        draft.clientId = id;
        draft.newAlias = '';
        renderClientPicker();
      });
    }
    const newInput = document.getElementById('ss-client-new-input');
    if (newInput) {
      newInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          newSave.click();
        }
      });
    }

    document.getElementById('ss-flow-skip').addEventListener('click', () => {
      draft.clientId = null;
      currentStep = 1;
      render();
    });

    document.getElementById('ss-flow-next').addEventListener('click', () => {
      if (!draft.clientId) return;
      currentStep = 1;
      render();
    });
  }

  function renderQuestion(step) {
    if (step === 1) renderQ1();
    else if (step === 2) renderQ2();
    else if (step === 3) renderQ3();
    else if (step === 4) renderQ4();
    else if (step === 5) renderQ5();
  }

  function flowFooter(step) {
    const isLast = step === 5;
    return `
      <div class="ss-flow-actions">
        <button class="ss-btn ss-btn-secondary" id="ss-flow-back">Forrige</button>
        <button class="ss-btn ss-btn-primary" id="ss-flow-next">${isLast ? 'Gem indførsel' : 'Næste'}</button>
      </div>
    `;
  }

  function wireFlowFooter(step) {
    document.getElementById('ss-flow-back').addEventListener('click', () => {
      saveDraftToCurrentStep();
      currentStep = step - 1;
      render();
    });
    document.getElementById('ss-flow-next').addEventListener('click', () => {
      saveDraftToCurrentStep();
      if (step === 5) {
        completeEntry();
      } else {
        currentStep = step + 1;
        render();
      }
    });
  }

  function renderQ1() {
    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="1">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>
        <p class="ss-flow-progress">1 af 5</p>
        <p class="ss-flow-indledning">Lad billedet komme før ordet — hvor var arbejdet i dag?</p>
        <h2 class="ss-flow-spoergsmaal">Hvor levede dagens arbejde?</h2>

        <div class="ss-options">
          ${ZONES.map(z => `
            <label class="ss-option ${draft.zones.includes(z.id) ? 'ss-option-active' : ''}">
              <input type="checkbox" name="zone" value="${z.id}" ${draft.zones.includes(z.id) ? 'checked' : ''}>
              <span class="ss-option-label">${escapeHtml(z.label)}</span>
            </label>
          `).join('')}
        </div>

        <p class="ss-flow-hjaelp">Vælg den zone hvor mest af mødet udfoldede sig. Du kan også vælge to, hvis arbejdet bevægede sig.</p>

        ${flowFooter(1)}
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);

    // Limit checkbox til max 2
    appEl.querySelectorAll('input[name="zone"]').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = appEl.querySelectorAll('input[name="zone"]:checked');
        if (checked.length > 2) {
          cb.checked = false;
          return;
        }
        // Update visual state
        const label = cb.closest('.ss-option');
        if (label) {
          if (cb.checked) label.classList.add('ss-option-active');
          else label.classList.remove('ss-option-active');
        }
      });
    });

    wireFlowFooter(1);
  }

  function renderQ2() {
    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="2">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>
        <p class="ss-flow-progress">2 af 5</p>
        <p class="ss-flow-indledning">Ikke hvad du bragte med dig — men hvad mødet bad dig om.</p>
        <h2 class="ss-flow-spoergsmaal">Hvilken kvalitet blev du bedt om at bringe?</h2>

        <div class="ss-options">
          ${QUALITIES.map(q => `
            <label class="ss-option ${draft.quality === q.id ? 'ss-option-active' : ''}">
              <input type="radio" name="quality" value="${q.id}" ${draft.quality === q.id ? 'checked' : ''}>
              <span class="ss-option-label">${escapeHtml(q.label)}</span>
            </label>
          `).join('')}
        </div>

        <p class="ss-flow-hjaelp">Den der trådte tydeligst frem i mødet. Sjældent valgt — oftest kaldt på.</p>

        ${flowFooter(2)}
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);

    appEl.querySelectorAll('input[name="quality"]').forEach(rb => {
      rb.addEventListener('change', () => {
        appEl.querySelectorAll('.ss-option').forEach(l => l.classList.remove('ss-option-active'));
        const label = rb.closest('.ss-option');
        if (label) label.classList.add('ss-option-active');
      });
    });

    wireFlowFooter(2);
  }

  function renderQ3() {
    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="3">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>
        <p class="ss-flow-progress">3 af 5</p>
        <p class="ss-flow-indledning">Lad krop besvare først, ikke tanke.</p>
        <h2 class="ss-flow-spoergsmaal">Hvad mærkede du i din egen krop?</h2>

        <textarea class="ss-textarea" rows="6" placeholder="Få linjer er nok. Mærk inden du skriver — tempoet, tyngden, åndedrættet, det der trækker sig sammen, det der åbner sig. Hvad lever stadig i dig fra den session?">${escapeHtml(draft.kropTekst)}</textarea>

        ${flowFooter(3)}
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);
    wireFlowFooter(3);
  }

  function renderQ4() {
    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="4">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>
        <p class="ss-flow-progress">4 af 5</p>
        <p class="ss-flow-indledning">Ikke hvad du opnåede — hvad der skiftede rolle i feltet.</p>
        <h2 class="ss-flow-spoergsmaal">Hvad bevægede sig — og hvad blev?</h2>

        <textarea class="ss-textarea" rows="6" placeholder="Noget reorganiserede sig måske, mens andet stod stille. En holdning forvandlede sig, en spænding forblev. Begge dele bærer mening. Beskriv det du så.">${escapeHtml(draft.bevaegelseTekst)}</textarea>

        ${flowFooter(4)}
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);
    wireFlowFooter(4);
  }

  function renderQ5() {
    appEl.innerHTML = `
      <section class="ss-flow" data-ss-step="5">
        <button class="ss-btn-text ss-flow-cancel" id="ss-flow-cancel">‹ Afbryd</button>
        <p class="ss-flow-progress">5 af 5</p>
        <p class="ss-flow-indledning">Det modellen ikke fanger, lever ofte her.</p>
        <h2 class="ss-flow-spoergsmaal">Hvad overraskede dig?</h2>

        <textarea class="ss-textarea" rows="6" placeholder="En vending du ikke ventede. Et billede der dukkede op. En følelse der kom fra et andet sted end du regnede med. Lad det få plads — også selvom det ikke kan navngives helt.">${escapeHtml(draft.overraskelseTekst)}</textarea>

        ${flowFooter(5)}
      </section>
    `;

    document.getElementById('ss-flow-cancel').addEventListener('click', cancelEntry);
    wireFlowFooter(5);
  }

  function completeEntry() {
    // Spring over hvis der ikke er givet noget overhovedet
    const hasContent =
      (draft.zones && draft.zones.length > 0) ||
      draft.quality ||
      (draft.kropTekst || '').trim() ||
      (draft.bevaegelseTekst || '').trim() ||
      (draft.overraskelseTekst || '').trim();

    if (!hasContent) {
      if (!confirm('Indførslen er tom. Vil du gemme den alligevel?')) {
        return;
      }
    }

    const entry = {
      id: uuid(),
      clientId: draft.clientId || null,
      date: todayKey(),
      zones: (draft.zones || []).slice(),
      quality: draft.quality || null,
      kropTekst: (draft.kropTekst || '').trim(),
      bevaegelseTekst: (draft.bevaegelseTekst || '').trim(),
      overraskelseTekst: (draft.overraskelseTekst || '').trim()
    };

    state.sessions.push(entry);
    setState(state);

    currentStep = 6;
    render();
  }

  function renderEntrySaved() {
    // Den senest gemte indførsel — bruges til at beregne genklange
    const lastEntry = state.sessions[state.sessions.length - 1];
    const text = lastEntry ? combinedFreeText(lastEntry) : '';
    const resonanceHtml = renderResonanceCards(text);

    appEl.innerHTML = `
      <section class="ss-saved">
        <div class="ss-saved-symbol" aria-hidden="true">✦</div>
        <p class="ss-saved-text">Indførslen er gemt.</p>
      </section>
      ${resonanceHtml}
      <div class="ss-saved-actions">
        <button class="ss-btn ss-btn-primary" id="ss-saved-back">Tilbage til oversigten</button>
      </div>
    `;
    document.getElementById('ss-saved-back').addEventListener('click', () => {
      draft = null;
      currentStep = 0;
      render();
    });

    // Ingen auto-redirect — lad brugeren dvæle med genklangen
  }

  // ----- Init -----

  async function loadGenklangeData() {
    try {
      const [mtRes, roRes] = await Promise.all([
        fetch(MIKROTEKSTER_URL, { cache: 'no-cache' }),
        fetch(ORDBOG_URL, { cache: 'no-cache' })
      ]);
      if (mtRes.ok) {
        const mt = await mtRes.json();
        mikrotekster = mt.mikrotekster || [];
      }
      if (roRes.ok) {
        const ro = await roRes.json();
        resonansOrdbog = ro.resonans_ordbog || {};
      }
    } catch (e) {
      // Genklange er en tilføjelse — feature virker også uden
      console.warn('Genklange-data kunne ikke indlæses:', e);
    }
  }

  async function init() {
    appEl = document.getElementById('sessionsspejl-app');
    if (!appEl) return;
    state = loadStorage();
    // Load genklange-data først så resonansen er klar når brugeren gemmer
    await loadGenklangeData();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
