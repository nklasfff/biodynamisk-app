# Hero-illustrationer

Appens centrale visuelle element. Sfæriske kugler med radial gradient, soft glow, og subtil pulseren. Bygges som genbrugelige SVG-komponenter i koden — ikke som 60 statiske filer.

## Det visuelle sprog

Alle hero-illustrationer deler samme grundkvalitet:
- **Sfærisk dybde** via radial gradient (lys øverst-venstre, dyb nederst-højre)
- **Soft glow** rundt om kuglen (Gaussian blur, samme farvefamilie)
- **Subtilt højlys** (lysere radial gradient øverst-venstre for ekstra volumen)
- **Tynd hvid stroke** på kuglens kant (0.5 px, opacity 0.25)
- **Soft shadow** under kuglen (Gaussian blur, forskydning nedad)
- **Pulseren** — åndedrag-lignende, 6 sekunder pr. cyklus

## SVG-komponenten: Basis-kugle

Alle varianter bygger på denne grundkugle:

```html
<svg viewBox="0 0 400 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="[beskrivelse]">
  <defs>
    <radialGradient id="sphere-[id]" cx="35%" cy="28%" r="75%">
      <stop offset="0%" stop-color="#C9D4DE"/>
      <stop offset="35%" stop-color="#8FA3B8"/>
      <stop offset="70%" stop-color="#5E748A"/>
      <stop offset="100%" stop-color="#3A4A5C"/>
    </radialGradient>

    <radialGradient id="glow-[id]" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#8FA3B8" stop-opacity="0.35"/>
      <stop offset="50%" stop-color="#8FA3B8" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#8FA3B8" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="highlight-[id]" cx="32%" cy="25%" r="30%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="#FFFFFF" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>

    <filter id="blur-[id]" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>

    <filter id="shadow-[id]" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" in="SourceGraphic" result="blur"/>
      <feOffset in="blur" dx="0" dy="6" result="offset"/>
      <feComponentTransfer in="offset" result="shadow">
        <feFuncA type="linear" slope="0.25"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode in="shadow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Glow-halo (pulserer i opacity) -->
  <ellipse class="hero-glow" cx="200" cy="130" rx="140" ry="140"
           fill="url(#glow-[id])" filter="url(#blur-[id])"/>

  <!-- Kugle-gruppen (pulserer i scale) -->
  <g class="hero-sphere" filter="url(#shadow-[id])">
    <circle cx="200" cy="130" r="85" fill="url(#sphere-[id])"/>
    <ellipse cx="178" cy="108" rx="38" ry="28"
             fill="url(#highlight-[id])" opacity="0.9"/>
    <circle cx="200" cy="130" r="85" fill="none"
            stroke="#FFFFFF" stroke-width="0.5" stroke-opacity="0.25"/>
  </g>
</svg>
```

**Erstatt `[id]` med unik identifier** pr. instans (fx `fulcrum`, `zone-b-venstre`) for at undgå CSS-konflikter når flere kugler er på samme side.

## Pulseren (CSS)

```css
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.015); }
}

@keyframes glow-breathe {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 1; }
}

.hero-sphere {
  animation: breathe 6s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}

.hero-glow {
  animation: glow-breathe 6s ease-in-out infinite;
  transform-origin: center;
  transform-box: fill-box;
}
```

**Regler:**
- 6 sekunder pr. cyklus (svarer til et dybt, roligt åndedrag)
- Scale går fra 1 til 1.015 (subtilt, ikke fedtet)
- Glow pulserer synkront med scale
- `ease-in-out` — ikke lineær
- Overvej `prefers-reduced-motion` — hvis brugeren har sat dette, skal animationen stoppes

## Varianter

### 1. Enkelt-kugle

Brug: begrebsside, kvalitetsside, stadie-side, perspektiv-side, klientmønster-side, princip-side, essay-side.

Én kugle i centrum. Størrelse: radius 85 i et 400×260 viewBox.

### 2. 3-cirkel (til zoner)

Brug: rum-side. Følger bogens venstre-midt-højre-struktur.

Tre kugler på en vandret linje:
- Venstre kugle: cx="100", radius 60, opacity 0.85 (lidt tilbagetrukket)
- Midt-kugle: cx="200", radius 85 (hovedfokus)
- Højre kugle: cx="300", radius 60, opacity 0.85

Alle tre pulserer synkront (samme animation-delay). Evt. svage linjer imellem (stiplede, `stroke-dasharray`).

### 3. 2-cirkel (til integration)

Brug: hvor to ting mødes (fx Venn-lignende koncepter).

To kugler, lidt overlappende. Mellem dem: evt. en lysere zone der antyder overlap.

### 4. Venn-overlap (3-cirkler der overlapper)

Brug: hvor tre koncepter flettes (som bogens "Vejrtrækningens Tre Dimensioner").

Tre kugler arrangeret som triangel. Overlappende områder bliver synlige gennem semi-transparent fill. Kræver lidt mere kompleks SVG med `mask` eller `mix-blend-mode`.

### 5. Konstellation (4-9 kugler)

Brug: oversigtssider hvor vi vil vise et gruppe-felt (fx de 9 principielle begreber).

Central kugle + satellitter i cirkel rundt om. Stiplede linjer mellem dem.

**Bemærk:** 18 kugler fungerer ikke på mobil (for små, ulæselige). Brug i stedet liste-visning på oversigtssider for store grupper.

### 6. Abstrakt motiv (sparsomt)

Brug: hjemmeskærm, evt. essay-sider.

Ikke en kugle, men fx en bølgelinje, en horisontlinje, eller en enkel cirkelform. Samme farver, samme stemning. Bruges sjældent — bryder rytmen.

## Implementation som komponent

Byg som en genbrugelig komponent (vanilla JS web component eller simpel template-funktion):

```javascript
function heroSphere({ id, size = 'normal', label }) {
  // Returnerer SVG-streng med unikke IDs baseret på `id`-parameter
  // `size` kan være 'small', 'normal', 'large'
  // `label` bruges som aria-label
}

function heroTripleCircle({ id, leftLabel, centerLabel, rightLabel }) {
  // 3-cirkel-variant
}

// osv.
```

Komponenten placeres i `components/hero.js` og genbruges på tværs af sidetyper.

## Tilgængelighed

- Alle SVG'er har `role="img"` og `aria-label` der beskriver hvad kuglen repræsenterer (fx "Fulcrum — det dynamiske omdrejningspunkt")
- `prefers-reduced-motion: reduce` → stop animationen
- Kontrast: kuglerne er dekorative, tekst ligger udenfor — ingen kontrast-problemer

## Hvad der ikke hører hjemme her

- Ingen 3D-rotation (rotation stjæler roen — stilhed er kernen)
- Ingen tekst inde i kuglerne (det skærer ind i formen)
- Ingen neon-glow eller stærke effekter (subtilt, ikke iøjnefaldende)
- Ingen farveskift — alle kugler er i samme skifergrå-blå familie
