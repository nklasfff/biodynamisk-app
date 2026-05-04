// Perspektiver-oversigt — figur formet som et øje. Pupillen i midten
// rummer "De 7 Perspektiver" som helhed. Øvre øjelåg bærer de tre første
// perspektiver, nedre øjelåg de fire sidste. Tap på en orb for at se
// essensen, og figuren scroller automatisk til detalje-panelet.

(function() {
  // De 7 perspektiver + central pupil. Positionerne danner et øje:
  // - 3 orbs på øvre øjelåg, evenly spaced (t=0.25, 0.5, 0.75)
  // - 4 orbs på nedre øjelåg, evenly spaced (t=0.2, 0.4, 0.6, 0.8)
  // - 1 stor orb i centrum som pupil
  const NODES = [
    {
      key: 'helhed', titel: 'De 7 Perspektiver', undertitel: 'pupillen — det samlede blik',
      x: 190, y: 240, r: 22, role: 'pupil',
      bullets: [
        'Et samlet udtryk for transformationens mange dimensioner',
        'Spiralen hvor hvert perspektiv fører naturligt til det næste',
        'Helheden afsløres når alle syv ses sammen'
      ]
    },
    // Øvre øjelåg — perspektiver 1, 2, 3
    {
      key: 'p1', titel: 'Barnets Øjne og Livets Tempo', undertitel: 'i transformationens væv',
      x: 105, y: 141, r: 14, role: 'upper',
      bullets: [
        'Friske øjne der ikke er filtreret af fortiden',
        'Livets eget tempo følges, ikke forceres',
        'Konstant berøring og berigelse fra alle aspekter'
      ]
    },
    {
      key: 'p2', titel: 'Stilhedens Skabende Kraft', undertitel: 'fra ikke-form til form',
      x: 190, y: 100, r: 14, role: 'upper',
      bullets: [
        'Stilheden som ikke er fravær, men kreativ kilde',
        'Det u-manifesterede potentiale altid til stede',
        'Fra stilheden udspringer al manifestation'
      ]
    },
    {
      key: 'p3', titel: 'Modenhedens Samtidige Lag', undertitel: 'begynderen og mesteren i ét',
      x: 275, y: 141, r: 14, role: 'upper',
      bullets: [
        'Begynderens åbenhed og mesterens nuancer samtidigt',
        'Modenhed inkluderer alle stadier vi har været i',
        'Hver omdrejning bringer dybere integration'
      ]
    },
    // Nedre øjelåg — perspektiver 4, 5, 6, 7
    {
      key: 'p4', titel: 'Bevægelsens Paradoks', undertitel: 'stilhed og bevægelse i ét',
      x: 88, y: 322, r: 14, role: 'lower',
      bullets: [
        'Stilstand og bevægelse som samme grundtilstand',
        'At være ankret er ikke at være statisk',
        'Den dybeste bevægelse opstår fra stilhed'
      ]
    },
    {
      key: 'p5', titel: 'At Blive Fundet af Verden', undertitel: 'den modtagende åbenhed',
      x: 156, y: 373, r: 14, role: 'lower',
      bullets: [
        'At slippe at finde og lade verden finde os',
        'Modtagende tilstand som sansende åbenhed',
        'Verden træder frem når vi giver plads'
      ]
    },
    {
      key: 'p6', titel: 'Gavens Forløsning', undertitel: 'lyset gennem mørkets integration',
      x: 224, y: 373, r: 14, role: 'lower',
      bullets: [
        'Den unikke gave der bæres frem af processen',
        'Gennem mørkere lag forløses gavens dybde',
        'Ingen gennemgang uden integration af skygge'
      ]
    },
    {
      key: 'p7', titel: 'Den Daglige Fordybelse', undertitel: 'praksis som portal',
      x: 292, y: 322, r: 14, role: 'lower',
      bullets: [
        'Praksis ved briksen som vedvarende fornyelse',
        'Hver dag uddyber feltet på sin egen måde',
        'Det daglige som portalen til det dybe'
      ]
    }
  ];

  const W = 380;
  const H = 480;

  function buildSVG() {
    // Øjenkonturen — to bløde Q-buer der danner et almond-formet øje.
    // Øvre låg fra (20, 240) over (190, 100) til (360, 240).
    // Nedre låg samme vej tilbage gennem (190, 380).
    const upperLid = 'M 20 240 Q 190 70 360 240';
    const lowerLid = 'M 20 240 Q 190 410 360 240';

    const orbsSVG = NODES.map((n, idx) => {
      const auraR = Math.round(n.r * 4);
      // Label-position: upper låg labels over orben, lower under, pupil under-højre
      let labelY, labelAnchor = 'middle', labelX = n.x;
      if (n.role === 'upper') {
        labelY = n.y - n.r - 12;
      } else if (n.role === 'lower') {
        labelY = n.y + n.r + 18;
      } else {
        // pupil
        labelY = n.y + n.r + 22;
      }

      // Korte labels i flere linjer for orbs på lågene
      const labelLines = (n.role === 'pupil')
        ? ['de 7', 'perspektiver']
        : n.titel.split(' ').reduce((acc, w) => {
            const lastLen = acc[acc.length - 1] ? acc[acc.length - 1].length : 0;
            if (lastLen > 0 && lastLen + w.length > 16) acc.push(w);
            else acc[acc.length - 1] = (acc[acc.length - 1] ? acc[acc.length - 1] + ' ' : '') + w;
            return acc;
          }, ['']);

      const labelTexts = labelLines.map((line, i) => `
        <text x="${labelX}" y="${labelY + i * 12}" text-anchor="${labelAnchor}"
              font-family="Cormorant Garamond, Georgia, serif"
              font-size="${n.role === 'pupil' ? 11 : 10}" font-style="italic"
              fill="#e8c4d0" opacity="0.85">${line}</text>
      `).join('');

      return `
        <g class="persp-orb persp-orb-${n.role}" data-key="${n.key}" onclick="PerspektiverOversigt.tap('${n.key}', true)">
          <circle cx="${n.x}" cy="${n.y}" r="${auraR}" fill="url(#persp-aura)" class="persp-aura">
            <animate attributeName="r" values="${auraR};${auraR + 6};${auraR}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.6).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="url(#persp-core)" class="persp-core">
            <animate attributeName="r" values="${n.r};${n.r + 2};${n.r}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.6).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          ${labelTexts}
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="persp-svg" role="img" aria-label="De 7 Perspektiver — øjet">
        <defs>
          <radialGradient id="persp-well" cx="50%" cy="50%" r="65%">
            <stop offset="0%" stop-color="#1f2a35"/>
            <stop offset="55%" stop-color="#131a22"/>
            <stop offset="100%" stop-color="#0c1218"/>
          </radialGradient>
          <radialGradient id="persp-core" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fce8ec" stop-opacity="1"/>
            <stop offset="30%" stop-color="#e8c4d0" stop-opacity="0.75"/>
            <stop offset="70%" stop-color="#b880a0" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#7a5270" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="persp-aura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#d8a0b8" stop-opacity="0.28"/>
            <stop offset="55%" stop-color="#8a5878" stop-opacity="0.08"/>
            <stop offset="100%" stop-color="#8a5878" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="persp-iris" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e8c4d0" stop-opacity="0.10"/>
            <stop offset="80%" stop-color="#b880a0" stop-opacity="0.04"/>
            <stop offset="100%" stop-color="#8a5878" stop-opacity="0"/>
          </radialGradient>
        </defs>

        <rect x="0" y="0" width="${W}" height="${H}" fill="url(#persp-well)"/>

        <!-- Iris — subtilt rødligt felt bag pupillen, indenfor øjenkonturen -->
        <ellipse cx="190" cy="240" rx="100" ry="70" fill="url(#persp-iris)"/>

        <!-- Øjenkonturen — øvre og nedre øjelåg som tynde glødende linjer -->
        <path d="${upperLid}" stroke="#e8c4d0" stroke-width="0.7" fill="none" opacity="0.55"/>
        <path d="${lowerLid}" stroke="#e8c4d0" stroke-width="0.7" fill="none" opacity="0.55"/>

        <!-- Orbs (orbsene tegnes oven på lågene så de sidder på dem) -->
        ${orbsSVG}
      </svg>
    `;
  }

  function renderDetail(key) {
    const n = NODES.find(x => x.key === key);
    if (!n) return;
    const panel = document.getElementById('perspektiver-detail');
    if (!panel) return;
    panel.innerHTML = `
      <h3 class="persp-detail-titel">${n.titel}</h3>
      ${n.undertitel ? `<p class="persp-detail-undertitel">${n.undertitel}</p>` : ''}
      <ul class="persp-detail-list">
        ${n.bullets.map(b => `<li>${b}</li>`).join('')}
      </ul>
    `;
  }

  function highlight(key) {
    document.querySelectorAll('.persp-orb').forEach(g => {
      g.classList.toggle('selected', g.dataset.key === key);
    });
  }

  window.PerspektiverOversigt = {
    tap: function(key, scroll) {
      highlight(key);
      renderDetail(key);
      if (scroll) {
        const panel = document.getElementById('perspektiver-detail');
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
      const wrapper = document.getElementById('perspektiver-svg-wrapper');
      if (!wrapper) return;
      wrapper.innerHTML = buildSVG();
      this.tap('helhed', false);
    }
  };
})();
