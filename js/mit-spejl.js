// Mit Spejl — selv-spejling baseret på app'ens materiale
// Etape 1: 18 spørgsmål, deterministisk profil-beregning, lokalt gemt

(function() {
  const STORAGE_KEY = 'biodynamisk-spejl-historik';

  // KORT spejling: 18 spørgsmål i tre akser, ~5 minutter.
  // Hvert spørgsmål peger til ét stadie/egenskab/zone.
  // Skala 1-10. Output normaliseres pr. dimension.
  const QUESTIONS_KORT = [
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

  // DYB spejling: 50 spørgsmål, ~20 minutter — fuld kortlægning.
  // Hvert område har flere spørgsmål; scorerne gennemsnits-aggregeres pr. dimension.
  const QUESTIONS_DYB = [
    // === Stadie 1 — Den Urolige Begyndelse (3) ===
    { akse: 'stadie', target: 1, titel: 'Mental ro', tekst: 'Hvor sjældent fyldes dit sind af søgen efter problemer eller forudbestemte protokoller under behandling?' },
    { akse: 'stadie', target: 1, titel: 'Slip af kontrol', noegle: true, noegleId: 'slip-af-kontrol', tekst: 'Hvor stabilt kan du slippe behovet for at forstå alt rationelt og tillade processen at udfolde sig?' },
    { akse: 'stadie', target: 1, titel: 'Frigjort fra ego-frygt', noegle: true, noegleId: 'ego-frygt', tekst: 'Hvor lidt påvirkes din praksis af spørgsmål som "er jeg dygtig nok?" eller "gør jeg det rigtige?"' },

    // === Stadie 2 — Væskekroppen og de Første Levende Pauser (3) ===
    { akse: 'stadie', target: 2, titel: 'Pauser mellem tanker', tekst: 'Hvor stabilt mærker du tydelige mellemrum mellem dine tanker under behandlingen?' },
    { akse: 'stadie', target: 2, titel: 'Væskekroppen vågner', tekst: 'Hvor stabilt sanser du væskekroppens spontane balancepunkter i klienten?' },
    { akse: 'stadie', target: 2, titel: 'Abdominal vejrtrækning', tekst: 'Hvor stabilt synker din vejrtrækning af sig selv ned under diafragma — vandlignende kvalitet?' },

    // === Stadie 3 — Den Relationelle Udvidelse (3) ===
    { akse: 'stadie', target: 3, titel: 'Co-regulering uden teknik', tekst: 'Hvor klart oplever du at din ro skaber rum for klientens regulering — gennem simpel tilstedeværelse?' },
    { akse: 'stadie', target: 3, titel: 'Det fælles felt', tekst: 'Hvor stabilt mærker du Primary Respiration som ét fælles felt mellem dig og klienten?' },
    { akse: 'stadie', target: 3, titel: 'Relationel intuition', tekst: 'Hvor stabilt fornemmer du familiære dynamikker eller arbejdsrelationer leve i klientens krop?' },

    // === Stadie 4 — The Long Tide (3) ===
    { akse: 'stadie', target: 4, titel: 'At blive bevæget af The Long Tide', tekst: 'Hvor ofte oplever du at blive bevæget af The Long Tide — at den tager opmærksomheden, ikke kun observeres?' },
    { akse: 'stadie', target: 4, titel: 'Instinktiv erkendelse', tekst: 'Hvor stabilt arbejder du fra instinktiv erkendelse frem for analyse?' },
    { akse: 'stadie', target: 4, titel: 'Gennemsigtige grænser', tekst: 'Når grænsen mellem dig og klienten bliver gennemsigtig — hvor stabilt bevarer du integriteten i mødet?' },

    // === Stadie 5 — Dynamisk Stilhed (3) ===
    { akse: 'stadie', target: 5, titel: 'Paradoksernes møde', tekst: 'Har du oplevet samtidig at være adskilt og ét med klientens proces — uden at det opløser sig?' },
    { akse: 'stadie', target: 5, titel: 'Læsioner som kommunikation', tekst: 'Hvor stabilt genkender du læsioner som Sundhedens budbringere — ikke som dysfunktion der skal fjernes?' },
    { akse: 'stadie', target: 5, titel: 'At blive skabt af livet', tekst: 'Mærker du at blive "drømt ind i verden" af en større drømmer — samtidig med at være fuldt vågen?' },

    // === De 8 essentielle egenskaber — selv-aspekt + klient-aspekt (16) ===
    { akse: 'egenskab', target: 1, titel: 'Neutral lytning — i dig selv', noegle: true, noegleId: 'neutral-lytten', tekst: 'Hvor stabilt kan du være tilstede uden agenda — uden at lede efter noget bestemt?' },
    { akse: 'egenskab', target: 1, titel: 'Neutral lytning — i mødet', tekst: 'Hvor stabilt kan du holde rummet uden at dirigere klientens proces mod et forudbestemt resultat?' },

    { akse: 'egenskab', target: 2, titel: 'Selvregulering — i dig selv', tekst: 'Hvor stabilt kan du regulere dit eget nervesystem under behandlingen?' },
    { akse: 'egenskab', target: 2, titel: 'Selvregulering — under intensitet', tekst: 'Hvor stabilt kan du forblive reguleret når klientens nervesystem er aktiveret?' },

    { akse: 'egenskab', target: 3, titel: 'Sansning — eget system', tekst: 'Hvor klart sanser du dit eget systems respons under behandling — fra øjeblik til øjeblik?' },
    { akse: 'egenskab', target: 3, titel: 'Sansning — terapeutiske skift', tekst: 'Hvor klart sanser du når et stillepunkt opstår, eller når noget regulerer sig i klienten?' },

    { akse: 'egenskab', target: 4, titel: 'Tålmodighed — at vente', noegle: true, noegleId: 'taalmodighed', tekst: 'Hvor stabilt kan du hvile i uvished uden at fylde rummet med intention?' },
    { akse: 'egenskab', target: 4, titel: 'Tålmodighed — klientens tempo', tekst: 'Hvor stabilt kan du give klientens proces den tid den selv behøver?' },

    { akse: 'egenskab', target: 5, titel: 'Helhedens prioritering — i dig', tekst: 'Hvor klart mærker du din egen krops prioritering — uden at din analyse overtager?' },
    { akse: 'egenskab', target: 5, titel: 'Helhedens prioritering — i klienten', tekst: 'Hvor klart mærker du klientens egen prioritering — den indre rækkefølge der tjener helheden bedst?' },

    { akse: 'egenskab', target: 6, titel: 'Synkron bevægelse — egen krop', tekst: 'Hvor stabilt bevæger du dig synkront med din egen krops impulser i behandlingsrummet?' },
    { akse: 'egenskab', target: 6, titel: 'Synkron bevægelse — klientens krop', tekst: 'Hvor præcist følger du klientens bevægelser uden at føre eller modstå?' },

    { akse: 'egenskab', target: 7, titel: 'Berøringen — afstemt med dig', tekst: 'Hvor afstemt er din egen kropslige kontakt med dig selv mens du behandler?' },
    { akse: 'egenskab', target: 7, titel: 'Berøringen — afstemt med klienten', tekst: 'Hvor afstemt er kvaliteten i din berøring med klientens øjebliks-udtryk — hverken for tung eller for fjern?' },

    { akse: 'egenskab', target: 8, titel: 'Rytme — i dagligdagen', tekst: 'Hvor klart mærker du rytmen i dit eget liv — hvile, arbejde, integration?' },
    { akse: 'egenskab', target: 8, titel: 'Rytme — i behandlingen', tekst: 'Hvor klart mærker du behandlingens egen rytme — start, intensitet, afrunding?' },

    // === Sansningens lag — sansning + arbejde (10) ===
    { akse: 'zone', target: 'A', titel: 'Den fysiske krop — sansning', tekst: 'Hvor stabilt sanser du klientens fysiske krop — vævet, knoglerne, organerne?' },
    { akse: 'zone', target: 'A', titel: 'Den fysiske krop — arbejde', tekst: 'Hvor stabilt kan du møde fysiske spændinger og læsioner uden at ville fjerne dem?' },

    { akse: 'zone', target: 'B', titel: 'Væskekroppen — sansning', tekst: 'Hvor stabilt sanser du væskekroppens bevægelser som ét levende kontinuum?' },
    { akse: 'zone', target: 'B', titel: 'Væskekroppen — arbejde', tekst: 'Hvor stabilt kan du støtte væskekroppens egne reguleringer uden at føre dem?' },

    { akse: 'zone', target: 'C', titel: 'Det relationelle felt — sansning', tekst: 'Hvor stabilt mærker du det relationelle felt mellem dig og klienten?' },
    { akse: 'zone', target: 'C', titel: 'Det relationelle felt — arbejde', tekst: 'Hvor stabilt kan du holde et trygt relationelt rum, særligt ved sårbare temaer?' },

    { akse: 'zone', target: 'D', titel: 'Primary Respiration — sansning', tekst: 'Hvor stabilt mærker du Primary Respiration som levende rytme under behandlingen?' },
    { akse: 'zone', target: 'D', titel: 'Primary Respiration — arbejde', tekst: 'Hvor stabilt arbejder du i kontakt med The Long Tide — som vejviser, ikke kun som observation?' },

    { akse: 'zone', target: 'E', titel: 'Dynamisk Stilhed — sansning', tekst: 'Hvor ofte berører du Dynamisk Stilhed — kilden hvor alt udspringer?' },
    { akse: 'zone', target: 'E', titel: 'Dynamisk Stilhed — arbejde', tekst: 'Hvor stabilt kan du være i Dynamisk Stilhed under behandling — uden at miste klienten?' },

    // === Klient-relationelle aspekter (5) ===
    { akse: 'egenskab', target: 5, titel: 'Klientmønstre', tekst: 'Hvor klart genkender du de typiske klientmønstre — og lader dem være, frem for at definere klienten?' },
    { akse: 'egenskab', target: 4, titel: 'Læsionsfeltet', tekst: 'Hvor stabilt kan du være tilstede med klientens læsionsfelt uden at forsøge at "løse" det?' },
    { akse: 'egenskab', target: 5, titel: 'Automatic Shifting', tekst: 'Hvor klart mærker du klientens system spontant prioritere — fra sted til sted i behandlingen?' },
    { akse: 'stadie', target: 2, titel: 'The Neutral indfinder sig', tekst: 'Hvor stabilt mærker du The Neutral indfinde sig — homogen, samlet substans i klienten?' },
    { akse: 'stadie', target: 5, titel: 'Sundheden som skabelon', tekst: 'Hvor stabilt mærker du klientens iboende skabelon for sundhed — selv i intense eller fastlåste tilstande?' },

    // === Praksis-aspekter (4) ===
    { akse: 'egenskab', target: 8, titel: 'Daglig praksis', tekst: 'Hvor stabilt vender du tilbage til den biodynamiske tilgang dagligt — også på de svære dage?' },
    { akse: 'egenskab', target: 4, titel: 'Stilhed udenfor briksen', noegle: true, noegleId: 'stilhed-udenfor', tekst: 'Hvor stabilt finder du stilheden i din hverdag — udenfor behandlingsrummet?' },
    { akse: 'egenskab', target: 2, titel: 'Egne pauser', tekst: 'Hvor stabilt tager du pauser i dit eget liv som understøtter din praksis?' },
    { akse: 'egenskab', target: 8, titel: 'Integration over tid', tekst: 'Hvor stabilt integrerer du nye erkendelser i din praksis — så de bliver levende viden?' }
  ];

  // === KLIENTMØNSTRE ===
  // De ni mønstre fra "Typiske Klientmønstre" — bruges som valgfri refleksion
  // efter sliderne i både kort og dyb spejling. To akser: hvilke møder du ofte,
  // og hvilke reagerer du kraftigst på. Forskellen er ofte det interessante.
  const KLIENTMOENSTRE = [
    { id: 'stresset',           titel: 'Den Stressede Klient' },
    { id: 'gamle-traumer',      titel: 'Klienten med Gamle Traumer' },
    { id: 'barnet',             titel: 'Barnet med den Levende Væskekrop' },
    { id: 'skeptisk',           titel: 'Den Skeptiske Klient' },
    { id: 'overvaeldelse',      titel: 'Klienten i Overvældelse' },
    { id: 'sensitiv',           titel: 'Den Særligt Sensitive' },
    { id: 'kroniske-smerter',   titel: 'Klienten med Kroniske Smerter' },
    { id: 'spirituelt-soegende',titel: 'Den Spirituelt Søgende' },
    { id: 'akut-traumatiseret', titel: 'Den Akut Traumatiserede' }
  ];

  // Aktive spørgsmål — sættes når brugeren vælger kort/dyb
  let QUESTIONS = QUESTIONS_KORT;
  let CURRENT_TYPE = null; // 'kort' eller 'dyb'

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
    if (!container) return;
    container.innerHTML = QUESTIONS.map((q, i) => {
      const tekstfelt = q.noegle ? `
        <textarea
          class="spejl-q-tekstfelt"
          id="q-${i}-text"
          data-noegle-id="${q.noegleId}"
          rows="2"
          aria-label="Egne ord til ${q.titel} (valgfrit)"
          placeholder="Skriv nogle ord her, hvis de er der. Lad dem selv vise sig."
        ></textarea>
      ` : '';
      return `
        <div class="spejl-question${q.noegle ? ' spejl-question--noegle' : ''}" data-index="${i}">
          <h3 class="spejl-q-titel">${q.titel}</h3>
          <p class="spejl-q-tekst">${q.tekst}</p>
          <div class="spejl-slider-row">
            <span class="spejl-slider-anchor">sjældent</span>
            <input type="range" min="1" max="10" value="5" class="spejl-slider" id="q-${i}" oninput="document.getElementById('q-${i}-val').textContent = this.value">
            <span class="spejl-slider-anchor">næsten altid</span>
          </div>
          <div class="spejl-slider-value" id="q-${i}-val">5</div>
          ${tekstfelt}
        </div>
      `;
    }).join('');
  }

  // === RENDER KLIENTMØNSTRE ===
  // Vises som en collapsible sektion efter sliderne. Brugeren kan markere
  // hvilke mønstre hen møder ofte og hvilke hen reagerer kraftigst på.
  function renderKlientmoenstre() {
    const container = document.getElementById('spejl-moenstre');
    if (!container) return;
    const rows = KLIENTMOENSTRE.map(m => `
      <div class="spejl-moenster-row" data-moenster-id="${m.id}">
        <span class="spejl-moenster-titel">${m.titel}</span>
        <div class="spejl-moenster-toggles">
          <label class="spejl-moenster-toggle">
            <input type="checkbox" id="moenster-${m.id}-moeder">
            <span>Møder ofte</span>
          </label>
          <label class="spejl-moenster-toggle">
            <input type="checkbox" id="moenster-${m.id}-reagerer">
            <span>Reagerer kraftigt på</span>
          </label>
        </div>
      </div>
    `).join('');
    container.innerHTML = `
      <details class="spejl-moenstre-details">
        <summary class="spejl-moenstre-summary">
          <span class="spejl-moenstre-titel">Klientmønstre — valgfrit</span>
          <span class="spejl-moenstre-hint">Tryk for at folde ud</span>
        </summary>
        <div class="spejl-moenstre-indhold">
          <p class="spejl-moenstre-intro">Der er ni typiske klientmønstre i bogen. Markér dem du møder ofte — og dem du reagerer kraftigst på. De to er ikke altid de samme, og forskellen kan være værd at lægge mærke til.</p>
          <div class="spejl-moenstre-rows">${rows}</div>
        </div>
      </details>
    `;
  }

  // Saml klientmønster-svar fra DOM
  function samlKlientmoenstre() {
    const ud = {};
    KLIENTMOENSTRE.forEach(m => {
      const moeder = document.getElementById('moenster-' + m.id + '-moeder');
      const reagerer = document.getElementById('moenster-' + m.id + '-reagerer');
      const mb = moeder && moeder.checked;
      const rb = reagerer && reagerer.checked;
      if (mb || rb) {
        ud[m.id] = { moeder: mb, reagerer: rb };
      }
    });
    return ud;
  }

  // Slå titel op fra ID
  function moensterTitel(id) {
    const m = KLIENTMOENSTRE.find(x => x.id === id);
    return m ? m.titel : id;
  }

  // === BEREGN PROFIL ===
  function beregnProfil() {
    // Akkumulér scores pr. target (sum + count) — gennemsnits-aggregeres
    const acc = { stadie: {}, egenskab: {}, zone: {} };
    // Saml fritekst-svar fra nøgle-spørgsmål, og slider-værdi for hvert nøgle-spørgsmål
    // (slideren gemmes pr. noegleId så vi kan vise før/nu side om side selv hvis spørgsmåls-listen omarrangeres)
    const tekster = {};
    const noegleSlider = {};

    QUESTIONS.forEach((q, i) => {
      const val = parseInt(document.getElementById('q-' + i).value, 10);
      // Normalisér 1-10 til 0-100
      const score = Math.round(((val - 1) / 9) * 100);
      if (!acc[q.akse][q.target]) acc[q.akse][q.target] = { sum: 0, n: 0 };
      acc[q.akse][q.target].sum += score;
      acc[q.akse][q.target].n += 1;

      if (q.noegle && q.noegleId) {
        const ta = document.getElementById('q-' + i + '-text');
        const v = ta ? ta.value.trim() : '';
        if (v) tekster[q.noegleId] = v;
        noegleSlider[q.noegleId] = val;
      }
    });

    const avg = (bucket) => {
      const out = {};
      for (const k in bucket) out[k] = Math.round(bucket[k].sum / bucket[k].n);
      return out;
    };

    const stadier = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, ...avg(acc.stadie) };
    const egenskaber = avg(acc.egenskab);
    // Sikr at alle 8 egenskaber findes (selv hvis ingen spørgsmål peger til dem)
    for (let k = 1; k <= 8; k++) if (egenskaber[k] === undefined) egenskaber[k] = 0;
    const zoner = { 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, ...avg(acc.zone) };

    // Tyngdepunkt på modenhedsspiralen — vægtet gennemsnit
    const stadieKeys = [1, 2, 3, 4, 5];
    const stadieSum = stadieKeys.reduce((a, k) => a + stadier[k], 0);
    let tyngdepunkt = 1;
    if (stadieSum > 0) {
      let weighted = 0;
      stadieKeys.forEach(k => weighted += k * stadier[k]);
      tyngdepunkt = Math.round((weighted / stadieSum) * 10) / 10;
    }

    return {
      stadier,
      egenskaber,
      zoner,
      tyngdepunkt,
      type: CURRENT_TYPE || 'kort',
      dato: new Date().toISOString(),
      tekster,
      noegleSlider,
      klientmoenstre: samlKlientmoenstre()
    };
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
  // Mandala-form: centreret radial visualisering — tydeligt anderledes end Mit Spejls hero (rejsens bue).
  // Pentagon af stadier indenfor, oktagon af egenskaber udenom, koncentriske zone-ringe, central sol.
  function byggVisualisering(profil) {
    const tyngdepunkt = profil.tyngdepunkt;

    const allScores = [
      ...Object.values(profil.stadier),
      ...Object.values(profil.egenskaber),
      ...Object.values(profil.zoner)
    ];
    const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;
    const auraSize = 90 + (avg / 100) * 70; // 90-160

    const cx = 190, cy = 190;

    // 5 zone-ringe — koncentriske, opacity efter zone-score
    const zoneKeys = ['A', 'B', 'C', 'D', 'E'];
    const zoneRings = zoneKeys.map((z, i) => {
      const r = 50 + i * 22; // 50, 72, 94, 116, 138
      const score = profil.zoner[z] || 0;
      const opacity = (0.10 + (score / 100) * 0.22).toFixed(2);
      return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#d8a0b8" stroke-width="0.4" opacity="${opacity}"/>`;
    }).join('');

    // 5 stadier i pentagon, top-pointed (-90° start, hver 72°)
    const stadieR = 80;
    const stadieAngles = [-90, -18, 54, 126, 198];
    const stadieDot = stadieAngles.map((deg, i) => {
      const rad = deg * Math.PI / 180;
      const x = (cx + stadieR * Math.cos(rad)).toFixed(1);
      const y = (cy + stadieR * Math.sin(rad)).toFixed(1);
      const score = profil.stadier[i + 1] || 0;
      const opacity = (0.35 + (score / 100) * 0.55).toFixed(2);
      const r = (3.2 + (score / 100) * 3).toFixed(1);
      return `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#orb-g-spe-2)" opacity="${opacity}"/>`;
    }).join('');

    // Subtil eger fra centrum til hver stadie — opacity følger stadiens score
    const stadieSpokes = stadieAngles.map((deg, i) => {
      const rad = deg * Math.PI / 180;
      const x2 = (cx + (stadieR - 8) * Math.cos(rad)).toFixed(1);
      const y2 = (cy + (stadieR - 8) * Math.sin(rad)).toFixed(1);
      const x1 = (cx + 32 * Math.cos(rad)).toFixed(1);
      const y1 = (cy + 32 * Math.sin(rad)).toFixed(1);
      const score = profil.stadier[i + 1] || 0;
      const opacity = (0.10 + (score / 100) * 0.25).toFixed(2);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#e8c4d0" stroke-width="0.4" opacity="${opacity}"/>`;
    }).join('');

    // 8 egenskaber i oktagon, ydre ring
    const egR = 132;
    const egenskaber = [];
    for (let i = 0; i < 8; i++) {
      const deg = -90 + i * 45; // -90 til 225
      const rad = deg * Math.PI / 180;
      const x = (cx + egR * Math.cos(rad)).toFixed(1);
      const y = (cy + egR * Math.sin(rad)).toFixed(1);
      const score = profil.egenskaber[i + 1] || 0;
      const opacity = (0.25 + (score / 100) * 0.7).toFixed(2);
      const r = (1.8 + (score / 100) * 2.4).toFixed(1);
      egenskaber.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="url(#orb-g-spe-2)" opacity="${opacity}"/>`);
    }
    const egenskabOrbs = egenskaber.join('');

    // Tyngdepunkts-akse: en let lysere eger mod den dominerende stadie
    const tpIdx = Math.max(0, Math.min(4, Math.round(tyngdepunkt) - 1));
    const tpRad = stadieAngles[tpIdx] * Math.PI / 180;
    const tpX2 = (cx + (stadieR - 8) * Math.cos(tpRad)).toFixed(1);
    const tpY2 = (cy + (stadieR - 8) * Math.sin(tpRad)).toFixed(1);
    const tpX1 = (cx + 26 * Math.cos(tpRad)).toFixed(1);
    const tpY1 = (cy + 26 * Math.sin(tpRad)).toFixed(1);
    const tpAxis = `<line x1="${tpX1}" y1="${tpY1}" x2="${tpX2}" y2="${tpY2}" stroke="#fce8ec" stroke-width="0.7" opacity="0.55"/>`;

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

        <!-- Aura — pulserer med samlet stabilitet -->
        <ellipse cx="${cx}" cy="${cy}" rx="${auraSize}" ry="${auraSize}" fill="url(#aura-g-spe-2)">
          <animate attributeName="rx" values="${auraSize};${auraSize + 18};${auraSize}" dur="9s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          <animate attributeName="ry" values="${auraSize};${auraSize + 18};${auraSize}" dur="9s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
        </ellipse>

        <!-- 5 zone-ringe (koncentriske) -->
        ${zoneRings}

        <!-- Egere fra centrum til stadier -->
        ${stadieSpokes}

        <!-- Tyngdepunkts-akse: tydeligere eger mod dominerende stadie -->
        ${tpAxis}

        <!-- 8 egenskaber i oktagon (yder-ring) -->
        ${egenskabOrbs}

        <!-- 5 stadier i pentagon (inder-ring) -->
        ${stadieDot}

        <!-- Central sol — det nuværende selv -->
        <ellipse cx="${cx}" cy="${cy}" rx="20" ry="20" fill="url(#sun-g-spe-2)">
          <animate attributeName="rx" values="20;28;20" dur="7s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
          <animate attributeName="ry" values="20;28;20" dur="7s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>
        </ellipse>
      </svg>
    `;
  }

  // === HISTORIK & BEVÆGELSE ===
  function hentHistorik() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch (e) { return []; }
  }

  function formatDato(isoString) {
    const d = new Date(isoString);
    const md = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec'];
    return `${d.getDate()}. ${md[d.getMonth()]}`;
  }

  // Sammenlign nuværende profil med forrige — returnér deltas
  function beregnDeltas(nuværende, forrige) {
    if (!forrige) return null;
    const stadier = {};
    for (let k = 1; k <= 5; k++) {
      stadier[k] = (nuværende.stadier[k] || 0) - (forrige.stadier[k] || 0);
    }
    const egenskaber = {};
    for (let k = 1; k <= 8; k++) {
      egenskaber[k] = (nuværende.egenskaber[k] || 0) - (forrige.egenskaber[k] || 0);
    }
    const zoner = {};
    ['A','B','C','D','E'].forEach(z => {
      zoner[z] = (nuværende.zoner[z] || 0) - (forrige.zoner[z] || 0);
    });
    const tyngde = nuværende.tyngdepunkt - forrige.tyngdepunkt;
    return { stadier, egenskaber, zoner, tyngde };
  }

  // Generer tekst om bevægelsen siden sidste spejling
  function genererBevægelseTekst(deltas, forrige, nuværende) {
    if (!deltas) return null;

    const stigende = Object.entries(deltas.egenskaber)
      .filter(([_, d]) => d >= 8)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2);
    const faldende = Object.entries(deltas.egenskaber)
      .filter(([_, d]) => d <= -8)
      .sort((a, b) => a[1] - b[1])
      .slice(0, 2);

    let tyngdeTekst = '';
    if (Math.abs(deltas.tyngde) < 0.15) {
      tyngdeTekst = `Dit modenheds-tyngdepunkt har ligget stabilt omkring **${nuværende.tyngdepunkt.toFixed(1)}** siden ${formatDato(forrige.dato)}. Stilstand er ikke standsning — det er ofte hvor det dybeste arbejde sker.`;
    } else if (deltas.tyngde > 0) {
      tyngdeTekst = `Dit tyngdepunkt har bevæget sig fra **${forrige.tyngdepunkt.toFixed(1)}** til **${nuværende.tyngdepunkt.toFixed(1)}** siden ${formatDato(forrige.dato)} — opad i spiralen, men husk at spiralens karakter er at vi vender tilbage til det vi troede vi havde forladt.`;
    } else {
      tyngdeTekst = `Dit tyngdepunkt er gledet fra **${forrige.tyngdepunkt.toFixed(1)}** til **${nuværende.tyngdepunkt.toFixed(1)}** siden ${formatDato(forrige.dato)}. Ikke tilbagefald — spiralens natur. Det er ofte præcis her at noget dybere kan integreres.`;
    }

    let stigerTekst = '';
    if (stigende.length > 0) {
      const navne = stigende.map(([k, d]) => `**${EGENSKAB_NAVN[k]}** (+${d})`).join(' og ');
      stigerTekst = `${navne} er åbnet sig mere end ved sidste spejling.`;
    }

    let falderTekst = '';
    if (faldende.length > 0) {
      const navne = faldende.map(([k, d]) => `**${EGENSKAB_NAVN[k]}** (${d})`).join(' og ');
      falderTekst = `${navne} mærkes mindre stabil end tidligere — måske et signal om at noget vil ses, ikke at noget er tabt.`;
    }

    return { tyngde: tyngdeTekst, stiger: stigerTekst, falder: falderTekst };
  }

  // Tidslinje-SVG: viser de seneste spejlinger som punkter på en kurve
  function byggTidslinje(historik) {
    if (historik.length < 2) return '';
    const last = historik.slice(-6);
    const W = 380, H = 180;
    const padX = 30, padY = 30;
    const innerW = W - 2 * padX;
    const innerH = H - 2 * padY;

    const points = last.map((p, i) => {
      const x = padX + (i / Math.max(1, last.length - 1)) * innerW;
      // y: stadie 1 nederst, 5 øverst
      const y = padY + (1 - (p.tyngdepunkt - 1) / 4) * innerH;
      return { x, y, profil: p, dato: formatDato(p.dato) };
    });

    // Smooth path through points
    let path = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1], cur = points[i];
      const cx = (prev.x + cur.x) / 2;
      path += ` Q ${cx} ${prev.y}, ${cx} ${(prev.y + cur.y) / 2} T ${cur.x} ${cur.y}`;
    }

    // Y-akse labels (stadie 1-5)
    const yLabels = [1, 2, 3, 4, 5].map(s => {
      const y = padY + (1 - (s - 1) / 4) * innerH;
      return `<text x="${padX - 8}" y="${y + 4}" text-anchor="end" font-family="Cinzel, serif" font-size="9" fill="#8a5878" opacity="0.6">${s}</text>`;
    }).join('');

    // Punkter — sidste fremhæves
    const dots = points.map((p, i) => {
      const isLast = i === points.length - 1;
      const r = isLast ? 6 : 3.5;
      const opacity = isLast ? 1 : 0.55;
      return `
        <circle cx="${p.x}" cy="${p.y}" r="${r}" fill="url(#tidsline-sun)" opacity="${opacity}"/>
        <text x="${p.x}" y="${H - 8}" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="10" font-style="italic" fill="#8a5878" opacity="${isLast ? 1 : 0.5}">${p.dato}</text>
      `;
    }).join('');

    return `
      <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="spejl-tidslinje-svg">
        <defs>
          <radialGradient id="tidsline-sun" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fce8ec" stop-opacity="1"/>
            <stop offset="50%" stop-color="#e8c4d0" stop-opacity="0.7"/>
            <stop offset="100%" stop-color="#8a5878" stop-opacity="0"/>
          </radialGradient>
        </defs>
        ${yLabels}
        <path d="${path}" stroke="#e8c4d0" stroke-width="1" fill="none" opacity="0.6"/>
        ${dots}
      </svg>
    `;
  }

  // Smartere henvisninger baseret på bevægelse + nuværende tilstand
  function smartereHenvisninger(profil, deltas) {
    const stadie = Math.round(profil.tyngdepunkt);
    const base = HENVISNINGER[stadie] || HENVISNINGER[3];
    const ekstra = [];

    if (deltas) {
      // Hvis tyngdepunkt stiger og næste stadie er inden for rækkevidde, foreslå det
      if (deltas.tyngde > 0.2 && stadie < 5) {
        const næste = HENVISNINGER[stadie + 1];
        if (næste && næste[0]) ekstra.push(næste[0]);
      }
      // Hvis en bestemt egenskab er faldet markant, foreslå refleksioner
      const størsteFald = Object.entries(deltas.egenskaber)
        .filter(([_, d]) => d <= -10)
        .sort((a, b) => a[1] - b[1])[0];
      if (størsteFald) {
        ekstra.push({
          titel: 'Refleksioner over de essentielle egenskaber',
          url: 'kapitel.html?id=de-otte-essentielle-egenskaber'
        });
      }
    }

    // Saml unik liste, max 4
    const seen = new Set();
    const liste = [...base, ...ekstra].filter(h => {
      if (seen.has(h.url)) return false;
      seen.add(h.url);
      return true;
    }).slice(0, 4);

    return liste;
  }

  // === FØR/NU-SPEJLING (etape 4) ===
  // Tema-information pr. nøgle-spørgsmål — bruges til at navngive bevægelser
  // i bogens egen vokabular. Modsætning er det stadie/sprog brugeren bevæger
  // sig fra ved bevægelse opad (slider stiger).
  const NOEGLE_TEMA = {
    'slip-af-kontrol':  { titel: 'kontrol', fra: 'Det Første Stadie\'s søgen', til: 'Det Andet Stadie\'s tålmodighed', kategorier: ['kontrol', 'agenda', 'outcome', 'overgang', 'taalmodighed'] },
    'ego-frygt':        { titel: 'din egen værdighed', fra: 'tvivlen om at være dygtig nok', til: 'at hvile i dig selv mens tvivlen er der', kategorier: ['tvivl', 'frygt'] },
    'neutral-lytten':   { titel: 'agenda', fra: 'at lede efter noget bestemt', til: 'at lytte uden at vide', kategorier: ['agenda', 'kontrol', 'lytten', 'taalmodighed'] },
    'taalmodighed':     { titel: 'uvished', fra: 'at fylde rummet med intention', til: 'at hvile i ikke-viden', kategorier: ['taalmodighed', 'tvivl', 'kropsmarker', 'overgang'] },
    'stilhed-udenfor':  { titel: 'stilhed i hverdagen', fra: 'stilhed kun ved briksen', til: 'stilhed der følger med', kategorier: ['kropsmarker', 'overgang', 'resonans'] }
  };

  // Foretræk det match hvis kategori står i tema'ets prioriteringsliste.
  // Falder tilbage til første ikke-general/ikke-ambiguous match.
  function vælgRelevantOrd(matches, tema) {
    if (!matches || matches.length === 0) return null;
    const ikkeGenerel = matches.filter(o =>
      o.mapping.kategori !== 'general' && o.mapping.kategori !== 'ambiguous'
    );
    if (ikkeGenerel.length === 0) return null;
    if (tema && tema.kategorier) {
      for (const kat of tema.kategorier) {
        const fundet = ikkeGenerel.find(o => o.mapping.kategori === kat);
        if (fundet) return fundet;
      }
    }
    return ikkeGenerel[0];
  }

  // Find seneste DYB spejling der kom før den givne profil i tid.
  // Returnerer null hvis ingen findes.
  function findForrigeDybBefore(historik, profil) {
    const idx = historik.findIndex(p => p.dato === profil.dato);
    const cutoff = idx === -1 ? historik.length : idx;
    for (let i = cutoff - 1; i >= 0; i--) {
      if (historik[i].type === 'dyb') return historik[i];
    }
    return null;
  }

  // Alle dybe spejlinger der kom før den givne profil — bruges af anker-vælger
  function alleForrigeDybe(historik, profil) {
    const idx = historik.findIndex(p => p.dato === profil.dato);
    const cutoff = idx === -1 ? historik.length : idx;
    return historik.slice(0, cutoff).filter(p => p.type === 'dyb');
  }

  // Antal dage mellem to ISO-datoer
  function dageMellem(isoÆldre, isoNyere) {
    const a = new Date(isoÆldre).getTime();
    const b = new Date(isoNyere).getTime();
    return Math.floor((b - a) / (1000 * 60 * 60 * 24));
  }

  // Beregn bevægelses-score for hvert nøgle-spørgsmål.
  // Slider-delta tæller direkte (0-9 absolut). Tekst-skift giver bonus:
  //   +3 hvis tekst i begge og adskiller sig
  //   +5 hvis tekst kun i én af dem (asymmetri = stort signal)
  function beregnNoegleBevægelser(før, nu) {
    const ud = [];
    for (const id in NOEGLE_TEMA) {
      const sFør = (før.noegleSlider || {})[id];
      const sNu = (nu.noegleSlider || {})[id];
      const tFør = (før.tekster || {})[id] || '';
      const tNu = (nu.tekster || {})[id] || '';
      let score = 0;
      let sliderDelta = null;
      if (sFør != null && sNu != null) {
        sliderDelta = sNu - sFør;
        score += Math.abs(sliderDelta);
      }
      let tekstSkift = 'ingen';
      if (tFør && tNu && tFør !== tNu)        { score += 3; tekstSkift = 'begge'; }
      else if (!tFør && tNu)                   { score += 5; tekstSkift = 'kun-nu'; }
      else if (tFør && !tNu)                   { score += 5; tekstSkift = 'kun-før'; }
      if (score > 0) {
        ud.push({ id, score, sliderDelta, sFør, sNu, tFør, tNu, tekstSkift });
      }
    }
    ud.sort((a, b) => b.score - a.score);
    return ud;
  }

  // Generer den lille spejlings-tekst nederst i hver før/nu-blok.
  function genererNoegleSpejling(item, før, nu) {
    const tema = NOEGLE_TEMA[item.id];
    const T = window.SpejlThesaurus;
    const datoFør = formatDato(før.dato);

    // Hvis tekst kun i én af dem — to klare scenarier
    if (item.tekstSkift === 'kun-nu') {
      return `Sidste gang lod du dette spørgsmål stå uden ord. I dag har du fundet et sprog for det.`;
    }
    if (item.tekstSkift === 'kun-før') {
      return `Du skrev om det her i ${datoFør} — i dag står det åbent. Måske er det stadig der, måske er det fortrukket.`;
    }

    // Begge har tekst — brug thesaurus til at finde sproglige skift
    if (item.tekstSkift === 'begge' && T) {
      const d = T.diff(item.tFør, item.tNu);
      // Vælg det tematisk mest relevante forsvundet og kommet-til-ord
      const forsvundet = vælgRelevantOrd(d.forsvundet, tema);
      const kommetTil = vælgRelevantOrd(d.kommetTil, tema);

      if (forsvundet && kommetTil) {
        return `Du har bevæget dig på **${tema.titel}**. I ${datoFør} var ordet '${forsvundet.ord}' centralt; i dag bruger du '${kommetTil.ord}'. I bogens sprog er det bevægelsen fra ${tema.fra} mod ${tema.til}.`;
      }
      if (forsvundet && !kommetTil) {
        return `Ordet '${forsvundet.ord}' var fremme i ${datoFør}. I dag er det ikke længere der. Det er en stille bevægelse — noget har sluppet sit greb.`;
      }
      if (!forsvundet && kommetTil) {
        return `Et nyt ord er kommet til siden ${datoFør}: '${kommetTil.ord}'. Det peger mod **${tema.titel}** som et levende felt.`;
      }
      // Tekst har bevæget sig men ingen nøgle-ord at hænge det op på
      return `Dit sprog har bevæget sig — i ${datoFør} brugte du andre ord end i dag. Læs dem ved siden af hinanden og mærk hvad der har skiftet.`;
    }

    // Kun slider-bevægelse, ingen tekst
    if (item.sliderDelta != null && item.sliderDelta !== 0) {
      if (item.sliderDelta > 0) {
        return `Slideren er gledet opad siden ${datoFør} — noget har åbnet sig på **${tema.titel}**.`;
      }
      return `Slideren er gledet nedad siden ${datoFør}. Det er ikke tilbagefald — måske blot et signal om at noget vil ses påny.`;
    }
    return '';
  }

  // Render selve før/nu-sektionen. Returnerer HTML-streng (eller tom).
  function byggFørNuSektion(forrige, nuværende, formatMd) {
    if (!forrige || forrige.type !== 'dyb' || nuværende.type !== 'dyb') return '';
    const bevægelser = beregnNoegleBevægelser(forrige, nuværende);
    if (bevægelser.length === 0) return '';

    // Vis op til 3 stærkeste
    const top = bevægelser.slice(0, 3);
    const datoFør = formatDato(forrige.dato);
    const datoNu = formatDato(nuværende.dato);

    const blokke = top.map(item => {
      const tema = NOEGLE_TEMA[item.id];
      const sliderFør = item.sFør != null ? `${item.sFør} / 10` : '—';
      const sliderNu = item.sNu != null ? `${item.sNu} / 10` : '—';
      const tFør = item.tFør ? `<p class="spejl-fornu-citat">"${escapeHtml(item.tFør)}"</p>` : `<p class="spejl-fornu-citat spejl-fornu-citat--tom">ingen ord</p>`;
      const tNu = item.tNu ? `<p class="spejl-fornu-citat">"${escapeHtml(item.tNu)}"</p>` : `<p class="spejl-fornu-citat spejl-fornu-citat--tom">ingen ord</p>`;
      const spejling = genererNoegleSpejling(item, forrige, nuværende);

      return `
        <article class="spejl-fornu-blok">
          <h4 class="spejl-fornu-tema">${tema.titel.toUpperCase()}</h4>
          <div class="spejl-fornu-grid">
            <div class="spejl-fornu-kolonne">
              <div class="spejl-fornu-dato">${datoFør}</div>
              <div class="spejl-fornu-slider">${sliderFør}</div>
              ${tFør}
            </div>
            <div class="spejl-fornu-kolonne">
              <div class="spejl-fornu-dato spejl-fornu-dato--nu">${datoNu}</div>
              <div class="spejl-fornu-slider spejl-fornu-slider--nu">${sliderNu}</div>
              ${tNu}
            </div>
          </div>
          ${spejling ? `<p class="spejl-fornu-refleksion">${formatMd(spejling)}</p>` : ''}
        </article>
      `;
    }).join('');

    return `
      <section class="spejl-fornu">
        <h3 class="spejl-tekst-heading">Før og nu</h3>
        <p class="spejl-fornu-intro">Vi sammenligner din spejling i dag med din dybe spejling fra ${datoFør}. Her er de tre områder hvor bevægelsen er tydeligst — med dine egne ord før og nu.</p>
        ${blokke}
      </section>
    `;
  }

  // Lille hjælpe-funktion — escaper HTML i brugerens tekst
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  }

  // Anker-vælger: lille select hvor brugeren kan skifte hvilken tidligere dyb
  // spejling før/nu-sektionen sammenlignes med. Vises kun hvis der er mindst 2
  // tidligere dybe at vælge mellem.
  function byggAnkerVælger(tilgængelige, valgt, profil) {
    if (!tilgængelige || tilgængelige.length < 2) return '';
    const options = tilgængelige.map(p => {
      const sel = (valgt && p.dato === valgt.dato) ? ' selected' : '';
      return `<option value="${p.dato}"${sel}>${formatDato(p.dato)} (tyngde ${p.tyngdepunkt.toFixed(1)})</option>`;
    }).reverse().join(''); // nyeste først
    return `
      <div class="spejl-anker-vælger-wrap">
        <p class="spejl-anker-hjælp">Du kan vælge en ældre dyb spejling at sammenligne med — det viser længere bevægelser.</p>
        <div class="spejl-anker-vælger">
          <label class="spejl-anker-label" for="spejl-anker-select">Sammenlign med</label>
          <select id="spejl-anker-select" class="spejl-anker-select" onchange="window.MitSpejl.skiftAnker('${profil.dato}', this.value)">
            ${options}
          </select>
        </div>
      </div>
    `;
  }

  // === KLIENTMØNSTRE I RESULTATET ===
  // Vis valgte mønstre + en lille spejlings-tekst om forskellen mellem
  // hvad brugeren møder ofte og hvad hen reagerer kraftigst på.
  function byggKlientmoensterSektion(profil, formatMd) {
    const mn = profil.klientmoenstre || {};
    const ids = Object.keys(mn);
    if (ids.length === 0) return '';

    const moeder = ids.filter(id => mn[id].moeder);
    const reagerer = ids.filter(id => mn[id].reagerer);
    const begge = moeder.filter(id => reagerer.includes(id));
    const kunMoeder = moeder.filter(id => !reagerer.includes(id));
    const kunReagerer = reagerer.filter(id => !moeder.includes(id));

    const titler = arr => arr.map(id => `**${moensterTitel(id)}**`).join(', ');

    // Generer spejlings-tekst
    let spejling = '';
    if (moeder.length > 0 && reagerer.length === 0) {
      spejling = `Du møder ${titler(moeder)} ofte i din praksis. Ingen af dem trigger dig stærkt — de føles som mønstre du har fundet en plads til at være med.`;
    } else if (moeder.length === 0 && reagerer.length > 0) {
      spejling = `Du reagerer kraftigt på ${titler(reagerer)} — selvom du ikke møder dem ofte. Måske er det netop sjældenheden der gør dem store, eller måske venter de på at blive mødt fuldt.`;
    } else if (kunReagerer.length > 0 && begge.length === 0) {
      spejling = `Du møder ${titler(kunMoeder)} ofte uden at reagere kraftigt. Men ${titler(kunReagerer)} bevæger dig stærkt selvom de er sjældnere. Forskellen er værd at lægge mærke til — det du sjældent møder kalder ofte mest på dig.`;
    } else if (begge.length > 0 && kunReagerer.length === 0 && kunMoeder.length === 0) {
      spejling = `Du møder og reagerer på de samme mønstre: ${titler(begge)}. Det er ikke nødvendigvis en mangel — det kan være de mønstre der bærer den tyngde du står med lige nu.`;
    } else if (begge.length > 0) {
      const dele = [];
      if (begge.length > 0) dele.push(`Du både møder og reagerer på ${titler(begge)}`);
      if (kunMoeder.length > 0) dele.push(`du møder ${titler(kunMoeder)} uden at reagere kraftigt`);
      if (kunReagerer.length > 0) dele.push(`og ${titler(kunReagerer)} trigger dig selvom du ikke møder dem ofte`);
      spejling = dele.join('. ') + '. De du reagerer på men sjældent møder, kan være dér noget kalder.';
    }

    // Liste-visning af alle markerede mønstre
    const liste = ids.map(id => {
      const merkører = [];
      if (mn[id].moeder) merkører.push('møder ofte');
      if (mn[id].reagerer) merkører.push('reagerer kraftigt på');
      return `<li class="spejl-moenster-item"><span class="spejl-moenster-item-titel">${moensterTitel(id)}</span> <span class="spejl-moenster-item-meta">${merkører.join(' · ')}</span></li>`;
    }).join('');

    return `
      <section class="spejl-tekst spejl-moenstre-resultat">
        <h3 class="spejl-tekst-heading">Klientmønstre</h3>
        <ul class="spejl-moenstre-liste">${liste}</ul>
        ${spejling ? `<p class="spejl-moenstre-spejling">${formatMd(spejling)}</p>` : ''}
      </section>
    `;
  }

  // === REFLEKSIV LUKKE-CYKLUS ===
  // Vis forrige intention hvis den findes på den profil der kom umiddelbart før.
  function byggForrigeIntention(forrige) {
    if (!forrige || !forrige.intention) return '';
    return `
      <section class="spejl-intention-forrige">
        <h3 class="spejl-tekst-heading">Din intention fra ${formatDato(forrige.dato)}</h3>
        <p class="spejl-intention-citat">"${escapeHtml(forrige.intention)}"</p>
        <p class="spejl-intention-spoergsmaal">Hvor er den nu?</p>
      </section>
    `;
  }

  // Vis felt til at sætte ny intention. Skjules når visningen kommer fra arkivet
  // (gamle profiler skal ikke kunne ændres).
  function byggNyIntention(profil, fraArkiv) {
    if (fraArkiv) {
      // Hvis profilen har en intention fra dengang, vis den read-only
      if (profil.intention) {
        return `
          <section class="spejl-intention-arkiv">
            <h3 class="spejl-tekst-heading">Din intention da</h3>
            <p class="spejl-intention-citat">"${escapeHtml(profil.intention)}"</p>
          </section>
        `;
      }
      return '';
    }
    const eksisterende = profil.intention ? escapeHtml(profil.intention) : '';
    return `
      <section class="spejl-intention-ny">
        <h3 class="spejl-tekst-heading">Sæt en intention</h3>
        <p class="spejl-intention-hjælp">Et par ord om hvad du vil holde øje med frem til næste spejling.</p>
        <textarea
          class="spejl-intention-felt"
          id="spejl-intention-text"
          rows="2"
          placeholder="Hvad vil du holde øje med frem til næste spejling?"
          onblur="window.MitSpejl.gemIntention('${profil.dato}', this.value)"
        >${eksisterende}</textarea>
        <p class="spejl-intention-status" id="spejl-intention-hint">${profil.intention ? 'Gemt — citeres tilbage til dig næste gang.' : 'En lille intention. Citeres tilbage til dig næste gang.'}</p>
      </section>
    `;
  }

  // === RENDER RESULTAT ===
  // Options:
  //   ankerProfil — eksplicit dyb-profil at sammenligne før/nu med (anker-vælger)
  //   fraArkiv    — true når visningen kommer fra arkivet (viser "tilbage til arkiv"-knap)
  function renderResultat(profil, options) {
    options = options || {};
    const tekst = genererTekst(profil);
    const visualisering = byggVisualisering(profil);
    const formatMd = (s) => s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Hent historik
    const historik = hentHistorik();

    // Find den profil der kom umiddelbart før denne — bruges til slider/tyngde-deltas
    const idx = historik.findIndex(p => p.dato === profil.dato);
    const forrige = idx > 0 ? historik[idx - 1] : (idx === -1 && historik.length >= 2 ? historik[historik.length - 2] : null);
    const deltas = beregnDeltas(profil, forrige);
    const bevægelse = genererBevægelseTekst(deltas, forrige, profil);
    const henvisninger = smartereHenvisninger(profil, deltas);
    const tidslinje = byggTidslinje(historik);

    // Før/nu-sammenligning — bruger anker-profil hvis sat, ellers seneste dyb før denne
    const forrigeDyb = options.ankerProfil || findForrigeDybBefore(historik, profil);
    const tilgængeligeAnkre = profil.type === 'dyb' ? alleForrigeDybe(historik, profil) : [];
    const ankerVælgerHTML = byggAnkerVælger(tilgængeligeAnkre, forrigeDyb, profil);
    const førNuSektion = byggFørNuSektion(forrigeDyb, profil, formatMd);

    // Klientmønster-sektion (kun hvis brugeren har markeret nogle)
    const klientmoensterSektion = byggKlientmoensterSektion(profil, formatMd);

    // Refleksiv lukke-cyklus
    const forrigeIntentionSektion = byggForrigeIntention(forrige);
    const nyIntentionSektion = byggNyIntention(profil, !!options.fraArkiv);

    document.getElementById('spejl-form').style.display = 'none';
    const valgEl = document.getElementById('spejl-valg');
    if (valgEl) valgEl.style.display = 'none';
    const resultatDiv = document.getElementById('spejl-resultat');
    resultatDiv.style.display = 'block';

    // Seneste spejling åbner som separat skærm — skjul Mit Spejl-headeren og opdater top-nav
    const pageHeader = document.getElementById('spejl-page-header');
    if (pageHeader) pageHeader.style.display = 'none';
    const backBtn = document.getElementById('spejl-back-btn');
    if (backBtn) {
      backBtn.textContent = '‹ Tilbage';
      backBtn.onclick = function() { window.MitSpejl.tilbageTilValg(); };
    }
    const cat = document.getElementById('spejl-category');
    if (cat) cat.textContent = 'SENESTE SPEJLING';

    let bevægelseSection = '';
    if (bevægelse) {
      bevægelseSection = `
        <section class="spejl-tekst spejl-bevaegelse">
          <h3 class="spejl-tekst-heading">Bevægelsen siden sidste spejling</h3>
          <p>${formatMd(bevægelse.tyngde)}</p>
          ${bevægelse.stiger ? `<p>${formatMd(bevægelse.stiger)}</p>` : ''}
          ${bevægelse.falder ? `<p>${formatMd(bevægelse.falder)}</p>` : ''}
        </section>
      `;
    }

    let tidslinjeSection = '';
    if (tidslinje) {
      tidslinjeSection = `
        <section class="spejl-tidslinje">
          <h3 class="spejl-tekst-heading">Din rejse over tid</h3>
          <p class="spejl-tidslinje-tekst">${historik.length} spejlinger siden ${formatDato(historik[0].dato)}. Punktet til højre er nu — punkterne til venstre er hvor du har været.</p>
          ${tidslinje}
        </section>
      `;
    }

    resultatDiv.innerHTML = `
      <div class="spejl-visualisering">${visualisering}</div>

      ${forrigeIntentionSektion}

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

      ${klientmoensterSektion}

      ${ankerVælgerHTML}

      ${førNuSektion}

      ${bevægelseSection}

      ${tidslinjeSection}

      <section class="spejl-henvisninger">
        <h3 class="spejl-tekst-heading">Læs videre</h3>
        ${henvisninger.map(h => `<a class="spejl-henvisning" href="${h.url}">${h.titel}</a>`).join('')}
      </section>

      ${nyIntentionSektion}

      <div class="spejl-actions">
        ${options.fraArkiv
          ? '<button class="spejl-btn-secondary" onclick="window.MitSpejl.seArkiv()">‹ Tilbage til arkiv</button>'
          : '<button class="spejl-btn-secondary" onclick="window.MitSpejl.reset()">Spejl igen</button>'}
        ${historik.length >= 2 ? '<button class="spejl-btn-secondary" onclick="window.MitSpejl.seArkiv()">Mit arkiv</button>' : ''}
        ${!options.fraArkiv && historik.length > 0 ? '<button class="spejl-btn-secondary" onclick="window.MitSpejl.slet()">Slet historik</button>' : ''}
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
    vælgType: function(type) {
      CURRENT_TYPE = type;
      QUESTIONS = (type === 'dyb') ? QUESTIONS_DYB : QUESTIONS_KORT;
      // Skjul valg-skærm, vis form
      const valg = document.getElementById('spejl-valg');
      if (valg) valg.style.display = 'none';
      const form = document.getElementById('spejl-form');
      if (form) form.style.display = 'block';
      const dybIntro = document.getElementById('spejl-dyb-intro');
      if (dybIntro) dybIntro.style.display = (type === 'dyb') ? 'block' : 'none';
      renderQuestions();
      renderKlientmoenstre();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    tilbageTilValg: function() {
      const valg = document.getElementById('spejl-valg');
      if (valg) valg.style.display = 'block';
      const form = document.getElementById('spejl-form');
      if (form) form.style.display = 'none';
      const res = document.getElementById('spejl-resultat');
      if (res) res.style.display = 'none';
      // Gendan side-headeren og top-nav når vi er tilbage til Mit Spejl-valg
      const pageHeader = document.getElementById('spejl-page-header');
      if (pageHeader) pageHeader.style.display = '';
      const backBtn = document.getElementById('spejl-back-btn');
      if (backBtn) {
        backBtn.textContent = '‹ Rejsen';
        backBtn.onclick = function() { window.location.href = 'rejsen.html'; };
      }
      const cat = document.getElementById('spejl-category');
      if (cat) cat.textContent = 'REJSEN';
      visHistorikKnap();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    submit: function() {
      const profil = beregnProfil();
      gemProfil(profil);
      renderResultat(profil);
    },
    gemIntention: function(profilDato, tekst) {
      // Opdater intention på profilen i localStorage. Kaldes på blur fra
      // intention-tekstfeltet i resultat-skærmen.
      let historik = [];
      try { historik = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch (e) {}
      const idx = historik.findIndex(p => p.dato === profilDato);
      if (idx === -1) return;
      const trimmet = (tekst || '').trim();
      if (trimmet) {
        historik[idx].intention = trimmet;
      } else {
        delete historik[idx].intention;
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(historik));
      // Lille visuel bekræftelse — opdater hint-tekst hvis findes
      const hint = document.getElementById('spejl-intention-hint');
      if (hint) {
        hint.textContent = trimmet ? 'Gemt — citeres tilbage til dig næste gang.' : 'En lille intention. Citeres tilbage til dig næste gang.';
      }
    },
    reset: function() {
      document.getElementById('spejl-resultat').style.display = 'none';
      // Tilbage til valg-skærm i stedet for direkte til form
      this.tilbageTilValg();
    },
    seHistorik: function() {
      const historik = hentHistorik();
      if (historik.length === 0) return;
      const seneste = historik[historik.length - 1];
      renderResultat(seneste);
    },
    skiftAnker: function(profilDato, ankerDato) {
      const historik = hentHistorik();
      const profil = historik.find(p => p.dato === profilDato);
      const anker = historik.find(p => p.dato === ankerDato);
      if (!profil) return;
      const idx = historik.findIndex(p => p.dato === profilDato);
      const erSeneste = idx === historik.length - 1;
      renderResultat(profil, { ankerProfil: anker, fraArkiv: !erSeneste });
    },
    seArkiv: function() {
      renderArkiv();
    },
    seProfilFraArkiv: function(dato) {
      const historik = hentHistorik();
      const profil = historik.find(p => p.dato === dato);
      if (!profil) return;
      const idx = historik.findIndex(p => p.dato === dato);
      const erSeneste = idx === historik.length - 1;
      renderResultat(profil, { fraArkiv: !erSeneste });
    },
    slet: function() {
      if (!confirm('Slet hele din spejl-historik? Den kan ikke gendannes.')) return;
      localStorage.removeItem(STORAGE_KEY);
      this.tilbageTilValg();
    }
  };

  // Render arkiv: kronologisk liste over alle spejlinger
  function renderArkiv() {
    const historik = hentHistorik();
    const valg = document.getElementById('spejl-valg');
    const form = document.getElementById('spejl-form');
    const res = document.getElementById('spejl-resultat');
    if (valg) valg.style.display = 'none';
    if (form) form.style.display = 'none';
    if (!res) return;
    res.style.display = 'block';

    if (historik.length === 0) {
      res.innerHTML = `
        <section class="spejl-arkiv">
          <h3 class="spejl-tekst-heading">Mit arkiv</h3>
          <p class="spejl-tidslinje-tekst">Du har endnu ingen spejlinger gemt.</p>
          <div class="spejl-actions">
            <button class="spejl-btn-secondary" onclick="window.MitSpejl.tilbageTilValg()">Tilbage</button>
          </div>
        </section>
      `;
      return;
    }

    // Nyeste først
    const items = historik.slice().reverse().map(p => {
      const typeLabel = p.type === 'dyb' ? 'Dyb' : 'Kort';
      const harTekst = p.tekster && Object.keys(p.tekster).length > 0;
      return `
        <button class="spejl-arkiv-item" onclick="window.MitSpejl.seProfilFraArkiv('${p.dato}')">
          <span class="spejl-arkiv-dato">${formatDato(p.dato)}</span>
          <span class="spejl-arkiv-meta">${typeLabel} spejling · tyngde ${p.tyngdepunkt.toFixed(1)}${harTekst ? ' · med ord' : ''}</span>
        </button>
      `;
    }).join('');

    res.innerHTML = `
      <section class="spejl-arkiv">
        <h3 class="spejl-tekst-heading">Mit arkiv</h3>
        <p class="spejl-tidslinje-tekst">Her er alle dine spejlinger samlet, nyeste først. Tryk på en for at se den fuldt ud — du kan også sammenligne den med endnu tidligere dybe spejlinger.</p>
        <div class="spejl-arkiv-liste">${items}</div>
        <div class="spejl-actions">
          <button class="spejl-btn-secondary" onclick="window.MitSpejl.tilbageTilValg()">Tilbage</button>
        </div>
      </section>
    `;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Generer tids-prompt-tekst baseret på dage siden seneste DYB spejling.
  // Returnerer null hvis ingen dyb findes eller den er for ny til prompt.
  function tidsPromptTekst(dageSidenDyb) {
    if (dageSidenDyb == null) return null;
    if (dageSidenDyb < 90) return null; // <3 mdr — ingen prompt
    if (dageSidenDyb < 180) {
      return 'Det er omkring 3 måneder siden din sidste dybe spejling. Tager du en ny, vil du se dine svar — og dine ord — side om side med dem du gav sidst.';
    }
    if (dageSidenDyb < 365) {
      return 'Det er omkring et halvt år siden du sad med den dybe spejling. Det er ofte her bevægelser begynder at vise sig tydeligt — tager du en ny, kan du se dine ord side om side.';
    }
    return 'Et år er gået siden din sidste dybe spejling. Spejler du igen, kan du se hvor langt du har bevæget dig — i tal og i dine egne ord.';
  }

  // Vis historik-banner øverst på formularen hvis brugeren har spejlet før.
  // Hvis seneste dyb spejling er > 3 mdr gammel, vises en blid invitation
  // til at tage en ny dyb spejling.
  function visHistorikKnap() {
    const historik = hentHistorik();
    const banner = document.getElementById('spejl-historik-banner');
    if (!banner) return;
    if (historik.length === 0) {
      banner.style.display = 'none';
      return;
    }
    const seneste = historik[historik.length - 1];
    const senesteDyb = [...historik].reverse().find(p => p.type === 'dyb');
    const dageSidenDyb = senesteDyb ? dageMellem(senesteDyb.dato, new Date().toISOString()) : null;
    const tidsPrompt = tidsPromptTekst(dageSidenDyb);

    banner.style.display = 'block';

    if (tidsPrompt) {
      // Tids-prompt: blid invitation til ny dyb spejling
      banner.innerHTML = `
        <p class="spejl-historik-tekst">${tidsPrompt}</p>
        <div class="spejl-historik-knapper">
          <button class="spejl-btn-primary" onclick="window.MitSpejl.vælgType('dyb')">Tag en ny dyb spejling</button>
          <button class="spejl-btn-secondary" onclick="window.MitSpejl.seArkiv()">Mit arkiv</button>
        </div>
      `;
      return;
    }

    // Standard-banner: kort opsummering + adgang til historik
    banner.innerHTML = `
      <p class="spejl-historik-tekst">Din seneste spejling var ${formatDato(seneste.dato)} — tyngdepunkt <strong>${seneste.tyngdepunkt.toFixed(1)}</strong>. ${historik.length > 1 ? historik.length + ' tidligere spejlinger gemt på din enhed.' : ''}</p>
      <div class="spejl-historik-knapper">
        <button class="spejl-btn-secondary" onclick="window.MitSpejl.seHistorik()">Se seneste spejling</button>
        ${historik.length >= 2 ? '<button class="spejl-btn-secondary" onclick="window.MitSpejl.seArkiv()">Mit arkiv</button>' : ''}
      </div>
    `;
  }

  // Init — vis valg-skærm først (form rendrer først efter type er valgt)
  function init() {
    visHistorikKnap();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
