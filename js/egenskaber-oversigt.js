// Egenskaber-oversigt — figur formet som en cirkel. Centrum-orb rummer
// "De essentielle egenskaber" som helhed. Otte orbs placeret harmonisk
// på cirklens streg ved 45° intervaller. Tynde streger mellem alle orbs
// indbyrdes plus radial streg fra hver perimeter-orb til centrum.
// Tap på en orb scroller automatisk til detalje-panelet.

(function() {
  const CX = 190;
  const CY = 240;
  const R_RING = 140;

  // Center + 8 perimeter-orbs ved 45° intervaller. Vinkel-rækkefølge
  // starter ved top (12 o'clock) og går med uret.
  const NODES = [
    {
      key: 'helhed', titel: 'De essentielle egenskaber', undertitel: 'helheden — det levende interface',
      role: 'center', x: CX, y: CY, r: 22, angle: null,
      bullets: [
        'De otte kvaliteter som ét sammenhængende felt',
        'Ingen kvalitet eksisterer alene — alle bærer hinanden',
        'Helheden danner behandlerens levende interface'
      ]
    },
    {
      key: 'e1', titel: 'Neutral lytten uden agenda', kortTitel: 'Neutral lytten', undertitel: 'rummet der lyttes ind i',
      role: 'ring', angle: 270, // 12 o'clock
      bullets: [
        'Tilstede uden at lede efter problemer',
        'Ingen forudbestemt protokol eller resultat',
        'Rummet holdes åbent for det der vil vise sig'
      ]
    },
    {
      key: 'e2', titel: 'Selvregulering af nervesystemet', kortTitel: 'Selvregulering', undertitel: 'fundamentet under alt',
      role: 'ring', angle: 315,
      bullets: [
        'Eget nervesystem reguleret under hele behandlingen',
        'Forbliver grounded selv ved klientens intensitet',
        'Fundament for relationel co-regulering'
      ]
    },
    {
      key: 'e3', titel: 'Sansning af den terapeutiske proces', kortTitel: 'Sansning af proces', undertitel: 'at følge frem for at føre',
      role: 'ring', angle: 0,
      bullets: [
        'Klart sanse skift, stillepunkter og reguleringer',
        'Følger processen frem for at lede den',
        'Mærker det subtile før det åbenbarer sig'
      ]
    },
    {
      key: 'e4', titel: 'Tålmodighed & uvished', kortTitel: 'Tålmodighed', undertitel: 'rummet hvor noget kan vise sig',
      role: 'ring', angle: 45,
      bullets: [
        'Hvile i ikke-vidende uden at fylde med intention',
        'Lade processen tage den tid den behøver',
        'Uvished som åbning, ikke mangel'
      ]
    },
    {
      key: 'e5', titel: 'At mærke helhedens prioritering', kortTitel: 'Helhedens prioritering', undertitel: 'systemets egen rækkefølge',
      role: 'ring', angle: 90,
      bullets: [
        'Kroppens egen rækkefølge for heling',
        'Slippe egen analyse til fordel for systemets logik',
        'Tillid til den iboende intelligens'
      ]
    },
    {
      key: 'e6', titel: 'Synkron bevægelse med kroppen', kortTitel: 'Synkron bevægelse', undertitel: 'dialogen i bevægelsen',
      role: 'ring', angle: 135,
      bullets: [
        'Følge kroppens bevægelser uden at føre eller modstå',
        'Match hvor vi mødes, ikke hvor vi vil hen',
        'Bevægelsen som dialog frem for handling'
      ]
    },
    {
      key: 'e7', titel: 'Kvalitet i berøringen', kortTitel: 'Berøringens kvalitet', undertitel: 'afstemt med øjeblikket',
      role: 'ring', angle: 180,
      bullets: [
        'Hverken for tung eller for fjern',
        'Afstemt med øjeblikkets udtryk',
        'Berøringen taler før ordene'
      ]
    },
    {
      key: 'e8', titel: 'Sans for behandlingens rytme', kortTitel: 'Behandlingens rytme', undertitel: 'naturlig vekslen i tid',
      role: 'ring', angle: 225,
      bullets: [
        'Mærke start, intensitet og afrunding',
        'Hvile og bevægelse i naturlig vekslen',
        'Behandlingens egen tempo respekteret'
      ]
    }
  ];

  // Beregn x/y for ring-orbs ud fra angle
  NODES.forEach(n => {
    if (n.role === 'ring') {
      const rad = n.angle * Math.PI / 180;
      n.x = Math.round(CX + R_RING * Math.cos(rad));
      n.y = Math.round(CY + R_RING * Math.sin(rad));
      n.r = 14;
    }
  });

  const W = 380;
  const H = 480;

  function buildEdges() {
    const ring = NODES.filter(n => n.role === 'ring');
    const center = NODES.find(n => n.role === 'center');
    const edges = [];
    // Alle ring-orbs forbundet to og to (28 edges)
    for (let i = 0; i < ring.length; i++) {
      for (let j = i + 1; j < ring.length; j++) {
        edges.push([ring[i], ring[j]]);
      }
    }
    // Hver ring-orb forbundet til centrum (8 edges)
    ring.forEach(r => edges.push([r, center]));
    return edges;
  }

  function buildSVG() {
    const edges = buildEdges();

    const edgesSVG = edges.map(([a, b]) => {
      // Trim linjen så den ikke går ind i orben
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const len = Math.sqrt(dx * dx + dy * dy);
      const ux = dx / len;
      const uy = dy / len;
      const x1 = a.x + ux * (a.r + 2);
      const y1 = a.y + uy * (a.r + 2);
      const x2 = b.x - ux * (b.r + 2);
      const y2 = b.y - uy * (b.r + 2);
      return `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
        stroke="#c4d0dc" stroke-width="0.3" opacity="0.18"/>`;
    }).join('');

    // Den ydre cirkel som tynde glødende ring (passerer gennem alle 8 orbs)
    const ringPath = `<circle cx="${CX}" cy="${CY}" r="${R_RING}" fill="none"
      stroke="#c4d0dc" stroke-width="0.5" opacity="0.32"/>`;

    const orbsSVG = NODES.map((n, idx) => {
      const auraR = Math.round(n.r * 4);
      // Label-position: udenfor orben i radial retning, men labels ved
      // venstre og højre kant flyttes indenfor cirklen så de ikke clippes.
      let labelX, labelY, labelAnchor = 'middle';
      if (n.role === 'center') {
        labelX = n.x;
        labelY = n.y + n.r + 22;
      } else if (n.angle === 0) {
        // Højre — label til venstre for orben (indad)
        labelX = n.x - n.r - 8;
        labelY = n.y + 4;
        labelAnchor = 'end';
      } else if (n.angle === 180) {
        // Venstre — label til højre for orben (indad)
        labelX = n.x + n.r + 8;
        labelY = n.y + 4;
        labelAnchor = 'start';
      } else if (n.angle === 270) {
        // Top — label over orben
        labelX = n.x;
        labelY = n.y - n.r - 12;
      } else if (n.angle === 90) {
        // Bund — label under orben
        labelX = n.x;
        labelY = n.y + n.r + 16;
      } else {
        // Diagonaler (45/135/225/315) — udadgående
        const rad = n.angle * Math.PI / 180;
        const labelDist = n.r + 14;
        labelX = Math.round(n.x + labelDist * Math.cos(rad));
        labelY = Math.round(n.y + labelDist * Math.sin(rad));
        if (Math.cos(rad) > 0.3) labelAnchor = 'start';
        else if (Math.cos(rad) < -0.3) labelAnchor = 'end';
      }

      // Wrap titel hvis lang — break ved naturligt sted. Bruger kort-titel
      // hvor den findes (perimeter-orbs) så labels passer indenfor SVG.
      const labelText = n.kortTitel || n.titel;
      const lines = wrapTitle(labelText, n.role === 'center' ? 22 : 16);
      const labelTexts = lines.map((line, i) => `
        <text x="${labelX}" y="${labelY + i * 12}" text-anchor="${labelAnchor}"
              font-family="Cormorant Garamond, Georgia, serif"
              font-size="${n.role === 'center' ? 11 : 10}" font-style="italic"
              fill="#c4d0dc" opacity="0.9">${line}</text>
      `).join('');

      return `
        <g class="egen-orb egen-orb-${n.role}" data-key="${n.key}" onclick="EgenskaberOversigt.tap('${n.key}', true)">
          <circle cx="${n.x}" cy="${n.y}" r="${auraR}" fill="url(#egen-aura)" class="egen-aura">
            <animate attributeName="r" values="${auraR};${auraR + 6};${auraR}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.5).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="url(#egen-core)" class="egen-core">
            <animate attributeName="r" values="${n.r};${n.r + 2};${n.r}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.5).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          ${labelTexts}
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="egen-svg" role="img" aria-label="De 8 essentielle egenskaber">
        <defs>
          <radialGradient id="egen-well" cx="50%" cy="50%" r="65%">
            <stop offset="0%" stop-color="#1f2a35"/>
            <stop offset="55%" stop-color="#131a22"/>
            <stop offset="100%" stop-color="#0c1218"/>
          </radialGradient>
          <radialGradient id="egen-core" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#f2f7fb" stop-opacity="1"/>
            <stop offset="30%" stop-color="#c4d0dc" stop-opacity="0.75"/>
            <stop offset="70%" stop-color="#8fa3b8" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#5e748a" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="egen-aura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#b8c5d3" stop-opacity="0.28"/>
            <stop offset="55%" stop-color="#7a8b9c" stop-opacity="0.08"/>
            <stop offset="100%" stop-color="#7a8b9c" stop-opacity="0"/>
          </radialGradient>
        </defs>

        <rect x="0" y="0" width="${W}" height="${H}" fill="url(#egen-well)"/>

        <!-- Cirklen — gennem alle 8 perimeter-orbs -->
        ${ringPath}

        <!-- Streger mellem alle orbs — danner et stjernemønster -->
        ${edgesSVG}

        <!-- Orbs (oven på stregerne) -->
        ${orbsSVG}
      </svg>
    `;
  }

  // Naiv ord-wrap til labels
  function wrapTitle(titel, maxChars) {
    const words = titel.split(' ');
    const lines = [''];
    words.forEach(w => {
      const last = lines[lines.length - 1];
      if ((last + ' ' + w).trim().length > maxChars) lines.push(w);
      else lines[lines.length - 1] = (last ? last + ' ' : '') + w;
    });
    return lines.filter(Boolean);
  }

  function renderDetail(key) {
    const n = NODES.find(x => x.key === key);
    if (!n) return;
    const panel = document.getElementById('egenskaber-detail');
    if (!panel) return;
    panel.innerHTML = `
      <h3 class="egen-detail-titel">${n.titel}</h3>
      ${n.undertitel ? `<p class="egen-detail-undertitel">${n.undertitel}</p>` : ''}
      <ul class="egen-detail-list">
        ${n.bullets.map(b => `<li>${b}</li>`).join('')}
      </ul>
    `;
  }

  function highlight(key) {
    document.querySelectorAll('.egen-orb').forEach(g => {
      g.classList.toggle('selected', g.dataset.key === key);
    });
  }

  window.EgenskaberOversigt = {
    tap: function(key, scroll) {
      highlight(key);
      renderDetail(key);
      if (scroll) {
        const panel = document.getElementById('egenskaber-detail');
        if (panel) {
          const rect = panel.getBoundingClientRect();
          const targetY = (window.pageYOffset || document.documentElement.scrollTop) + rect.top - 24;
          try { window.scrollTo({ top: targetY, behavior: 'smooth' }); } catch (e) {}
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
      const wrapper = document.getElementById('egenskaber-svg-wrapper');
      if (!wrapper) return;
      wrapper.innerHTML = buildSVG();
      this.tap('helhed', false);
    }
  };
})();
