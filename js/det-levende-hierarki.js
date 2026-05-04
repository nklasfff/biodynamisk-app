// Det Levende Liv — interaktiv version af bogens summerende figur.
// Glowing orbs med radial gradient, tynde lysbuer, soft pulseren.
// Tap på en orb viser dens kvaliteter i detalje-panelet og scroller ned dertil.

(function() {
  const NODES = {
    // ======= Række 1 (top) — Dynamisk Stilhed =======
    'dyn': {
      titel: 'Dynamisk Stilhed',
      level: 1,
      x: 190, y: 60, r: 22,
      label: 'dynamisk\nstilhed',
      bullets: [
        'Livets arnested og oprindelse',
        'Det umanifesterede potentiale',
        'Skabelonen til selve livet',
        'Den absolutte stilhed hvorfra Breath of Life udspringer',
        'Berøres kun i sjældne øjeblikke af nåde'
      ]
    },

    // ======= Række 2 — Breath of Life · Embryologiske Kræfter · Ubrudt Helhed =======
    'bre': {
      titel: 'Breath of Life',
      level: 2,
      x: 80, y: 180, r: 20,
      label: 'breath\nof life',
      bullets: [
        'Den første manifestation fra Dynamisk Stilhed',
        'Bærer alle livets formgivende impulser',
        'Driver Primary Respiration’s evige rytmer',
        'Det formative åndedræt der bevæger alt',
        'Kilden til al biologisk udfoldelse'
      ]
    },
    'emb': {
      titel: 'De Embryologiske Kræfter',
      level: 2,
      x: 190, y: 180, r: 20,
      label: 'embryologiske\nkræfter',
      bullets: [
        'De formative kræfter der skabte os',
        'De vedligeholdende kræfter gennem hele livet',
        'De helbredende kræfter når vi rammes',
        'Det kontinuerlige bagtæppe for al biologisk udfoldelse',
        'Den iboende intelligens der tager føringen i terapeutiske processer'
      ]
    },
    'wh': {
      titel: 'Ubrudt Helhed',
      level: 2,
      x: 300, y: 180, r: 20,
      label: 'ubrudt\nhelhed',
      bullets: [
        'Kroppen som integreret aspekt af livet selv',
        'Sundheden som umistelig skabelon',
        'Kontinuerlig tilblivelse fra øjeblik til øjeblik',
        'Helheden prioriterer altid sin egen integritet',
        'Skabelonen forbliver intakt under alle vilkår'
      ]
    },

    // ======= Række 3 — Primary Respiration · Væskekroppen · The Long Tide · Midtlinjen =======
    'prm': {
      titel: 'Primary Respiration',
      level: 3,
      x: 70, y: 300, r: 14,
      label: 'primary\nrespiration',
      bullets: [
        'The Long Tide fra horisonten',
        'The Fluid Tide i væskekroppen',
        'Livets egen rytme og pulsering',
        'Bærer den iboende behandlingsplan',
        'Synkroniseringen til Motion Present'
      ]
    },
    'vae': {
      titel: 'Væskekroppen',
      level: 3,
      x: 150, y: 300, r: 14,
      label: 'væske-\nkroppen',
      bullets: [
        'Protoplasma-kvaliteter aktiveres',
        'Simultan respons gennem hele matrixen',
        'Levende kontinuum gennem organismen',
        'Væsken inden i væsken kommer til udtryk',
        'Kroppen bliver gennemstrømmelig for Primary Respiration'
      ]
    },
    'lng': {
      titel: 'The Long Tide',
      level: 3,
      x: 230, y: 300, r: 14,
      label: 'the long\ntide',
      bullets: [
        'Den lange, dybe rytme fra horisonten',
        'Universelle bevægelser der overtager opmærksomheden',
        'Bærer den iboende behandlingsplan',
        'Det dybeste lag af Primary Respiration',
        'Kontakten til den oprindelige stemme'
      ]
    },
    'mid': {
      titel: 'Midtlinjen',
      level: 3,
      x: 310, y: 300, r: 14,
      label: 'midt-\nlinjen',
      bullets: [
        'Den centrale organiserende akse gennem livet',
        'Bærer alle kroppens strukturer og funktioner',
        'Optimal fulcrum for kroppens normalisering',
        'Reference for al ubevidst organisering',
        'Kontinuitet fra konception til afslutning'
      ]
    },

    // ======= Række 4 — The Health · Axial Fluctuations · Potency · Ignition =======
    'hea': {
      titel: 'The Health',
      level: 4,
      x: 70, y: 420, r: 16,
      label: 'the\nhealth',
      bullets: [
        'Den umistelige skabelon for optimal funktion',
        'Altid intakt — uafhængig af læsioner',
        'Sundhedens skabelon kommunikerer altid',
        'Vejviseren tilbage til oprindelig konfiguration',
        'Latent potentiale i hver tilstand'
      ]
    },
    'axf': {
      titel: 'Axial Fluctuations',
      level: 4,
      x: 150, y: 420, r: 16,
      label: 'axial\nfluctuations',
      bullets: [
        'Longitudinale bevægelser langs midtlinjen',
        'Laterale bevægelser perpendikulært til aksen',
        'Organiseringen af bevægelse om midtlinjen',
        'Den dybe rytme i kraniets motilitet',
        'Sansningen af kroppens iboende koordinater'
      ]
    },
    'pot': {
      titel: 'Potency',
      level: 4,
      x: 230, y: 420, r: 16,
      label: 'potency',
      bullets: [
        'Livskraften som koncentreret essens',
        '"Væsken inden i væsken" — Sutherlands beskrivelse',
        'Den skabende kraft bundet i læsionsfeltet',
        'Frigøres når sundheden mødes uden tvang',
        'Som ild eller elektricitet i vandet'
      ]
    },
    'ign': {
      titel: 'Ignition',
      level: 4,
      x: 310, y: 420, r: 16,
      label: 'ignition',
      bullets: [
        'Antændelsen af Primary Respiration',
        'Sundhedens mønster genoprettes',
        'Livets ild aktiveres gennem midtlinjen',
        'Det øjeblik hvor systemet vågner',
        'Forløsningen af bunden potency'
      ]
    },

    // ======= Række 5 — Transmutation · Fulcrum · The Neutral · Stillpoints =======
    'tra': {
      titel: 'Transmutation',
      level: 5,
      x: 70, y: 540, r: 16,
      label: 'trans-\nmutation',
      bullets: [
        'Alkymistisk forvandling af tilstand',
        'Væv til væske transformation',
        'Ignition af livets ild',
        'Selve vævets natur ændres på fundamentalt niveau',
        'Det der var bundet bliver levende igen'
      ]
    },
    'ful': {
      titel: 'Fulcrum',
      level: 5,
      x: 150, y: 540, r: 16,
      label: 'fulcrum',
      bullets: [
        'Omdrejningspunkt hvorom bevægelse organiseres',
        'Stabile punkter i kroppens dynamiske felt',
        'Kan være anatomiske eller dynamiske',
        'Naturligt fulcrum i midtlinjen',
        'Referencepunkt for al heling'
      ]
    },
    'neu': {
      titel: 'The Neutral',
      level: 5,
      x: 230, y: 540, r: 16,
      label: 'the\nneutral',
      bullets: [
        'Autonomt nervesystem suspenderes',
        'Kroppen som homogen tilstand',
        'Døren til heling åbnes',
        'Lagene smelter sammen til én substans',
        'Kvaliteten kender vi fra at glide ind i søvnen'
      ]
    },
    'sti': {
      titel: 'Stillpoints',
      level: 5,
      x: 310, y: 540, r: 16,
      label: 'still-\npoints',
      bullets: [
        'Terapeutiske processer indfinder sig',
        'Augmentation af kræfter',
        'Transformation sker fra balancepunktet',
        'Bevægelsens omdrejningspunkter åbner mod heling',
        'Korte eller dybe — hver med sin egen dynamik'
      ]
    },

    // ======= Række 6 — Motion Present · Iboende Behandlingsplan · Automatic Shifting · The Lesion Field =======
    'mot': {
      titel: 'Motion Present',
      level: 6,
      x: 70, y: 660, r: 16,
      label: 'motion\npresent',
      bullets: [
        'Alle kroppens nuværende bevægelser',
        'Metabolske, autonome og embryologiske rytmer',
        'Det øjebliks udtryk vi synkroniserer med',
        'Indgangen til den biodynamiske dialog',
        'Behandlerens første kontaktpunkt'
      ]
    },
    'ibe': {
      titel: 'Den Iboende Behandlingsplan',
      level: 6,
      x: 150, y: 660, r: 16,
      label: 'iboende\nplan',
      bullets: [
        'Kroppens egen prioritering af heling',
        'Dybere logik end behandlerens analyse',
        'Helhedens iboende intelligens',
        'Kommer til udtryk gennem Automatic Shifting',
        'Den vej kroppen vælger selv'
      ]
    },
    'aut': {
      titel: 'Automatic Shifting',
      level: 6,
      x: 230, y: 660, r: 16,
      label: 'automatic\nshifting',
      bullets: [
        'Helhedens prioritering tager føringen',
        'Iboende behandlingsplan udfolder sig',
        'Systemisk organisering springer fra sted til sted',
        'Behandleren slipper sin egen plan',
        'Re-organisering følger en dybere logik'
      ]
    },
    'les': {
      titel: 'The Lesion Field',
      level: 6,
      x: 310, y: 660, r: 16,
      label: 'lesion\nfield',
      bullets: [
        'Det fastlåste energetiske felt',
        'Bunden potency og struktureret kraft',
        'Mønster fra tidligere overvældelse',
        'Indeholder både skade og kommunikation',
        'Forløses når sundheden mødes uden tvang'
      ]
    },

    // ======= Række 7 (bund) — Helhedens Genoprettelse =======
    'gen': {
      titel: 'Helhedens Genoprettelse',
      level: 7,
      x: 190, y: 790, r: 22,
      label: 'helhedens\ngenoprettelse',
      bullets: [
        'Kroppen vender tilbage til sin oprindelige skabelon',
        'Motion Present genopretter forbindelse til Sundheden',
        'Midtlinjen etablerer sig som naturligt fulcrum',
        'Læsionsfeltet løses op og kraften vender hjem',
        'Klienten lever ikke længere rundt om sit mønster'
      ]
    }
  };

  // Forbindelser: hver orb forbindes til ALLE orbs i rækken under sig.
  // Genereres dynamisk ved at gruppere noder efter y-koordinat (række).
  function buildEdges() {
    const byRow = {};
    Object.keys(NODES).forEach(key => {
      const y = NODES[key].y;
      if (!byRow[y]) byRow[y] = [];
      byRow[y].push(key);
    });
    const rowYs = Object.keys(byRow).map(Number).sort((a, b) => a - b);
    const edges = [];
    for (let i = 0; i < rowYs.length - 1; i++) {
      const upper = byRow[rowYs[i]];
      const lower = byRow[rowYs[i + 1]];
      upper.forEach(u => lower.forEach(l => edges.push([u, l])));
    }
    return edges;
  }
  const EDGES = buildEdges();

  function buildSVG() {
    const W = 380, H = 870;

    // Forbindelser som bløde C-kurver, tynde og lyse
    const edgesSVG = EDGES.map(([fromKey, toKey]) => {
      const a = NODES[fromKey], b = NODES[toKey];
      const startY = a.y + a.r + 4;
      const endY = b.y - b.r - 4;
      const midY = (startY + endY) / 2;
      return `<path d="M ${a.x} ${startY} C ${a.x} ${midY}, ${b.x} ${midY}, ${b.x} ${endY}"
        stroke="#f8f8f8" stroke-width="0.3" fill="none" opacity="0.20"/>`;
    }).join('');

    // Orb-grupper: blød aura + diffus core, label under.
    const orbsSVG = Object.entries(NODES).map(([key, n]) => {
      const lines = n.label.split('\n');
      const fontSize = (n.r >= 20) ? 10 : (n.r >= 16) ? 9.5 : 9;
      const lineH = fontSize + 2;
      const labelStartY = n.y + n.r + 16;
      const auraR = Math.round(n.r * 4);

      const labelLines = lines.map((line, idx) => `
        <text x="${n.x}" y="${labelStartY + idx * lineH}" text-anchor="middle"
              font-family="Cormorant Garamond, Georgia, serif"
              font-size="${fontSize}" font-style="italic"
              fill="#dcdcdc" opacity="0.7"
              class="hierarki-label" data-label="${key}">${line}</text>
      `).join('');

      return `
        <g class="hierarki-orb" data-key="${key}" onclick="HierarkiVis.tap('${key}', true)">
          <circle cx="${n.x}" cy="${n.y}" r="${auraR}"
                  fill="url(#aura-hier)" class="hierarki-aura" data-orb="${key}">
            <animate attributeName="r" values="${auraR};${auraR + 6};${auraR}" dur="8s"
                     repeatCount="indefinite" calcMode="spline"
                     keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}"
                  fill="url(#core-hier)" class="hierarki-core" data-orb="${key}">
            <animate attributeName="r" values="${n.r};${n.r + 3};${n.r}" dur="8s"
                     repeatCount="indefinite" calcMode="spline"
                     keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          ${labelLines}
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="hierarki-svg" role="img" aria-label="Det Levende Liv">
        <defs>
          <radialGradient id="well-hier" cx="50%" cy="42%" r="65%">
            <stop offset="0%" stop-color="#2a3847"/>
            <stop offset="55%" stop-color="#1d2731"/>
            <stop offset="100%" stop-color="#141b22"/>
          </radialGradient>
          <radialGradient id="core-hier" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#f8f8f8" stop-opacity="1"/>
            <stop offset="30%" stop-color="#e0e0e0" stop-opacity="0.75"/>
            <stop offset="70%" stop-color="#b0b0b0" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#b0b0b0" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="aura-hier" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#dcdcdc" stop-opacity="0.28"/>
            <stop offset="55%" stop-color="#909090" stop-opacity="0.08"/>
            <stop offset="100%" stop-color="#909090" stop-opacity="0"/>
          </radialGradient>
        </defs>

        <rect x="0" y="0" width="${W}" height="${H}" fill="url(#well-hier)"/>

        ${edgesSVG}
        ${orbsSVG}
      </svg>
    `;
  }

  function renderDetail(key) {
    const n = NODES[key];
    if (!n) return;
    const panel = document.getElementById('hierarki-detail');
    panel.innerHTML = `
      <h3 class="hierarki-detail-titel">${n.titel}</h3>
      <ul class="hierarki-detail-list">
        ${n.bullets.map(b => `<li>${b}</li>`).join('')}
      </ul>
    `;
  }

  function highlight(key) {
    document.querySelectorAll('.hierarki-orb').forEach(g => {
      g.classList.toggle('selected', g.dataset.key === key);
    });
  }

  window.HierarkiVis = {
    tap: function(key, scroll) {
      highlight(key);
      renderDetail(key);
      if (scroll) {
        const panel = document.getElementById('hierarki-detail');
        if (panel) {
          const rect = panel.getBoundingClientRect();
          const targetY = (window.pageYOffset || document.documentElement.scrollTop) + rect.top - 24;
          try {
            window.scrollTo({ top: targetY, behavior: 'smooth' });
          } catch (e) {}
          setTimeout(() => {
            const r = panel.getBoundingClientRect();
            if (r.top > 80) {
              window.scrollTo(0, (window.pageYOffset || 0) + r.top - 24);
            }
          }, 50);
        }
      }
    },
    init: function() {
      const container = document.getElementById('hierarki-svg-wrapper');
      if (!container) return;
      container.innerHTML = buildSVG();
      this.tap('dyn', false);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HierarkiVis.init());
  } else {
    HierarkiVis.init();
  }
})();
