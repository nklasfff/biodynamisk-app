# Design-system

Alle visuelle valg for appen. CSS-variabler defineres i `:root` og genbruges i hele kodebasen.

## Farvepalet

Én sammenhængende skifergrå-blå familie. Ingen sekundær accentfarve.

```css
:root {
  /* Baggrunde */
  --bg-primary: #faf8f5;      /* Siders baggrund, varm off-white */
  --bg-secondary: #f4f1ed;    /* Ydre baggrund, fx bag hovedcontainer */
  --bg-card: rgba(255, 255, 255, 0.55);  /* Foldbare kort */

  /* Tekst */
  --text-primary: #2B3C4F;    /* Dyb skifer, al brødtekst */
  --text-secondary: #5B6A78;  /* Rolig grå-blå, underordnet tekst */
  --text-muted: #7C8894;      /* Metadata, placeholder */
  --text-label: #9AA6B3;      /* Små labels i Cinzel */

  /* Borders & accents */
  --border-card: rgba(43, 60, 79, 0.12);
  --border-card-hover: rgba(43, 60, 79, 0.25);
  --accent-line: rgba(91, 106, 120, 0.5);  /* Venstre-streg på kort */
  --divider: rgba(91, 106, 120, 0.35);     /* Vandrette skillestreger */

  /* Kugle-gradient (SVG) */
  --sphere-light: #C9D4DE;
  --sphere-mid: #8FA3B8;
  --sphere-deep: #5E748A;
  --sphere-dark: #3A4A5C;
}
```

## Typografi

To skrifter. Cinzel åbner rummet, Cormorant bærer indholdet.

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Cinzel:wght@300;400&display=swap');

:root {
  --font-display: 'Cinzel', serif;
  --font-body: 'Cormorant Garamond', Georgia, serif;
}
```

### Cinzel — display, altid versaler

| Brug | Størrelse | Vægt | Letter-spacing |
|------|-----------|------|----------------|
| Hovedtitel (fx "FULCRUM") | 32px | 400 | 3px |
| Stor label (fx "BEHANDLINGS-FÆNOMEN · 7") | 12-14px | 300 | 3-4px |
| Lille label (fx "DE 18 BEGREBER") | 10-11px | 300 | 3-4px |

**Regler:**
- ALTID versaler (`text-transform: uppercase`)
- Aldrig under 10px
- Aldrig som brødtekst

### Cormorant Garamond — læse og prosa

| Brug | Størrelse | Vægt | Style |
|------|-----------|------|-------|
| Sektionstitel (når den står alene) | 22-24px | 400 | normal |
| Undertitel kursiv (fx "det dynamiske omdrejningspunkt") | 16px | 400 | italic |
| Brødtekst | 17px | 400 | normal (`line-height: 1.75`) |
| Kort-overskrift | 17px | 500 | normal |
| Lille kursiv / metadata | 14px | 400 | italic |
| Tilbage-knap | 14px | 400 | italic |

**Regler:**
- Aldrig versaler (undtagen enkelte bogstaver)
- Kursiv bruges til undertitler, citater, refleksionsspørgsmål

## Layout-tokens

```css
:root {
  /* Border-radius */
  --radius-card: 12px;
  --radius-pill: 20px;
  --radius-screen: 28px;  /* Ydre container på mobil */

  /* Spacing */
  --space-card-gap: 10px;       /* Mellem foldbare kort */
  --space-section: 2rem;         /* Mellem større sektioner */
  --space-hero-bottom: 1.5rem;   /* Under hero-illustration */

  /* Kort-dimensioner */
  --card-padding: 16px 18px;
  --card-marker-width: 4px;
  --card-marker-height: 18px;
}
```

## Komponent-specifikationer

### Foldbart kort

Den mest brugte komponent. Specifikation:

```
┌─────────────────────────────────────────┐
│ ▎ Overskrift                        ▾  │  ← lukket
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ▎ Overskrift                        ▴  │
├─────────────────────────────────────────┤
│   Indhold i brødtekst, Cormorant 17px   │  ← åbnet
│   med line-height 1.75 ...              │
└─────────────────────────────────────────┘
```

- Baggrund: `var(--bg-card)`
- Border: `0.5px solid var(--border-card)` (bliver `var(--border-card-hover)` når åben)
- Border-radius: `var(--radius-card)`
- Padding: `var(--card-padding)`
- Venstre-markør: 4×18px, `var(--accent-line)`, border-radius 2px
- Chevron `▾` roterer 180° ved åbning (CSS transition 0.2s)
- Åbning animeres med `max-height` transition 0.3s ease
- Margin mellem kort: `var(--space-card-gap)`

### Pill (til relationer)

Små klikbare labels der linker til andre enheder.

```
┌─────────────────┐
│ • Midtlinjen    │  ← "hænger sammen med" (prik)
└─────────────────┘
┌─────────────────┐
│ ◆ Zone A        │  ← "lever også i" (lille firkant)
└─────────────────┘
```

- Baggrund: `rgba(91, 106, 120, 0.08)`
- Border: `0.5px solid rgba(91, 106, 120, 0.2)`
- Border-radius: `var(--radius-pill)`
- Padding: 8px 14px
- Font: Cormorant Garamond 14px/400
- Markør: prik (4×4px, circle) eller firkant (6×6px, rotated 45°)

### Skillestreg

Tynd vandret linje til visuelle pauser:

```css
.divider {
  width: 32px;
  height: 0.5px;
  background: var(--accent-line);
  opacity: 0.35;
  margin: 0 auto;
}
```

### Bundnavigation

Fire faner, altid synlige. Hver fane:
- Ikon (16×18px SVG)
- Label i Cormorant 10px med letter-spacing 0.5px
- Aktiv: `var(--text-primary)`, inaktiv: `var(--text-label)`
- Padding: 6px 4px
- Layout: `display: flex; justify-content: space-around`

Fire fane-ikoner (design-forslag, kan forfines):
- **Modellen**: central cirkel + 4 små satellit-cirkler
- **Behandleren**: én cirkel med mindre cirkel i midten (fokus)
- **Rejsen**: bølgelinje der stiger fra venstre til højre
- **Inspiration**: tre overlappende cirkler (Venn-agtigt)
