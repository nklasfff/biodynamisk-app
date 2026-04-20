# Den Biodynamiske App

PWA til behandlere der arbejder med kraniosakral terapi. Baseret på bogen "Den Biodynamiske Model" (~36.000 ord, 13 kapitler). Appen er opslagsværk og udforskningsrum — ikke bog-i-app-format.

## Stack

- Vanilla HTML/CSS/JavaScript (ingen framework, ingen build-step)
- PWA med service worker (offline-support)
- Markdown-baseret indhold (loades dynamisk via `fetch()`)
- YAML-frontmatter parses manuelt (simpel parser, ingen ekstern dependency)
- Markdown parses med `marked.js` loaded fra CDN én gang — cachet af service workeren
- Deploys til GitHub Pages

## Projektstruktur

- `FUNDAMENT.md` — Filosofisk forståelse og design-rationale. Læs først.
- `docs/design-system.md` — CSS-variabler, typografi, komponent-specifikationer
- `docs/side-typer.md` — Layout for hver sidetype (begreb, zone, kvalitet, osv.)
- `docs/hero-illustrationer.md` — SVG-specifikation for sfæriske kugler med pulseren
- `docs/indholds-struktur.md` — Hvordan `content/` er organiseret + frontmatter-format + relationer.json-format
- `docs/relationer-raatabel.md` — Arbejdsdokumentation: kapitel-for-kapitel begrundelse for hver relation i relationer.json, med citat-parafrase fra bogen
- `content/` — Al bogens tekst som markdown-filer (én fil pr. enhed)
- `relationer.json` — Krydshenvisninger mellem enheder (struktureret data). Appens runtime-datakilde
- `tools/byg_relationer.py` — Udviklerscript der bygger og validerer `relationer.json`. Ikke del af appen; køres manuelt når relationer skal tilføjes eller ændres
- `hero_dbm.png` — Havbilledet, bruges som hero på hjemmeskærmen
- `.nojekyll` — Tom fil i roden; kræves af GitHub Pages for at serve filer/mapper normalt

## Principper

- **Content-first:** Indholdet er primært, designet støtter. Al bogens tekst skal med — ikke kondenseret.
- **Progressive disclosure:** Foldbare kort så lange tekster ikke overvælder. Samme mønster på alle sider.
- **Mobil-først:** Optimeret til smartphone. Tap-targets min. 44×44 px.
- **Luft og ro:** Generøs whitespace. Appen må ikke føles presset.
- **Ingen tredjepartsafhængigheder i runtime:** Kun Google Fonts (Cinzel + Cormorant Garamond) og `marked.js` fra CDN. Ingen npm, ingen bundler.

## Arbejdsmetode

Når du bygger en ny funktion eller sidetype:
1. Læs `FUNDAMENT.md` hvis du ikke har kontekst på projektet.
2. Læs den relevante dok-fil i `docs/` (fx `side-typer.md` for en ny side).
3. Konsulter `content/` for indholdets struktur.
4. Byg komponenter så genbrugelige som muligt.

## Vigtige beslutninger der er taget

- To skrifter, ingen tredje: Cinzel (versaler, overskrifter) + Cormorant Garamond (brødtekst). Se `docs/design-system.md`.
- Hero-illustrationer er SVG-komponenter med radial gradient, soft glow, subtil pulseren (6 sek cyklus). Se `docs/hero-illustrationer.md`.
- Fire hovedsektioner: Modellen, Behandleren, Rejsen, Inspiration. Hjemmeskærm er udgangspunkt, ikke en fane.
- Navigation: bundnavigation (4 faner) + hjemmeskærm + relationer (springveje).

## Commands

- `python3 -m http.server 8000` (kør i projektets rod) — nødvendig for udvikling. **Åbn ikke `index.html` direkte med dobbeltklik** — `fetch()` blokeres af browserens CORS ved `file://`, og intet indhold vil loade.
- Ingen build-step. Filerne serveres direkte både lokalt og af GitHub Pages.

## Git-konventioner

- Commit-beskeder skal være korte, præcise og på dansk
- **ALDRIG** brug Claude Code-signaturer ("Generated with Claude Code" eller "Co-Authored-By: Claude") medmindre eksplicit bedt om det
- Dette er Niklas' projekt — commits skal afspejle det
- Brug standard git-workflow: stage → commit → push (når relevant)

## Hvad du ikke skal gøre

- Ikke introducér frameworks (React, Vue, Svelte osv.) uden eksplicit aftale
- Ikke introducér en tredje skrifttype
- Ikke lav "smart" AI-baseret søgning — simpel tekstsøgning er nok
- Ikke hardcode indhold i komponenter — alt kommer fra `content/` og `relationer.json`
- Ikke opfinde relationer — `relationer.json` skal bygges ud fra bogens egne krydshenvisninger (se `docs/indholds-struktur.md`)
- Ikke introducér en build-step, bundler eller npm-dependencies

## Relationer.json — status

Filen indeholder 40 entries: 18 begreber, 5 zoner, 8 kvaliteter, 5 stadier og 4 øvelser (øvelser er kun skaller indtil øvelses-kapitlet får egne relationer). Dækker Part I, II og III's kernestruktur. Ikke med endnu: de 7 perspektiver (kap 9), 9 klientmønstre (kap 7), 9 Blechschmidt-principper (kap 2), 5 intro-essays (kap 1), traditioner og specielle temaer (kap 11), integration (kap 12), afslutning (kap 13). Tilføjes gradvist ved at udvide `tools/byg_relationer.py` og køre scriptet igen.

Regler (fra `docs/indholds-struktur.md`):
- `haenger_sammen_med` = samme type (begreb → begreb, zone → zone)
- `lever_ogsaa_i` = anden type (begreb → zone, øvelse → begreb)
- Alle referencer går begge veje — scriptet validerer automatisk
- Kun relationer der faktisk står i bogen. Baggrund for hver relation er dokumenteret i `docs/relationer-raatabel.md`
