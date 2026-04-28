// Mit Spejl — selv-spejling baseret på app'ens materiale
// Etape 1: 18 spørgsmål, deterministisk profil-beregning, lokalt gemt

(function() {
  const STORAGE_KEY = 'biodynamisk-spejl-historik';

  // 18 spørgsmål i tre akser. Hvert spørgsmål peger til ét stadie/egenskab/zone.
  // Skala 1-10. Output normaliseres pr. dimension.
  const QUESTIONS = [
    // === Modenhedsspiral (5 stadier) ===
    {
      akse: 'stadie', target: 1,
      titel: 'Mental ro',
      tekst: 'Mens du arbejder ved briksen — hvor stille kan dit sind være? Hvor sjældent fyldes det af søgen efter problemer eller forudbestemte protokoller?'
    },
    {
      akse: 'stadie', target: 2,
      titel: 'Pauser mellem tanker',
      tekst: 'Hvor stabilt mærker du tydelige mellemrum mellem dine tanker under behandlingen — hvor sindet hviler uden at fylde rummet?'
    },
    {
      akse: 'stadie', target: 3,
      titel: 'Det relationelle felt',
      tekst: 'Hvor stabilt mærker du Primary Respiration som et fælles felt mellem dig og klienten — ikke kun som to separate systemer?'
    },
    {
      akse: 'stadie', target: 4,
      titel: 'The Long Tide',
      tekst: 'Hvor ofte oplever du at blive bevæget af The Long Tide — at en universel rytme tager opmærksomheden, ikke kun observeres?'
    },
    {
      akse: 'stadie', target: 5,
      titel: 'Dynamisk Stilhed',
      tekst: 'Har du oplevet øjeblikke af nåde hvor paradokserne mødes — hvor du samtidig er adskilt og ét med klientens proces?'
    },

    // === De 8 essentielle egenskaber ===
    {
      akse: 'egenskab', target: 1,
      titel: 'Neutral lytten uden agenda',
      tekst: 'Hvor stabilt kan du være tilstede uden agenda — uden at lede efter problemer eller dirigere processen mod et bestemt resultat?'
    },
    {
      akse: 'egenskab', target: 2,
      titel: 'Selvregulering af nervesystemet',
      tekst: 'Hvor stabilt kan du regulere dit eget nervesystem under behandlingen — også når klientens system er aktiveret eller intenst?'
    },
    {
      akse: 'egenskab', target: 3,
      titel: 'Sansning af den terapeutiske proces',
      tekst: 'Hvor klart sanser du den terapeutiske proces der udfolder sig — når noget skifter kvalitet, når et stillepunkt opstår, når noget regulerer sig?'
    },
    {
      akse: 'egenskab', target: 4,
      titel: 'Tålmodighed & uvished',
      tekst: 'Hvor stabilt kan du hvile i uvished — at vente uden at vide hvad der vil ske, uden at fylde rummet med intention?'
    },
    {
      akse: 'egenskab', target: 5,
      titel: 'Helhedens prioritering',
      tekst: 'Hvor klart kan du mærke kroppens egen prioritering — den indre rækkefølge der tjener helheden bedst, uafhængig af hvad du selv tror er nødvendigt?'
    },
    {
      akse: 'egenskab', target: 6,
      titel: 'Synkron bevægelse',
      tekst: 'Hvor stabilt kan du bevæge dig synkront med klientens krop — følge dens bevægelser præcist uden at føre eller modstå?'
    },
    {
      akse: 'egenskab', target: 7,
      titel: 'Kvalitet i berøringen',
      tekst: 'Hvor stabil og nærværende er kvaliteten i din berøring — hverken for tung eller for fjern, men afstemt med øjeblikkets udtryk?'
    },
    {
      akse: 'egenskab', target: 8,
      titel: 'Behandlingens rytme',
      tekst: 'Hvor klart mærker du behandlingens egen rytme — hvornår noget er færdigt, hvornår noget begynder, hvornår der skal hviles eller bevæges?'
    },

    // === Sanseliggørelse (5 zoner) ===
    {
      akse: 'zone', target: 'A',
      titel: 'Den fysiske krop',
      tekst: 'Hvor stabilt sanser du klientens fysiske krop — vævet, knoglerne, organerne, kroppens konkrete virkelighed?'
    },
    {
      akse: 'zone', target: 'B',
      titel: 'Væskekroppen',
      tekst: 'Hvor stabilt sanser du klientens væskekrop — det levende kontinuum af alle væsker, broen mellem energi og form?'
    },
    {
      akse: 'zone', target: 'C',
      titel: 'Det relationelle felt',
      tekst: 'Hvor stabilt mærker du det relationelle felt mellem dig og klienten — co-regulering, gennemsigtighed, det fælles rum?'
    },
    {
      akse: 'zone', target: 'D',
      titel: 'Primary Respiration',
      tekst: 'Hvor stabilt mærker du Primary Respiration — The Long Tide og The Fluid Tide — som levende rytmer under behandlingen?'
    },
    {
      akse: 'zone', target: 'E',
      titel: 'Dynamisk Stilhed',
      tekst: 'Hvor ofte berører du Dynamisk Stilhed — kilden hvor alt udspringer, paradoksernes rum?'
    }
  ];

  // === Tekst-skabeloner ===
  // Hvor du befinder dig — én pr. primært stadie
  const TEKST_STADIE = {
    1: 'Du står i den urolige begyndelse. Sindet søger, ønsker at forstå, leder efter problemer. Det er her alle starter, og hertil vender vi tilbage hver gang livet udfordrer på nye måder. Det er ikke et sted at forlade men et sted at lære at hvile i.',
    2: 'Pauserne mellem dine tanker er begyndt at vise sig. Væskekroppen vågner. Du mærker andet end mental støj — øjeblikke af stilhed der ikke er tomme men restituerende. Du står i transformationens arbejdsværelse.',
    3: 'Det relationelle felt åbner sig. Primary Respiration mærkes ikke kun i dig og klienten separat, men som fælles bevægelse. Co-regulering bliver naturlig. Det partikulære begynder at blive transparent for noget større.',
    4: 'The Long Tide bevæger sig i dig. Det instinktive niveau aktiveres. Du bliver ikke kun vidne til universelle rytmer — de tager opmærksomheden. Grænsen mellem dig og klienten bliver gennemsigtig.',
    5: 'I sjældne øjeblikke af nåde berører du Dynamisk Stilhed. Paradokserne mødes. Du er samtidig adskilt og ét. Sundheden viser sig som umistelig skabelon. Læsioner bliver kommunikation, ikke fejl.'
  };

  // Egenskab-navne
  const EGENSKAB_NAVN = {
    1: 'Neutral lytten uden agenda',
    2: 'Selvregulering af nervesystemet',
    3: 'Sansning af den terapeutiske proces',
    4: 'Tålmodighed & uvished',
    5: 'At mærke helhedens prioritering',
    6: 'Synkron bevægelse med kroppen',
    7: 'Kvalitet i berøringen',
    8: 'Sans for behandlingens rytme'
  };

  const ZONE_NAVN = {
    'A': 'den fysiske krop',
    'B': 'væskekroppen',
    'C': 'det relationelle felt',
    'D': 'Primary Respiration',
    'E': 'Dynamisk Stilhed'
  };

  // Henvisninger til relevant indhold afhængig af tyngdepunkt
  const HENVISNINGER = {
    1: [
      { titel: 'Det Første Stadie', url: 'stadie.html?id=01-foerste-stadie' },
      { titel: 'Tålmodighed & uvished', url: 'kapitel.html?id=de-otte-essentielle-egenskaber' }
    ],
    2: [
      { titel: 'Det Andet Stadie', url: 'stadie.html?id=02-andet-stadie' },
      { titel: 'Væskekroppen (Zone B)', url: 'zone.html?id=b-vaeskekrop' },
      { titel: 'At Opleve The Neutral (øvelse)', url: 'kapitel.html?id=de-fire-guidede-oevelser' }
    ],
    3: [
      { titel: 'Det Tredje Stadie', url: 'stadie.html?id=03-tredje-stadie' },
      { titel: 'Det relationelle felt (Zone C)', url: 'zone.html?id=c-relationelt-felt' },
      { titel: 'Bevægelsens Paradoks', url: 'kapitel.html?id=de-syv-perspektiver' }
    ],
    4: [
      { titel: 'Det Fjerde Stadie', url: 'stadie.html?id=04-fjerde-stadie' },
      { titel: 'The Long Tide (Zone D)', url: 'zone.html?id=d-primary-respiration' },
      { titel: 'Primary Respiration', url: 'begreb.html?id=03-primary-respiration' }
    ],
    5: [
      { titel: 'Det Femte Stadie', url: 'stadie.html?id=05-femte-stadie' },
      { titel: 'Dynamisk Stilhed (Zone E)', url: 'zone.html?id=e-dynamisk-stilhed' },
      { titel: 'Den Levende Spiral', url: 'stadie.html?id=06-den-levende-spiral' }
    ]
  };

  // === RENDER QUESTIONS ===
  function renderQuestions() {
    const container = document.getElementById('spejl-questions');
    container.innerHTML = QUESTIONS.map((q, i) => `
      <div class="spejl-question" data-index="${i}">
        <h3 class="spejl-q-titel">${q.titel}</h3>
        <p class="spejl-q-tekst">${q.tekst}</p>
        <div class="spejl-slider-row">
          <span class="spejl-slider-anchor">sjældent</span>
          <input type="range" min="1" max="10" value="5" class="spejl-slider" id="q-${i}" oninput="document.getElementById('q-${i}-val').textContent = this.value">
          <span class="spejl-slider-anchor">næsten altid</span>
        </div>
        <div class="spejl-slider-value" id="q-${i}-val">5</div>
      </div>
    `).join('');
  }

  // === BEREGN PROFIL ===
  function beregnProfil() {
    const stadier = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    const egenskaber = {};
    const zoner = { 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0 };

    QUESTIONS.forEach((q, i) => {
      const val = parseInt(document.getElementById('q-' + i).value, 10);
      // Normalisér 1-10 til 0-100
      const score = Math.round(((val - 1) / 9) * 100);
      if (q.akse === 'stadie') stadier[q.target] = score;
      else if (q.akse === 'egenskab') egenskaber[q.target] = score;
      else if (q.akse === 'zone') zoner[q.target] = score;
    });

    // Tyngdepunkt på modenhedsspiralen — vægtet gennemsnit
    const stadieKeys = [1, 2, 3, 4, 5];
    const stadieSum = stadieKeys.reduce((a, k) => a + stadier[k], 0);
    let tyngdepunkt = 1;
    if (stadieSum > 0) {
      let weighted = 0;
      stadieKeys.forEach(k => weighted += k * stadier[k]);
      tyngdepunkt = Math.round((weighted / stadieSum) * 10) / 10;
    }

    return { stadier, egenskaber, zoner, tyngdepunkt, dato: new Date().toISOString() };
  }

  // === GENERER TEKST ===
  function genererTekst(profil) {
    const primaertStadie = Math.round(profil.tyngdepunkt);

    const stadieTekst = TEKST_STADIE[primaertStadie] || TEKST_STADIE[3];

    // Top 2-3 egenskaber (højeste scorer)
    const sortedEgenskaber = Object.entries(profil.egenskaber)
      .sort((a, b) => b[1] - a[1]);
    const stærke = sortedEgenskaber.slice(0, 2).filter(([_, s]) => s >= 50);
    const vækst = sortedEgenskaber.filter(([_, s]) => s >= 30 && s < 60).slice(0, 2);
    const åbent = sortedEgenskaber.filter(([_, s]) => s < 30).slice(0, 2);

    // Zoner
    const zonerSorted = Object.entries(profil.zoner).sort((a, b) => b[1] - a[1]);
    const zoneStærk = zonerSorted[0];
    const zoneÅben = zonerSorted[zonerSorted.length - 1];

    let stærkeTekst = '';
    if (stærke.length > 0) {
      const navne = stærke.map(([k]) => `**${EGENSKAB_NAVN[k]}**`).join(' og ');
      stærkeTekst = `${navne} står stabilt i dig nu. Det er fundamentet alt andet hviler på.`;
    } else {
      stærkeTekst = 'Mange kvaliteter er stadig i bevægelse. Det er ikke en mangel — det er rejsens karakter, hvor alt er åbent.';
    }

    let bevægerTekst = '';
    if (vækst.length > 0) {
      const navne = vækst.map(([k]) => `**${EGENSKAB_NAVN[k]}**`).join(' og ');
      bevægerTekst = `${navne} bevæger sig på vej. Du mærker dem, men de er endnu ikke fuldt stabile. Det er præcis her vækst sker.`;
    } else {
      bevægerTekst = 'Du står i en periode hvor det meste er enten stabilt eller stadig åbent — overgangsfeltet er smalt lige nu.';
    }

    let åbentTekst = '';
    if (åbent.length > 0) {
      const navne = åbent.map(([k]) => `**${EGENSKAB_NAVN[k]}**`).join(' og ');
      åbentTekst = `${navne} er endnu åbent rum. Ikke som mangel men som invitation. Det er der rejsen fører hen næste gang.`;
    } else {
      åbentTekst = 'Ingen kvaliteter er helt skjulte for dig — alle er begyndt at vise sig på deres egen måde.';
    }

    const zoneTekst = `Du har stabilst adgang til **${ZONE_NAVN[zoneStærk[0]]}**. **${ZONE_NAVN[zoneÅben[0]]}** er stadig åbent — ikke fjern, men endnu ikke en hverdag.`;

    return {
      hvor: stadieTekst,
      stærke: stærkeTekst,
      bevæger: bevægerTekst,
      åbent: åbentTekst,
      zoner: zoneTekst,
      stadie: primaertStadie
    };
  }

  // === BYG VISUALISERING ===
  function byggVisualisering(profil) {
    const tyngdepunkt = profil.tyngdepunkt;
    // Map tyngdepunkt 1-5 til x-position på buen (50 til 330)
    const t = (tyngdepunkt - 1) / 4; // 0 til 1
    const sunX = 50 + t * 280;
    // Buens y-position ved x: y = 290 - 160 * (1 - (2*t - 1)^2)  approksimerer bue
    const sunY = 290 - 160 * (1 - Math.pow(2 * t - 1, 2));

    // Beregn aura-størrelse baseret på samlet stabilitet (gennemsnit af alle stadie+egenskab+zone)
    const allScores = [
      ...Object.values(profil.stadier),
      ...Object.values(profil.egenskaber),
      ...Object.values(profil.zoner)
    ];
    const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;
    const auraSize = 80 + (avg / 100) * 80; // 80-160

    // 8 egenskab-orbs over buen, lysstyrke = score
    const egenskabPositioner = [
      { cx: 100, cy: 170 },
      { cx: 142, cy: 138 },
      { cx: 170, cy: 118 },
      { cx: 210, cy: 118 },
      { cx: 238, cy: 138 },
      { cx: 280, cy: 170 },
      { cx: 195, cy: 100 },
      { cx: 155, cy: 155 }
    ];

    const egenskabOrbs = egenskabPositioner.map((pos, i) => {
      const score = profil.egenskaber[i + 1] || 0;
      const opacity = 0.25 + (score / 100) * 0.7;
      const r = 1.6 + (score / 100) * 2;
      return `<circle cx="${pos.cx}" cy="${pos.cy}" r="${r}" fill="url(#orb-g-spe-2)" opacity="${opacity}"/>`;
    }).join('');

    // 5 stadie-punkter på buen
    const stadiePos = [
      { cx: 80, cy: 266 },
      { cx: 125, cy: 218 },
      { cx: 190, cy: 190 },
      { cx: 255, cy: 218 },
      { cx: 300, cy: 266 }
    ];

    const stadiePunkter = stadiePos.map((pos, i) => {
      const score = profil.stadier[i + 1] || 0;
      const opacity = 0.3 + (score / 100) * 0.6;
      const r = 2.5 + (score / 100) * 2;
      return `<circle cx="${pos.cx}" cy="${pos.cy}" r="${r}" fill="url(#orb-g-spe-2)" opacity="${opacity}"/>`;
    }).join('');

    return `
      <svg viewBox="0 0 380 380" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="well-spe-2" cx="50%" cy="50%" r="65%">
            <stop offset="0%" stop-color="#2a3847"/>
            <stop offset="55%" stop-color="#1d2731"/>
            <stop offset="100%" stop-color="#141b22"/>
          </radialGradient>
          <radialGradient id="sun-g-spe-2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fce8ec" stop-opacity="1"/>
            <stop offset="30%" stop-color="#e8c4d0" stop-opacity="0.7"/>
            <stop offset="70%" stop-color="#b880a0" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#7a5270" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="aura-g-spe-2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#d8a0b8" stop-opacity="0.32"/>
            <stop offset="55%" stop-color="#8a5878" stop-opacity="0.10"/>
            <stop offset="100%" stop-color="#8a5878" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="orb-g-spe-2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fce8ec" stop-opacity="0.95"/>
            <stop offset="50%" stop-color="#e8c4d0" stop-opacity="0.55"/>
            <stop offset="100%" stop-color="#8a5878" stop-opacity="0"/>
          </radialGradient>
        </defs>

        <rect x="0" y="0" width="380" height="380" fill="url(#well-spe-2)"/>

        <ellipse cx="${sunX}" cy="${sunY}" rx="${auraSize}" ry="${auraSize * 0.92}" fill="url(#aura-g-spe-2)">
          <animate attributeName="rx" values="${auraSize};${auraSize + 18};${auraSize}" dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          <animate attributeName="ry" values="${auraSize * 0.92};${auraSize * 0.92 + 16};${auraSize * 0.92}" dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
        </ellipse>

        <path d="M 50 290 Q 190 130 330 290" stroke="#e8c4d0" stroke-width="0.7" fill="none" opacity="0.5"/>

        ${egenskabOrbs}
        ${stadiePunkter}

        <ellipse cx="${sunX}" cy="${sunY}" rx="22" ry="22" fill="url(#sun-g-spe-2)">
          <animate attributeName="rx" values="22;30;22" dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          <animate attributeName="ry" values="22;30;22" dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
        </ellipse>

        <line x1="60" y1="320" x2="320" y2="320" stroke="#8a5878" stroke-width="0.3" opacity="0.4"/>
      </svg>
    `;
  }

  // === RENDER RESULTAT ===
  function renderResultat(profil) {
    const tekst = genererTekst(profil);
    const visualisering = byggVisualisering(profil);
    const henvisninger = HENVISNINGER[tekst.stadie] || HENVISNINGER[3];
    const formatMd = (s) => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    document.getElementById('spejl-form').style.display = 'none';
    const resultatDiv = document.getElementById('spejl-resultat');
    resultatDiv.style.display = 'block';
    resultatDiv.innerHTML = `
      <div class="spejl-visualisering">${visualisering}</div>

      <section class="spejl-tekst">
        <h3 class="spejl-tekst-heading">Hvor du befinder dig nu</h3>
        <p>${formatMd(tekst.hvor)}</p>

        <h3 class="spejl-tekst-heading">Hvad lever stærkt i dig</h3>
        <p>${formatMd(tekst.stærke)}</p>

        <h3 class="spejl-tekst-heading">Hvad bevæger sig på vej</h3>
        <p>${formatMd(tekst.bevæger)}</p>

        <h3 class="spejl-tekst-heading">Hvad er stadig åbent</h3>
        <p>${formatMd(tekst.åbent)}</p>

        <h3 class="spejl-tekst-heading">Sansningens lag</h3>
        <p>${formatMd(tekst.zoner)}</p>
      </section>

      <section class="spejl-henvisninger">
        <h3 class="spejl-tekst-heading">Læs videre</h3>
        ${henvisninger.map(h => `<a class="spejl-henvisning" href="${h.url}">${h.titel}</a>`).join('')}
      </section>

      <div class="spejl-actions">
        <button class="spejl-btn-secondary" onclick="window.MitSpejl.reset()">Spejl igen</button>
      </div>
    `;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // === GEM I LOCALSTORAGE ===
  function gemProfil(profil) {
    let historik = [];
    try { historik = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch (e) {}
    historik.push(profil);
    if (historik.length > 12) historik = historik.slice(-12);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historik));
  }

  // === HÅNDTERING ===
  window.MitSpejl = {
    submit: function() {
      const profil = beregnProfil();
      gemProfil(profil);
      renderResultat(profil);
    },
    reset: function() {
      document.getElementById('spejl-resultat').style.display = 'none';
      document.getElementById('spejl-form').style.display = 'block';
      QUESTIONS.forEach((_, i) => {
        const slider = document.getElementById('q-' + i);
        if (slider) {
          slider.value = 5;
          document.getElementById('q-' + i + '-val').textContent = '5';
        }
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderQuestions);
  } else {
    renderQuestions();
  }
})();
