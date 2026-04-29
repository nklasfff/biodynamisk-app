// Mit Spejl — thesaurus til langtidsspejling
//
// Mapper nøgle-ord fra brugerens fritekst til positioner på rejsen
// (stadier 1-5, egenskaber 1-8). Bruges af før/nu-spejlingen til at
// navngive sproglige skift i bogens egen vokabular.
//
// Princip: kun utvetydige ord mappes. Tvetydige ord (kategori: 'ambiguous')
// citeres uforfalsket men placeres ikke. Generelle ord (kategori: 'general')
// kan optræde overalt på rejsen og bruges som farve, ikke som markør.

(function() {

  // === ORD-TABEL ===
  // Hvert ord: { stadie?, egenskab?, kategori, note? }
  // 'kategori' kategoriserer placeringen så app'en kan tale om mønstre
  // (fx "outcome-sprog", "forklarings-trang", "møde-sprog").
  const ORD = {
    // Stadie 1 — outcome-paradigmet
    'resultat':         { stadie: 1, kategori: 'outcome' },
    'resultater':       { stadie: 1, kategori: 'outcome' },
    'bedring':          { stadie: 1, kategori: 'outcome' },
    'symptom':          { stadie: 1, kategori: 'outcome' },
    'symptomer':        { stadie: 1, kategori: 'outcome' },
    'forværring':       { stadie: 1, kategori: 'outcome' },
    'det samme':        { stadie: 1, kategori: 'outcome' },
    'uændret':          { stadie: 1, kategori: 'outcome' },
    'symptomfri':       { stadie: 1, kategori: 'outcome' },
    'lindring':         { stadie: 1, kategori: 'outcome' },
    'virker det':       { stadie: 1, kategori: 'outcome' },
    'sker der noget':   { stadie: 1, kategori: 'outcome' },
    'årsag':            { stadie: 1, kategori: 'outcome' },

    // Stadie 1 — forklarings-trang
    'forklare':         { stadie: 1, kategori: 'forklaring' },
    'forklaring':       { stadie: 1, kategori: 'forklaring' },
    'hvordan':          { stadie: 1, kategori: 'forklaring' },
    'hvornår':          { stadie: 1, kategori: 'forklaring' },
    'logisk':           { stadie: 1, kategori: 'forklaring' },
    'rigtigt':          { stadie: 1, kategori: 'forklaring' },
    'forkert':          { stadie: 1, kategori: 'forklaring' },
    'hensigtsmæssig':   { stadie: 1, kategori: 'forklaring' },

    // Stadie 1 — forvirring og skepsis
    'tvivl':            { stadie: 1, kategori: 'tvivl' },
    'usikker':          { stadie: 1, kategori: 'tvivl' },
    'forvirret':        { stadie: 1, kategori: 'tvivl' },
    'mystisk':          { stadie: 1, kategori: 'tvivl' },
    'mærkeligt':        { stadie: 1, kategori: 'tvivl' },
    'blande sammen':    { stadie: 1, kategori: 'tvivl' },
    'healing':          { stadie: 1, kategori: 'tvivl' },
    'virkeligt':        { stadie: 1, kategori: 'tvivl' },
    'magi':             { stadie: 1, kategori: 'tvivl', note: 'typisk klient-frame' },

    // Stadie 1 — teknik-grebet
    'teknik':           { stadie: 1, kategori: 'teknik' },
    'teknikker':        { stadie: 1, kategori: 'teknik' },
    'greb':             { stadie: 1, kategori: 'teknik' },

    // Stadie 1 — frygt og overvælde (også egenskab 2 inverteret)
    'bange':            { stadie: 1, egenskab: 2, kategori: 'frygt', inverteret: true },
    'for meget':        { stadie: 1, egenskab: 2, kategori: 'frygt', inverteret: true },

    // Stadie 1 — kontrol-trang (bogens kerne-sprog)
    'kontrol':          { stadie: 1, kategori: 'kontrol' },
    'styre':            { stadie: 1, kategori: 'kontrol' },
    'leder':            { stadie: 1, egenskab: 1, kategori: 'kontrol', inverteret: true },
    'leder efter':      { stadie: 1, egenskab: 1, kategori: 'kontrol', inverteret: true },
    'agenda':           { egenskab: 1, kategori: 'agenda', inverteret: true },
    'intention':        { egenskab: 1, kategori: 'agenda', inverteret: true },
    'holde vejret':     { stadie: 1, kategori: 'kropsmarker' },

    // Stadie 1 → 2 — overgangs-ord
    'slippe':           { stadie: 2, kategori: 'overgang' },
    'give slip':        { stadie: 2, kategori: 'overgang' },
    'lader gå':         { stadie: 2, kategori: 'overgang' },

    // Stadie 2-3 — når noget begynder at lande
    'giver mening':     { stadie: 3, kategori: 'resonans' },
    'lytte':            { egenskab: 1, kategori: 'lytten' },
    'lytten':           { egenskab: 1, kategori: 'lytten' },
    'venter':           { egenskab: 4, kategori: 'taalmodighed' },
    'venten':           { egenskab: 4, kategori: 'taalmodighed' },
    'uvished':          { egenskab: 4, kategori: 'taalmodighed' },
    'tålmodig':         { egenskab: 4, kategori: 'taalmodighed' },
    'tålmodighed':      { egenskab: 4, kategori: 'taalmodighed' },

    // Stadie 3 — det relationelle felt
    'co-regulering':    { stadie: 3, kategori: 'relationel' },
    'fælles felt':      { stadie: 3, kategori: 'relationel' },
    'føle sig mødt':    { stadie: 3, egenskab: 1, kategori: 'moede' },
    'føler sig mødt':   { stadie: 3, egenskab: 1, kategori: 'moede' },
    'møde klienten':    { stadie: 3, egenskab: 1, kategori: 'moede' },
    'møder klienten':   { stadie: 3, egenskab: 1, kategori: 'moede' },

    // Stadie 4 — The Long Tide
    'long tide':        { stadie: 4, kategori: 'rytme' },
    'instinktiv':       { stadie: 4, kategori: 'rytme' },

    // Generelle ord — bygger sig op på alle stadier, central både for behandler og klient
    'tryg':             { kategori: 'general', tema: 'tryghed' },
    'tryghed':          { kategori: 'general', tema: 'tryghed' },
    'tillid':           { kategori: 'general', tema: 'tillid' },
    'hjælpe':           { kategori: 'general', tema: 'hjælp', note: 'central for behandlerens identitet' },
    'hjælp':            { kategori: 'general', tema: 'hjælp' },

    // Tvetydige ord — citat-only, ingen automatisk placering
    'balance':          { kategori: 'ambiguous' },
    'nervesystem':      { kategori: 'ambiguous' },
    'naturligt':        { kategori: 'ambiguous' },
    'naturlig':         { kategori: 'ambiguous' },
    'forståelse':       { kategori: 'ambiguous' },
    'rækkefølge':       { kategori: 'ambiguous' },
    'betydning':        { kategori: 'ambiguous' },
    'tilfreds':         { kategori: 'ambiguous' }
  };

  // === BESKRIVELSER AF KATEGORIER ===
  // Bruges når app'en skal tale om mønstre i sproget
  const KATEGORI_BESKRIVELSE = {
    'outcome':      { stadie: 1, beskrivelse: 'søgte resultater', modsætning: 'hvilede i processen' },
    'forklaring':   { stadie: 1, beskrivelse: 'søgte forklaring', modsætning: 'hvilede i ikke-viden' },
    'tvivl':        { stadie: 1, beskrivelse: 'rummede tvivl', modsætning: 'havde tillid' },
    'teknik':       { stadie: 1, beskrivelse: 'søgte teknik', modsætning: 'lyttede uden greb' },
    'frygt':        { stadie: 1, beskrivelse: 'var båret af bekymring', modsætning: 'hvilede i sig selv' },
    'kontrol':      { stadie: 1, beskrivelse: 'havde brug for kontrol', modsætning: 'kunne slippe' },
    'agenda':       { stadie: 1, beskrivelse: 'havde en agenda', modsætning: 'var åben uden agenda' },
    'overgang':     { stadie: 2, beskrivelse: 'rummer slip og åbenhed' },
    'resonans':     { stadie: 3, beskrivelse: 'mærker resonans frem for forklaring' },
    'lytten':       { egenskab: 1, beskrivelse: 'rummer lytten' },
    'taalmodighed': { egenskab: 4, beskrivelse: 'rummer tålmodighed og uvished' },
    'relationel':   { stadie: 3, beskrivelse: 'mærker det fælles felt' },
    'moede':        { stadie: 3, beskrivelse: 'taler om mødet' },
    'rytme':        { stadie: 4, beskrivelse: 'rummer instinktiv rytme' },
    'kropsmarker':  { stadie: 1, beskrivelse: 'bærer kropslig anspændthed' }
  };

  // === MATCHING ===
  // Find alle thesaurus-ord der optræder som understreng i teksten.
  // Returnerer en liste af { ord, mapping } for hvert match.
  function match(tekst) {
    if (!tekst) return [];
    const lower = tekst.toLowerCase();
    const fundne = [];
    for (const ord in ORD) {
      // Simpel substring-match. Multi-word-fraser ('for meget') matcher
      // ordret. Enkelt-ord matcher også som del af bøjede former
      // ('venter' matcher 'venter', men også 'ventede' — det er bevidst,
      // da bøjninger bærer samme tema).
      if (lower.includes(ord)) {
        fundne.push({ ord, mapping: ORD[ord] });
      }
    }
    return fundne;
  }

  // === DIFF ===
  // Sammenlign matches mellem to tekster. Returnerer hvad der er kommet
  // til, hvad der er forsvundet, og hvad der er bevaret.
  function diff(tekstFør, tekstNu) {
    const før = match(tekstFør).map(m => m.ord);
    const nu = match(tekstNu).map(m => m.ord);
    const førSæt = new Set(før);
    const nuSæt = new Set(nu);
    const kommetTil = nu.filter(o => !førSæt.has(o));
    const forsvundet = før.filter(o => !nuSæt.has(o));
    const beholdt = nu.filter(o => førSæt.has(o));
    return {
      kommetTil: kommetTil.map(o => ({ ord: o, mapping: ORD[o] })),
      forsvundet: forsvundet.map(o => ({ ord: o, mapping: ORD[o] })),
      beholdt: beholdt.map(o => ({ ord: o, mapping: ORD[o] }))
    };
  }

  // === DOMINERENDE STADIE I EN TEKST ===
  // Brug ord-matches til at vurdere hvor på rejsen sproget peger hen.
  // Returnerer { stadie: 1-5, fordeling: {1: n, 2: n, ...} } eller null
  // hvis ingen ord kan placeres.
  function dominerendeStadie(tekst) {
    const fordeling = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    let total = 0;
    match(tekst).forEach(({ mapping }) => {
      if (mapping.stadie && !mapping.inverteret) {
        fordeling[mapping.stadie] += 1;
        total += 1;
      } else if (mapping.stadie && mapping.inverteret) {
        // Inverteret betyder ordet markerer afstand fra stadiet — vi
        // tæller stadig, men bruger info'en når app'en formulerer.
        fordeling[mapping.stadie] += 1;
        total += 1;
      }
    });
    if (total === 0) return null;
    let dom = 1, max = 0;
    for (const k in fordeling) {
      if (fordeling[k] > max) { max = fordeling[k]; dom = parseInt(k, 10); }
    }
    return { stadie: dom, fordeling, total };
  }

  // === EKSPONERING ===
  window.SpejlThesaurus = {
    ord: ORD,
    kategorier: KATEGORI_BESKRIVELSE,
    match,
    diff,
    dominerendeStadie
  };
})();
