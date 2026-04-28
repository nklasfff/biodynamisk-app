// Det Levende Hierarki — interaktiv version af bogens summerende figur.
// Glowing orbs med radial gradient, tynde lysbuer, soft pulseren.
// Tap på en orb viser dens kvaliteter i detalje-panelet.

(function() {
  const NODES = {
    'emb': {
      titel: 'De Embryologiske Kræfter',
      level: 1,
      x: 190, y: 70, r: 22,
      label: 'embryologiske\nkræfter',
      bullets: [
        'De formative kræfter der skabte os',
        'De vedligeholdende kræfter gennem hele livet',
        'De helbredende kræfter når vi rammes'
      ]
    },
    'dyn': {
      titel: 'Dynamisk Stilhed',
      level: 2,
      x: 70, y: 230, r: 20,
      label: 'dynamisk\nstilhed',
      bullets: [
        'Livets arnested og oprindelse',
        'Det umanifesterede potentiale',
        'Skabelonen til selve livet'
      ]
    },
    'prm': {
      titel: 'Primary Respiration',
      level: 2,
      x: 190, y: 230, r: 20,
      label: 'primary\nrespiration',
      bullets: [
        'The Long Tide fra horisonten',
        'The Fluid Tide i væskekroppen',
        'Livets egen rytme og pulsering'
      ]
    },
    'hel': {
      titel: 'Kroppen som ubrudt helhed',
      level: 2,
      x: 310, y: 230, r: 20,
      label: 'ubrudt\nhelhed',
      bullets: [
        'Midtlinjen som organisator',
        'Sundheden som umistelig',
        'Kontinuerlig tilblivelse'
      ]
    },
    'neu': {
      titel: 'The Neutral',
      level: 3,
      x: 44, y: 430, r: 14,
      label: 'the\nneutral',
      bullets: [
        'Autonomt nervesystem suspenderes',
        'Kroppen som homogen tilstand',
        'Døren til heling åbnes'
      ]
    },
    'sti': {
      titel: 'Stillpoints opstår',
      level: 3,
      x: 117, y: 430, r: 14,
      label: 'still-\npoints',
      bullets: [
        'Terapeutiske processer indfinder sig',
        'Augmentation af kræfter',
        'Transformation sker fra balancepunktet'
      ]
    },
    'aut': {
      titel: 'Automatic Shifting',
      level: 3,
      x: 190, y: 430, r: 14,
      label: 'automatic\nshifting',
      bullets: [
        'Helhedens prioritering tager føringen',
        'Iboende behandlingsplan udfolder sig',
        'Systemisk organisering springer fra sted til sted'
      ]
    },
    'tra': {
      titel: 'Transmutation sker',
      level: 3,
      x: 263, y: 430, r: 14,
      label: 'trans-\nmutation',
      bullets: [
        'Alkymistisk forvandling af tilstand',
        'Væv til væske transformation',
        'Ignition af livets ild'
      ]
    },
    'vae': {
      titel: 'Væskekroppen vågner',
      level: 3,
      x: 336, y: 430, r: 14,
      label: 'væske-\nkroppen',
      bullets: [
        'Protoplasma-kvaliteter aktiveres',
        'Simultan respons gennem hele matrixen',
        'Levende kontinuum gennem organismen'
      ]
    },
    'gen': {
      titel: 'Helhedens genoprettelse',
      level: 4,
      x: 190, y: 620, r: 22,
      label: 'helhedens\ngenoprettelse',
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
    const W = 380, H = 720;

    // Forbindelser som bløde Q-kurver, tynde og lyse
    const edgesSVG = EDGES.map(([fromKey, toKey]) => {
      const a = NODES[fromKey], b = NODES[toKey];
      const startY = a.y + a.r + 4;
      const endY = b.y - b.r - 4;
      const midY = (startY + endY) / 2;
      // Q-curve med kontrolpunkter for blød bue
      return `<path d="M ${a.x} ${startY} C ${a.x} ${midY}, ${b.x} ${midY}, ${b.x} ${endY}"
        stroke="#faf4e8" stroke-width="0.35" fill="none" opacity="0.32"/>`;
    }).join('');

    // Orb-grupper: glowing aura + core, label under
    const orbsSVG = Object.entries(NODES).map(([key, n]) => {
      const lines = n.label.split('\n');
      const fontSize = n.level === 3 ? 9 : 10;
      const lineH = fontSize + 2;
      const labelStartY = n.y + n.r + 14;
      const auraR = n.r * 2.6;
      const innerR = n.r * 0.55;

      const labelLines = lines.map((line, idx) => `
        <text x="${n.x}" y="${labelStartY + idx * lineH}" text-anchor="middle"
              font-family="Cormorant Garamond, Georgia, serif"
              font-size="${fontSize}" font-style="italic"
              fill="#e8dfcf" opacity="0.7"
              class="hierarki-label" data-label="${key}">${line}</text>
      `).join('');

      return `
        <g class="hierarki-orb" data-key="${key}" onclick="HierarkiVis.tap('${key}')">
          <circle cx="${n.x}" cy="${n.y}" r="${auraR}"
                  fill="url(#aura-hier)" class="hierarki-aura" data-orb="${key}">
            <animate attributeName="r" values="${auraR};${auraR + 4};${auraR}" dur="8s"
                     repeatCount="indefinite" calcMode="spline"
                     keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}"
                  fill="url(#core-hier)" class="hierarki-core" data-orb="${key}">
            <animate attributeName="r" values="${n.r};${n.r + 2};${n.r}" dur="8s"
                     repeatCount="indefinite" calcMode="spline"
                     keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y - n.r * 0.15}" r="${innerR}"
                  fill="#faf4e8" opacity="0.55" class="hierarki-glow" data-orb="${key}"/>
          ${labelLines}
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="hierarki-svg" role="img" aria-label="Det levende hierarki">
        <defs>
          <radialGradient id="well-hier" cx="50%" cy="42%" r="65%">
            <stop offset="0%" stop-color="#2a3847"/>
            <stop offset="55%" stop-color="#1d2731"/>
            <stop offset="100%" stop-color="#141b22"/>
          </radialGradient>
          <radialGradient id="core-hier" cx="50%" cy="40%" r="55%">
            <stop offset="0%" stop-color="#faf4e8" stop-opacity="0.95"/>
            <stop offset="40%" stop-color="#f0e2c8" stop-opacity="0.55"/>
            <stop offset="80%" stop-color="#d4b98f" stop-opacity="0.18"/>
            <stop offset="100%" stop-color="#c9b8a0" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="aura-hier" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e8dfcf" stop-opacity="0.22"/>
            <stop offset="55%" stop-color="#a89880" stop-opacity="0.06"/>
            <stop offset="100%" stop-color="#a89880" stop-opacity="0"/>
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
    tap: function(key) {
      highlight(key);
      renderDetail(key);
    },
    init: function() {
      const container = document.getElementById('hierarki-svg-wrapper');
      if (!container) return;
      container.innerHTML = buildSVG();
      this.tap('emb');
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HierarkiVis.init());
  } else {
    HierarkiVis.init();
  }
})();
