// Det Levende Hierarki — interaktiv version af bogens summerende figur.
// 4 niveauer + forbindelser. Tap på en orb viser dens kvaliteter i detalje-panelet.

(function() {
  const NODES = {
    'emb': {
      titel: 'De Embryologiske Kræfter',
      level: 1,
      x: 190, y: 70, r: 38,
      kort: 'EMBRYOLOGISKE\nKRÆFTER',
      bullets: [
        'De formative kræfter der skabte os',
        'De vedligeholdende kræfter gennem hele livet',
        'De helbredende kræfter når vi rammes'
      ]
    },
    'dyn': {
      titel: 'Dynamisk Stilhed',
      level: 2,
      x: 70, y: 220, r: 34,
      kort: 'DYNAMISK\nSTILHED',
      bullets: [
        'Livets arnested og oprindelse',
        'Det umanifesterede potentiale',
        'Skabelonen til selve livet'
      ]
    },
    'prm': {
      titel: 'Primary Respiration',
      level: 2,
      x: 190, y: 220, r: 34,
      kort: 'PRIMARY\nRESPIRATION',
      bullets: [
        'The Long Tide fra horisonten',
        'The Fluid Tide i væskekroppen',
        'Livets egen rytme og pulsering'
      ]
    },
    'hel': {
      titel: 'Kroppen som ubrudt helhed',
      level: 2,
      x: 310, y: 220, r: 34,
      kort: 'UBRUDT\nHELHED',
      bullets: [
        'Midtlinjen som organisator',
        'Sundheden som umistelig',
        'Kontinuerlig tilblivelse'
      ]
    },
    'neu': {
      titel: 'The Neutral',
      level: 3,
      x: 50, y: 400, r: 28,
      kort: 'THE\nNEUTRAL',
      bullets: [
        'Autonomt nervesystem suspenderes',
        'Kroppen som homogen tilstand',
        'Døren til heling åbnes'
      ]
    },
    'sti': {
      titel: 'Stillpoints opstår',
      level: 3,
      x: 120, y: 400, r: 28,
      kort: 'STILL-\nPOINTS',
      bullets: [
        'Terapeutiske processer indfinder sig',
        'Augmentation af kræfter',
        'Transformation sker fra balancepunktet'
      ]
    },
    'aut': {
      titel: 'Automatic Shifting',
      level: 3,
      x: 190, y: 400, r: 28,
      kort: 'AUTOMATIC\nSHIFTING',
      bullets: [
        'Helhedens prioritering tager føringen',
        'Iboende behandlingsplan udfolder sig',
        'Systemisk organisering springer fra sted til sted'
      ]
    },
    'tra': {
      titel: 'Transmutation sker',
      level: 3,
      x: 260, y: 400, r: 28,
      kort: 'TRANS-\nMUTATION',
      bullets: [
        'Alkymistisk forvandling af tilstand',
        'Væv til væske transformation',
        'Ignition af livets ild'
      ]
    },
    'vae': {
      titel: 'Væskekroppen vågner',
      level: 3,
      x: 330, y: 400, r: 28,
      kort: 'VÆSKE-\nKROPPEN',
      bullets: [
        'Protoplasma-kvaliteter aktiveres',
        'Simultan respons gennem hele matrixen',
        'Levende kontinuum gennem organismen'
      ]
    },
    'gen': {
      titel: 'Helhedens genoprettelse',
      level: 4,
      x: 190, y: 580, r: 38,
      kort: 'HELHEDENS\nGENOPR.',
      bullets: [
        'Kroppen vender tilbage til sin oprindelige skabelon',
        'Motion Present genopretter forbindelse til Sundheden',
        'Midtlinjen etablerer sig som naturligt fulcrum'
      ]
    }
  };

  // Forbindelser: parent → children
  const EDGES = [
    ['emb', 'dyn'], ['emb', 'prm'], ['emb', 'hel'],
    ['dyn', 'neu'], ['dyn', 'sti'],
    ['prm', 'aut'],
    ['hel', 'tra'], ['hel', 'vae'],
    ['neu', 'gen'], ['sti', 'gen'], ['aut', 'gen'], ['tra', 'gen'], ['vae', 'gen']
  ];

  function buildSVG() {
    const W = 380, H = 680;

    // Build path for hver edge — blød kurve fra parent til child
    const edgesSVG = EDGES.map(([fromKey, toKey], i) => {
      const a = NODES[fromKey], b = NODES[toKey];
      const dy = b.y - a.y;
      const cpY = a.y + dy * 0.55;
      // Q-curve med kontrolpunkt mellem
      return `<path d="M ${a.x} ${a.y + a.r - 2} Q ${a.x} ${cpY}, ${(a.x + b.x) / 2} ${cpY} T ${b.x} ${b.y - b.r + 2}"
        stroke="#a89880" stroke-width="0.6" fill="none" opacity="0.35"/>`;
    }).join('');

    // Build orb-grupper
    const orbsSVG = Object.entries(NODES).map(([key, n]) => {
      const lines = n.kort.split('\n');
      const fontSize = n.level === 1 || n.level === 4 ? 9 : (n.level === 2 ? 8 : 7);
      const lineH = fontSize + 2;
      const startY = n.y - ((lines.length - 1) * lineH) / 2 + fontSize / 3;
      const labels = lines.map((line, idx) => `
        <text x="${n.x}" y="${startY + idx * lineH}" text-anchor="middle"
              font-family="Cinzel, serif" font-size="${fontSize}" font-weight="300"
              letter-spacing="1.2" fill="#3a2818" opacity="0.92">${line}</text>
      `).join('');

      return `
        <g class="hierarki-orb" data-key="${key}" onclick="HierarkiVis.tap('${key}')">
          <circle cx="${n.x}" cy="${n.y}" r="${n.r + 6}" fill="url(#aura-hier)" class="hierarki-aura" data-orb="${key}"/>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="url(#orb-hier)" stroke="#c9b8a0" stroke-width="0.5" class="hierarki-circle" data-orb="${key}"/>
          ${labels}
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="hierarki-svg" role="img" aria-label="Det levende hierarki">
        <defs>
          <radialGradient id="orb-hier" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stop-color="#faf4e8" stop-opacity="1"/>
            <stop offset="55%" stop-color="#f0e2c8" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#d4b98f" stop-opacity="0.5"/>
          </radialGradient>
          <radialGradient id="aura-hier" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e8dfcf" stop-opacity="0.35"/>
            <stop offset="60%" stop-color="#a89880" stop-opacity="0.1"/>
            <stop offset="100%" stop-color="#a89880" stop-opacity="0"/>
          </radialGradient>
        </defs>

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
    panel.classList.add('active');
  }

  function highlight(key) {
    document.querySelectorAll('.hierarki-circle').forEach(c => {
      c.classList.toggle('selected', c.dataset.orb === key);
    });
    document.querySelectorAll('.hierarki-aura').forEach(c => {
      c.classList.toggle('selected', c.dataset.orb === key);
    });
  }

  window.HierarkiVis = {
    tap: function(key) {
      highlight(key);
      renderDetail(key);
    },
    init: function() {
      const container = document.getElementById('hierarki-svg-wrapper');
      if (!container) return;
      container.innerHTML = buildSVG();
      // Vis intro-bullet i detalje-panelet ved start
      this.tap('emb');
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HierarkiVis.init());
  } else {
    HierarkiVis.init();
  }
})();
