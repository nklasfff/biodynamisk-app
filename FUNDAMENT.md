# FUNDAMENT — Den Biodynamiske App

*Et levende referencedokument. Læses først i enhver ny samtale om projektet.*

*Sidst opdateret: 19. april 2026 (v2 — arkitektur og typografi fastlagt)*

---

## 0. Om dette dokument

Dette er det destillerede fundament for appen om Den Biodynamiske Model. Det er ikke en kopi af bogen — det er den fælles forståelse mellem Niklas og Claude, bygget op gennem samtaler, som skal bevares på tværs af sessions.

**Brug:** Claude læser dette dokument først i enhver ny samtale om projektet, før der foreslås struktur, tekster, visuelle valg eller kodeløsninger. Niklas kan opdatere det når forståelsen skifter eller nye beslutninger træffes.

**Relation til andre dokumenter:**
- `2029_-_20-9_-_redigeret.docx` — selve bogen, primær kilde. Søges i med `project_knowledge_search`.
- SVG-illustrationer i mappen `dbm_visual` — det etablerede visuelle sprog.
- `hero_dbm.png` — havbilledet der fastlægger stemningen.
- Senere: `CLAUDE.md` — afledt af dette dokument, skrevet når vi er klar til at bygge i Claude Code.

---

## 1. Projektet kort

Niklas skriver en bog om Den Biodynamiske Model til kraniosakrale behandlere og beslægtede fagfolk. Bogen er nu et næsten komplet manuskript på ca. 36.000 ord fordelt på 4 dele og 13 kapitler. Appen skal ikke være bogen i app-format. Den skal være noget bogen ikke kan være.

**Hvem:** Fagfolk i feltet — behandlere der kender sproget. Ikke lægfolk, ikke kun Niklas' egne kursister.

**Hvad appen skal kunne:**
- Opslag — slå begreber op, få præcis information
- Udforskning — vandre i modellen uden bestemt formål
- Inspiration — finde hjælp når man står fast i praksis
- Relationer synlige — lade brugeren opleve hvordan elementer taler sammen
- Indhold der ikke findes i bogen — relationer mellem de 8 kvaliteter fx, som kun giver mening i dynamisk medie

**Platform:** PWA på GitHub Pages. Bygges i Claude Code på Niklas' Mac.

---

## 2. Det filosofiske fundament

### 2.1 Bohm som ankerpunkt

David Bohms *implicate* og *explicate order* er den nærmeste filosofiske analogi til Den Biodynamiske Models grundsyn. Det manifesterede er ikke adskilt fra det implicite — det er foldninger af samme underliggende virkelighed, konstant foldet ud og tilbage.

Dynamisk Stilhed er ikke "før" Breath of Life på en tidsakse. Den er altid til stede, som det implicite, mens Breath of Life, Primary Respiration, Fluid Body og fysisk krop er samtidige manifestationer af samme stilhed i forskellige foldninger. Kroppen kan "huske" sin oprindelse fordi oprindelsen aldrig forsvandt — den er altid foldet ind.

### 2.2 De to grundakser (ét princip, to vinkler)

**Akse 1 — De embryologiske kræfter som kontinuum:**
De kræfter der skabte fostret laver aldrig fejl. Det de gør er altid intelligent, altid hensigtsmæssigt, altid den bedst mulige løsning givet øjeblikkets betingelser. De opererer udenfor generne — som en selvorganiserende intelligens med helheden for øje. Det radikale er påstanden om kontinuitet: disse kræfter er ikke ophørt. Det er *de samme kræfter* der vedligeholder kroppen nu, heler efter skade, integrerer traumer. Vedligeholdelse, vækst, restaurering, transformation er variationer af samme grundlæggende bevægelse. Epigenetikken bekræfter det fra en anden vinkel.

**Akse 2 — Det relationelle som biologisk fundament:**
Det relationelle er ikke en tilføjelse til det individuelle — det er bygget ind i nervesystemets grundarkitektur fra fosterstadiet. Polyvagal teori viser at pattedyrs nervesystem er bygget til co-regulering. Vi regulerer os aldrig fuldt ud alene. Det gælder alle lag: normal funktion, mild ubalance, stress, sygdom, traumer. Det relationelle er centralt overalt.

**De to akser er ét princip:** De embryologiske kræfter skabte nervesystemet. Nervesystemet blev skabt til relation. Derfor er de embryologiske kræfter altid allerede indlejret i det relationelle — og det relationelle er altid allerede et udtryk for de embryologiske kræfter.

### 2.3 Bærende principper

Disse må gennemsyre appens struktur og opførsel:

- **Helhed først, dele siden.** Organismen starter som ubrudt helhed; dele træder frem gennem differentiering. En del er altid aspekt af helheden, aldrig isoleret enhed.
- **A-kausalitet.** Systemet bygger ikke på lineær årsag → virkning. Primary Respiration re-mønstrerer fra et niveau *før* normale kausale sammenhænge.
- **Bevægelse før form.** Blechschmidts princip. Først pulsering, derefter dannes hjertet. Struktur er øjebliksaspekt af underliggende bevægelse.
- **Samtidig tilstedeværelse.** Alle 18 begreber, alle 5 zoner, alle 5 stadier eksisterer samtidigt i enhver behandling. Det der skifter er hvad der er i forgrunden.
- **Cirkulær, ikke lineær.** Udvikling er spiral, ikke stige. Vi genbesøger samme landskaber fra dybere niveauer.
- **Det umistelige.** The Health kan ikke mistes. Potency kan ikke forøges eller formindskes. Potentialet kan ikke ødelægges, kun miste kontakten. Intet skal tilføjes — kun kontakt genoprettes.
- **Not-knowing som forudsætning.** Behandleren skaber ikke heling, men betingelser. Processen dirigeres af kræfterne, ikke af behandlerens plan.
- **Stilhed som kilde.** Dynamisk Stilhed er ikke fravær af bevægelse — den er bevægelsens ophav. Tomme rum, pauser, luft er aktive, ikke tomme.

---

## 3. Modellens indhold — hvordan det hænger sammen

### 3.1 Hierarkiet af manifestation

Fra det implicite til det eksplicite, samtidig til stede i alle lag:

1. **Dynamisk Stilhed** — det dybeste lag, umanifesteret potentiale, kilden
2. **Breath of Life** — første udtryk, rent energetisk, kaleidoskopisk, uden fast form
3. **Primary Respiration** — energien bliver til rytmer i det biologiske
   - **The Long Tide** — energien/skabelonen fra horisonten mod midtlinjen (100 sek/cyklus)
   - **The Fluid Tide** — når Long Tide rammer midtlinjen, gennem væskekroppen (2-3 cyklusser/min)
4. **Fluid Body** — broen mellem energi og fysisk form
5. **Fysisk krop** — den konkrete manifestation

Kapitel 6's 5 zoner (A-E) er samme hierarki anvendt på behandlingssituationen: Rum A fysisk krop, Rum B væskekrop, Rum C relationelt felt, Rum D The Long Tide/Primary Respiration, Rum E Dynamisk Stilhed. Det relationelle felt (Rum C) er placeret mellem væskekrop og Primary Respiration — biologisk præcist, for det er gennem væskekroppens åbning at det relationelle bliver muligt, og det er gennem det relationelle felt at Primary Respiration kan virke mellem to mennesker.

### 3.2 De 18 begreber i tre naturlige grupper

De 18 begreber er *ikke* én flad liste. De tjener forskellige funktioner:

**Gruppe 1 — Principielle/strukturelle begreber** (modellens arkitektur, ontologiske):
Dynamisk Stilhed, Breath of Life, Primary Respiration (inkl. Long Tide og Fluid Tide), Midtlinjen, The Health, Fluid Body, Wholeness, Potency, Axial Fluctuations.

**Gruppe 2 — Behandlings-fænomener** (hvad behandleren møder og mærker, fænomenologiske):
The Neutral, Motion Present, Fulcrum, Stillpoints, Transmutation, Automatic Shifting, Ignition, Den Iboende Behandlingsplan.

**Gruppe 3 — Patologisk/dysfunktionelt**:
The Lesion Field — det isolerede område der har mistet forbindelsen til helheden (men altid rummer Motion Present).

Denne gruppering skal bære appens struktur. De 18 begreber kan ikke bare være 18 cirkler på række.

### 3.3 Nøgledistinktioner der har konsekvenser for appen

**Fulcrum vs. Stillpoint:**
Fulcrum er et omdrejningspunkt i det levende — både sundt (bevægeligt, dynamisk anker) og dysfunktionelt (rigidt, isolerende). Det er en tilstand/struktur.
Stillpoint er en proces — den terapeutiske dynamik hvor noget går ind i reguleringsfase og forvandles. Det er ikke hvor noget *er*, men hvor noget *sker*.

**The Neutral — biologisk fænomen OG tilstand (samme ting, to sprog):**
Fysiologisk: det autonome nervesystem suspenderes. Kvalitativt: væv, væske og energi kommer i samklang med samme grundtonalitet ("everything cling to the same tonality"). Resultat: kroppen genvinder *stamcellens kapacitet* — midlertidig de-differentiering — og bliver åben for enhver retning. Det er forudsætningen for at de embryologiske kræfter kan udfolde deres fulde potentiale. Udenfor The Neutral arbejder de også, men med strukturelle begrænsninger.

**De embryologiske kræfter = de helende kræfter:**
Ikke to forskellige sæt kræfter. Samme intelligens, forskellige navne afhængigt af kontekst. Heling er ikke en speciel proces der aktiveres ved skade — det er hvad kræfterne gør hele tiden. Det bliver bare tydeligere ved skade fordi kroppen kalder mere åbenlyst på deres arbejde.

### 3.4 Bogens arkitektur

**Part I — Model og ophav:**
- Kap 1: Den Biodynamiske Model (5 intro-essays)
- Kap 2: Blechschmidts 9 embryologiske principper
- Kap 3: De 18 Biodynamiske Begreber
- Kap 4: I Behandlingssituationen (begreberne vævet sammen)

**Part II — Behandleren & behandlingen:**
- Kap 5: De 8 Essentielle Egenskaber
- Kap 6: De 5 Rum (A-E)
- Kap 7: 9 typiske klientmønstre

**Part III — Den indre rejse:**
- Kap 8: De 5 Stadier i behandlerens udvikling
- Kap 9: De 7 Perspektiver på transformation
- Kap 10: 4 Guidede Øvelser

**Part IV — Traditioner & inspirationer:**
- Kap 11: Andre traditioner + Specielle Temaer
- Kap 12: Integration i eksisterende praksis
- Kap 13: Afslutning

Ordliste og litteraturliste efterfølger.

**Hvert hovedkapitel har en "Invitationer til Refleksioner"-sektion** med færdige refleksionsspørgsmål skrevet af Niklas. De er del af bogen, ikke noget vi opfinder.

---

## 4. Det visuelle sprog

Niklas har etableret et konsistent grafisk sprog som appen skal tale:

**Paletten** — direkte oversat fra havbilledet (`hero_dbm.png`):
- Himmel: varm lysegrå til blødt blågrå (#DDE4EB → #B8C4D1)
- Horisont: næsten hvid med varme (#E8ECEF)
- Vandets dybeste: skifergrå-blå (#2B3C4F → #3A4A5C)
- Baggrund: varm off-white (#F4F2ED)
- Tekst primær: dyb skifer (#2B3C4F)
- Tekst sekundær: rolig grå-blå (#7C8894)

Én sammenhængende kølig-men-varm skifergrå-blå familie. Ingen sekundær accentfarve. Det er ensheden der skaber eksklusivitet.

**Formsproget:**
- Cirkler, ikke firkanter eller kort
- Central cirkel + satellitter i ring eller geometrisk mønster
- Tynde faste eller stiplede linjer mellem dem (netværket synligt)
- Nogle gange 3-cirkel-layout (venstre, midt, højre) for zoner
- Nogle gange Venn-lignende overlap for integration
- Meget luft omkring alt

**Typografi (fastlagt):**

To skrifter, ingen tredje. Den overordnede logik: **Cinzel åbner rummet, Cormorant bærer indholdet.** Cinzel siger *hvor du er*. Cormorant fortæller *hvad der er*.

**Cinzel** — display-skrift, kun i versaler
- Vægte: Light (300) og Regular (400)
- Bruges til: store titler ("FULCRUM", "RUM A", "MODELLEN"), kategori-labels ("BEHANDLINGS-FÆNOMEN · 7"), navigation-labels, metadata, tal og etiketter
- Altid versaler, altid letter-spacing 2-4px, aldrig under 10px, aldrig som brødtekst

**Cormorant Garamond** — læse- og prosaskrift
- Vægte: Light (300), Regular (400), Medium (500), Italic 300/400
- Bruges til: al brødtekst, undertitler ("det dynamiske omdrejningspunkt"), kort-overskrifter ("Det grundlæggende"), alle interaktive labels med tekst, kursive citater og refleksionsspørgsmål, tilbage-knap
- Kan være regular, medium eller italic — aldrig versaler undtagen enkelte bogstaver

**Fast størrelseshierarki:**
- Cinzel hovedtitel: 32px, vægt 400, letter-spacing 3px
- Cinzel stor label: 12-14px, vægt 300, letter-spacing 3-4px
- Cinzel lille label: 10-11px, vægt 300, letter-spacing 3-4px
- Cormorant sektionstitel: 22-24px, vægt 400
- Cormorant undertitel kursiv: 16px, vægt 400 italic
- Cormorant brødtekst: 17px, vægt 400, line-height 1.75
- Cormorant kort-overskrift: 17px, vægt 500
- Cormorant lille kursiv/metadata: 14px, vægt 400 italic

**Google Fonts-import:**
```
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Cinzel:wght@300;400&display=swap');
```

**Hvad vi ikke bruger:** ingen tredje skrift (ingen Inter, Work Sans, Lato, etc.), ingen Cormorant i versaler, ingen Cinzel som brødtekst, ingen Cinzel i små størrelser under 10px.

**Baggrundsfarver (opdateret):**
- Primær baggrund: `#faf8f5` (varm off-white, lidt lysere end `#F4F2ED`)
- Sekundær/ydre baggrund: `#f4f1ed`

**Dette skal appen tale flydende.** SVG'erne fra bogen er ikke bare illustrationer — de er byggesten i appen.

---

## 5. Appens karakter

### 5.1 Tre lag

**Lag 1 — Bogen:** Alt tekstindhold. De 18 begreber, 8 kvaliteter, 5 zoner, 5 stadier, 7 perspektiver, 4 øvelser, traditionerne, refleksionerne. Næsten al tekst fra bogen skal med — ikke kondenseret. Niklas' sprog bærer forståelsen.

**Lag 2 — Cirklerne som interaktion:** SVG-diagrammerne bliver interaktive. Cirklen *er* navigationen, og samtidig *er* cirklen del af forståelsen. Form og indhold er ét.

**Lag 3 — Forbindelserne:** Det underliggende netværk af hvordan alt hænger sammen. Det tredje lag gør appen til mere end en bog. Fra en begrebsside springer man til alle steder begrebet optræder. Fra en kvalitet ser man dens relation til hver af de andre. Fra et rum ser man hvilke begreber der særligt kalder her.

### 5.2 Konsekvenser for interfacet

**Vigtig distinktion:** Det biodynamiske er det appen *handler om*, ikke hvordan den er *bygget*. Strukturen og arkitekturen skal primært være overskuelig, intuitiv, let og logisk for brugeren. Vi må ikke blive fikseret af at alt skal være biodynamisk — fx fungerer en figur med 18 cirkler ikke på en smartphone hvis man skal kunne læse tekst og trykke på dem. God brugeroplevelse er vigtigere end filosofisk renhed i selve strukturen.

Med det sagt, disse principper bør stadig være til stede hvor de *kan* være det uden at gå på kompromis med brugervenlighed:

- Ingen hierarkisk træstruktur med drop-downs
- Ingen "næste"/"forrige"-knapper eller lineær progression påtvunget
- Cirkulær navigation — altid tilbage til samme punkter fra forskellige veje
- Pauser og stilhed i interfacet — hvid luft er aktiv
- Relationer synlige, ikke skjulte
- Ingen "du har gået glip af noget"-følelse. Alt er der altid. Det man møder er det der er i forgrunden lige nu.
- Appens *opførsel* i det biodynamiske indhold (sproget, stemningen, tonen) skal afspejle modellen. Navigationen skal bare fungere.

### 5.3 Det appen kan gøre bogen ikke kan

Konkrete eksempler på dynamikker vi har diskuteret:

- **Kvaliteternes relationer:** Vælg én af de 8 kvaliteter, se hvordan den taler med hver af de 7 andre. 56 små tekster der ville være tunge i en bog, men naturlige i en app.
- **Begreber på tværs af kapitler:** Tryk på Fulcrum, se hvor det optræder — i kapitel 3, i Rum A, i øvelsen "Kroppens Dynamiske Landskaber", i klientmønsteret "Gamle Traumer". Samme begreb, fire forskellige lys.
- **Klientmønster → alt andet:** Brugeren står fast i praksis med en klient. Vælg et mønster (fx "klienten går ikke til neutral"), få foldet ud hvilke zoner der arbejder, hvilke kvaliteter der kaldes på, hvilke begreber der er relevante.

Disse relationer findes ikke eksplicit i bogen. De skal skrives som supplement — og det er noget Niklas først kan skrive når vi ved hvilke relationer der er vigtigst.

### 5.4 Informationsarkitektur (fastlagt)

**Hjemmeskærm — ankomstrum:**
Appen åbner med hero-billedet (havet), en kort invitation, og fire indgange til modellen. Ankomst først, retning derefter. Hjemmeskærmen er ikke én af fanerne i bundnavigationen — den er udgangspunktet og det kendte sted man altid kan vende tilbage til.

**De fire indgange (hovedsektioner):**
1. **Modellen** — modellens ontologi (Part I: De 5 intro-essays, Blechschmidt, De 18 begreber, I behandlingssituationen)
2. **Behandleren** — praksis (Part II: De 8 essentielle egenskaber, De 5 zoner, Typiske klientmønstre)
3. **Rejsen** — udvikling (Part III: De 5 stadier, De 7 perspektiver, De 4 guidede øvelser)
4. **Inspiration** — integration (Part IV: Andre traditioner, Integration i praksis, Afslutning)

Disse fire er ikke tilfældige kapitelinddelinger — de afspejler fire fundamentalt forskellige perspektiver på det biodynamiske: ontologi, praksis, udvikling, integration. De matcher hvordan en behandler tænker.

**Navigation — fuld frihed:**
Brugeren kan bevæge sig på tre måder samtidigt:
- Via **hjemmeskærmen** — altid tilgængelig som kendt startpunkt
- Via **bundnavigation** — fire faner altid synlige, hurtig skift mellem sektioner
- Via **relationer** — springveje mellem elementer på tværs af sektioner

Ingen bevægelse er forbudt. Brugeren kan både slå op hurtigt og vandre langsomt.

### 5.5 Side-struktur (fastlagt som mønster)

**Progressive disclosure som grundprincip:** Der er meget tekst i bogen, og alt skal med. Løsningen er lagvis åbning af information gennem foldbare kort — inspireret af velfungerende patterns i apps der håndterer meget information (fx organ-apps). Ét mønster der gentages gennem hele appen, så brugeren lærer ét system at navigere i.

**Tre niveauer af information (gennemgående):**
- **Niveau 1 — Oversigt/navigation:** Hvor er jeg, hvad kan jeg vælge?
- **Niveau 2 — Emneside med foldbare kort:** Alle aspekter af et emne, foldet sammen
- **Niveau 3 — Indholdet inde i et kort:** Selve teksten, refleksionen, relationerne

**Standard begrebsside-struktur (fx Fulcrum):**
1. **Øverste linje:** Tilbage-knap til forrige niveau + lille label i Cinzel ("DE 18 BEGREBER")
2. **Kategori-label (Cinzel):** "BEHANDLINGS-FÆNOMEN · 7"
3. **Hero-illustration:** Den sfæriske kugle med subtil pulseren (6 sek cyklus)
4. **Hovedtitel i versaler (Cinzel):** "FULCRUM"
5. **Undertitel kursiv (Cormorant italic):** "det dynamiske omdrejningspunkt"
6. **Tynd vandret skiller-streg:** visuel åndepause
7. **Kort intro-tekst centreret:** 2-3 linjer der altid er synlige
8. **Foldbare kort:** typisk 5 stk., hver med venstre-streg som markør
   - Det grundlæggende
   - Unikke aspekter (fx "Sunde fulcrums", "Dysfunktionelle fulcrums" — specifikke pr. begreb)
   - Relationer (todelt: "Hænger sammen med" andre begreber + "Lever også i" andre sektioner)
   - Til refleksion (refleksionsspørgsmål fra bogen)

**Kort-design:**
- Baggrund: `rgba(255,255,255,0.55)` — let transparent på side-baggrund
- Border: `0.5px solid rgba(43, 60, 79, 0.12)`
- Border-radius: 12px
- Venstre-markør: 4px bred streg, 18px høj, i `#5B6A78` med opacity 0.5
- Kort-overskrift: Cormorant 17px medium
- Chevron ▾ roterer 180° ved åbning
- Margin mellem kort: 10px

**Hero-illustrationer — fast system:**

Gennemgående visuelt motiv: **sfærisk cirkel med subtil pulseren**. Ingen flade cirkler — altid med radial gradient (lys øverst-venstre, dyb nederst-højre), soft glow, subtilt højlys. Én eller flere kugler afhængigt af konteksten.

Typer af hero-illustrationer vi kommer til at bruge:
- **Enkelt-cirkel** (fx begrebsside): én kugle i centrum
- **2-cirkel** (fx integration af to ting)
- **3-cirkel** (fx zoner med midt/venstre/højre)
- **Venn-overlap** (fx Vejrtrækningens Tre Dimensioner — ting der integrerer)
- **4-5 cirkler** (fx mindre konstellationer)
- **Konstellation** (fx de 18 begreber — sjælden brug pga. smartphone-læsbarhed)
- **Abstrakte motiver** (fx bølgelinjer inspireret af havbilledet) — sparsomt brug

Alle illustrationer er i samme skifergrå-blå-familie, samme visuelle sprog (gradient + glow + højlys), så appen føles sammenhængende.

**Svag pulseren:**
- Kugler: `scale(1)` → `scale(1.015)` → `scale(1)` over 6 sekunder (ease-in-out)
- Glow-halo: opacity 0.85 → 1.0 → 0.85 over 6 sekunder
- Som et åndedrag, ikke som en alarm

**Side-rytme og luft:**
- Generøs padding omkring hero (2.5rem top, 1.5rem sider)
- Tynd skiller-streg mellem hero og brødtekst (`#5B6A78` ved opacity 0.35, 32px bred, 0.5px høj)
- Brødtekst-padding: 2rem horisontalt
- Kort-sektion-padding: 1.25-1.5rem horisontalt

---

## 6. Arbejdsproces og rækkefølge

### 6.1 Hvor vi er nu

- Bogen er lagt i projektet (`2029_-_20-9_-_redigeret.docx`)
- SVG-illustrationer er lagt i `dbm_visual`-mappen
- `hero_dbm.png` (havbilledet) er lagt i projektet
- Forståelsen af principperne er etableret
- Informationsarkitektur er fastlagt (sektion 5.4)
- Side-struktur med foldbare kort er fastlagt (sektion 5.5)
- Typografi-strategi er fastlagt (Cinzel + Cormorant Garamond, se sektion 4)
- Hero-illustration-princip er fastlagt (sfærisk kugle med subtil pulseren)
- Én nøgleskærm er bygget og godkendt: Fulcrum-siden

### 6.2 Næste skridt

1. **Bygge flere side-typer** — fx oversigten over de 18 begreber (niveau 1-skærm), en rum-side (3-cirkel hero), eller en sektions-indgangsside ("Modellen"-oversigten). Brugt til at udforske hvordan mønsteret tilpasses forskellige typer indhold.
2. **Hjemmeskærm-mockup** — hero-billedet med de fire indgange. En afgørende skærm at få rigtigt.
3. **Indholds-JSON** — al bogens tekst organiseret, alle refleksioner, alle relationer kortlagt. Stort stykke arbejde. Baseret på bogen i projektet.
4. **Supplerende tekster** (dem Niklas skal skrive) — særligt relationsbeskrivelser der ikke findes i bogen.
5. **`CLAUDE.md`** — afledt af alt ovenstående. Lægges i Claude Code-projektets rodmappe og læses automatisk ved hver session.
6. **Byg i Claude Code.**

### 6.3 Hvordan vi arbejder

Stille og roligt. Fundamentet er vigtigere end tempo. Claude foreslår ikke struktur eller løsninger uden at have fundamentet klart. Niklas styrer tempoet. Fremtidige Claude-sessions læser dette dokument først.

---

## 7. Åbne spørgsmål og uafklarede områder

Områder vi ikke har afgjort endnu — vigtigt at Claude ikke antager noget her uden at spørge:

- Skal der være en journal-/notat-funktion for læseren? (Oprindeligt foreslået som "min bog" — Niklas afviste den formulering. Uklart om funktionen i sig selv skal være der.)
- Skal bogens fulde tekst altid være tilgængelig i de foldbare kort? (Princippet er ja, men der kan være sektioner hvor kortere versioner giver mening — afklares når vi bygger konkrete sider.)
- Skal de 9 Blechschmidt-principper (kap 2) have samme tyngde som de 18 begreber, eller være underordnet?
- Lyd — skal Niklas indtale de 4 guidede øvelser? (Ikke afgjort.)
- Præcis hvilke relationer er vigtigst for brugeren at se? (Kvaliteternes indbyrdes relationer er bekræftet; de 18 begrebers relationer er sandsynlige; andre er uafklarede.)
- Hero-illustration på hjemmeskærmen — er det havbilledet som fotografi, eller et abstrakt grafisk motiv inspireret af det? (Afklares når vi bygger hjemmeskærmen.)
- Ikoner/symboler i bundnavigationen — præcis design. (Arbejdsforslag eksisterer; kan forfines.)

---

## 8. Det Claude endnu ikke har fuld forståelse af

Ærlige begrænsninger — Claude læser teksten og genkender den, men mangler behandlerens direkte erfaring:

- **Den sansemæssige forskel** mellem The Long Tide, The Fluid Tide og Primary Respiration. Forskellene beskrives, men den direkte sanse-kvalitet må Niklas kalibrere.
- **Den relationelle dimension i praksis** — hvordan det faktisk føles når to nervesystemer co-regulerer i Rum C. Læses, ikke mærkes.
- **Hierarkiet indbyrdes mellem de 18 begreber på detaljeniveau** — de tre grupper er klare, men finere skel (fx om Wholeness og Dynamisk Stilhed er på nøjagtig samme niveau) er noget der først afklares gennem konkret arbejde med relationerne.

Disse begrænsninger betyder at Niklas skal kalibrere når Claude foreslår noget der skal *lede brugeren ind* i en sanselig eller relationel oplevelse. Claude kan strukturere det, men ikke bære det alene.

---

*Slut på FUNDAMENT.md*
