// Traditioner-oversigt — snake-S layout der giver hurtig reference over
// de 13 traditioner og specielle temaer. Tap på en orb scroller automatisk
// ned til detalje-panelet.

(function() {
  // 13 noder placeret langs en sinus-kurve (period 8, amplitude 85) — som
  // sporet en slange efterlader i sandet. y stiger 55px pr orb.
  const NODES = [
    {
      key: 'tensegrity', titel: 'Tensegrity',
      undertitel: 'helhedens levende geometri',
      bullets: [
        'Hele kroppen som ét sammenhængende spændingsfelt',
        'Knogler i træk, fascia i kompression — i konstant balance',
        'Berøring i ét punkt påvirker hele systemet'
      ]
    },
    {
      key: 'anatomy', titel: 'Anatomy Trains',
      undertitel: 'kroppens kommunikerende linjer',
      bullets: [
        'Fascielle linjer der binder kroppen sammen',
        'Kraft og bevægelse forplantes langs linjerne',
        'Det lokale er altid i samtale med det globale'
      ]
    },
    {
      key: 'jin', titel: 'Jin Shin Jyutsu',
      undertitel: 'japansk visdom i vores hænder',
      bullets: [
        'Japansk håndspålægnings-tradition',
        '26 sikkerhedsenergilåse fordelt i kroppen',
        'Subtilt arbejde med energiens strømme'
      ]
    },
    {
      key: 'lovett', titel: 'Lovett Brother Relationship',
      undertitel: 'as above, so below',
      bullets: [
        'Korrelationer mellem forskellige niveauer i kroppen',
        'Kraniets motilitet spejler sakrums motilitet',
        'Dybe refleksive mønstre i den embryologiske arkitektur'
      ]
    },
    {
      key: 'monstre', titel: 'Mønstrene bag',
      undertitel: 'kortlægningen af dybere sammenhænge',
      bullets: [
        'Dybere sammenhænge bag overflade-symptomer',
        'Det fastlåste mønster fortæller en historie',
        'Læsionsfeltet bærer både skade og kommunikation'
      ]
    },
    {
      key: 'tcm', titel: 'TCM',
      undertitel: 'meridianernes baner',
      bullets: [
        'De 12 hovedmeridianer som energiens dagligdags veje',
        '8 ekstraordinære meridianer som dybere reservoirer',
        'Energiens systemiske kommunikation gennem kroppen'
      ]
    },
    {
      key: 'organ', titel: 'Organerne',
      undertitel: 'kroppens viscerale giganter',
      bullets: [
        'Viscerale organer som dynamiske partnere',
        'Hver organ har sin egen motilitet og rytme',
        'Organernes kommunikation med kroppens helhed'
      ]
    },
    {
      key: 'arvaev', titel: 'Arvæv',
      undertitel: 'det fastlåste potentiale',
      bullets: [
        'Fastlåste mønstre fra tidligere skader',
        'Det skjulte potentiale i selve arvævet',
        'Bufferzoner der venter på at åbne sig'
      ]
    },
    {
      key: 'straps', titel: 'Straps',
      undertitel: 'kroppens skjulte spændinger',
      bullets: [
        'Skjulte diagonale spændinger i kroppens nettverk',
        'Tværgående bindinger der trækker i flere retninger',
        'Subtile ankre under det åbenlyse mønster'
      ]
    },
    {
      key: 'multi', titel: 'Multimodale sekvenser',
      undertitel: 'synergien i behandlingen',
      bullets: [
        'Synergi gennem flere modaliteter samtidigt',
        'Berøring, ord, åndedræt, opmærksomhed',
        'Hver modalitet åbner et andet aspekt af helheden'
      ]
    },
    {
      key: 'rebal', titel: 'Re-balancering af klienten',
      undertitel: 'kunsten at favne overvældelse',
      bullets: [
        'At favne overvældelse uden at forstærke den',
        'Tilbageføre nervesystemet til regulering',
        'Det relationelle felts trygge ramme som ankre'
      ]
    },
    {
      key: 'oevelser', titel: 'Øvelser til klienten',
      undertitel: 'broer mellem behandlingerne',
      bullets: [
        'Broer mellem sessioner og hverdagsliv',
        'Klientens egen aktive deltagelse i processen',
        'Selvregulering der modnes mellem sessioner'
      ]
    },
    {
      key: 'speciel', titel: 'Specielle Temaer',
      undertitel: 'angst, traumer, midtlinje, åndedræt, børn',
      bullets: [
        'Angst, traumer, døende, hjernerystelser, vagus',
        'Midtlinjen og åndedrættet som dybe organisatorer',
        'Børnearbejde som parallelt biodynamisk univers'
      ]
    }
  ];

  // Beregn positions: snake-S sinus-kurve gennem orbs
  const W = 380;
  const TOP_PAD = 70;
  const ROW_H = 55;
  const AMPLITUDE = 85;
  const CENTER_X = 190;

  NODES.forEach((n, i) => {
    n.x = Math.round(CENTER_X + AMPLITUDE * Math.sin((Math.PI / 4) * i));
    n.y = TOP_PAD + i * ROW_H;
    n.r = 12;
  });

  const H = TOP_PAD + (NODES.length - 1) * ROW_H + 70;

  // Byg snake-trail som glat polyline (mange samples for smooth visning)
  function buildTrail() {
    const samples = 120;
    const startY = NODES[0].y;
    const endY = NODES[NODES.length - 1].y;
    const totalY = endY - startY;
    const pts = [];
    for (let n = 0; n <= samples; n++) {
      const t = (n / samples) * (NODES.length - 1);
      const x = Math.round(CENTER_X + AMPLITUDE * Math.sin((Math.PI / 4) * t));
      const y = Math.round(startY + (totalY * n / samples));
      pts.push(`${x} ${y}`);
    }
    return 'M ' + pts.join(' L ');
  }

  function buildSVG() {
    const trail = buildTrail();

    const orbsSVG = NODES.map((n, idx) => {
      // Skiftende label-side: orbs til højre side har label til højre, og omvendt
      const labelX = n.x < CENTER_X ? n.x + n.r + 10 : n.x - n.r - 10;
      const labelAnchor = n.x < CENTER_X ? 'start' : 'end';
      const auraR = Math.round(n.r * 4);

      return `
        <g class="trad-orb" data-key="${n.key}" onclick="TraditionerOversigt.tap('${n.key}', true)">
          <circle cx="${n.x}" cy="${n.y}" r="${auraR}" fill="url(#trad-aura)" class="trad-aura">
            <animate attributeName="r" values="${auraR};${auraR + 6};${auraR}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.5).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <circle cx="${n.x}" cy="${n.y}" r="${n.r}" fill="url(#trad-core)" class="trad-core">
            <animate attributeName="r" values="${n.r};${n.r + 2};${n.r}" dur="8s"
                     repeatCount="indefinite" begin="${(idx * 0.5).toFixed(1)}s"
                     calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          </circle>
          <text x="${labelX}" y="${n.y + 4}" text-anchor="${labelAnchor}"
                font-family="Cormorant Garamond, Georgia, serif"
                font-size="11" font-style="italic"
                fill="#e0d0b8" opacity="0.85">${n.titel}</text>
        </g>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="trad-svg" role="img" aria-label="Oversigt over traditioner og specielle temaer">
        <defs>
          <radialGradient id="trad-well" cx="50%" cy="40%" r="65%">
            <stop offset="0%" stop-color="#28323c"/>
            <stop offset="55%" stop-color="#181f26"/>
            <stop offset="100%" stop-color="#0d1217"/>
          </radialGradient>
          <radialGradient id="trad-core" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#f5e8d0" stop-opacity="1"/>
            <stop offset="30%" stop-color="#e0c8a0" stop-opacity="0.75"/>
            <stop offset="70%" stop-color="#b8a070" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#8a7250" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="trad-aura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e0c8a0" stop-opacity="0.26"/>
            <stop offset="55%" stop-color="#a08868" stop-opacity="0.07"/>
            <stop offset="100%" stop-color="#a08868" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="${W}" height="${H}" fill="url(#trad-well)"/>

        <!-- Snake-trail i sandet — prikket sti der vinder sig gennem orbs -->
        <path d="${trail}" stroke="#c8b088" stroke-width="0.6" fill="none"
              opacity="0.45" stroke-dasharray="1.2 4.5" stroke-linecap="round"/>

        ${orbsSVG}
      </svg>
    `;
  }

  function renderDetail(key) {
    const n = NODES.find(x => x.key === key);
    if (!n) return;
    const panel = document.getElementById('traditioner-detail');
    if (!panel) return;
    panel.innerHTML = `
      <h3 class="trad-detail-titel">${n.titel}</h3>
      ${n.undertitel ? `<p class="trad-detail-undertitel">${n.undertitel}</p>` : ''}
      <ul class="trad-detail-list">
        ${n.bullets.map(b => `<li>${b}</li>`).join('')}
      </ul>
    `;
  }

  function highlight(key) {
    document.querySelectorAll('.trad-orb').forEach(g => {
      g.classList.toggle('selected', g.dataset.key === key);
    });
  }

  window.TraditionerOversigt = {
    tap: function(key, scroll) {
      highlight(key);
      renderDetail(key);
      if (scroll) {
        const panel = document.getElementById('traditioner-detail');
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
      const wrapper = document.getElementById('traditioner-svg-wrapper');
      if (!wrapper) return;
      wrapper.innerHTML = buildSVG();
      this.tap(NODES[0].key, false);
    }
  };
})();
