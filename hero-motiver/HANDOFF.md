# HANDOFF — Nyt hero-system

## Mål

Erstatte alle hero-kugler i appen med et nyt visuelt system hvor hver side har sit eget unikke, abstrakte motiv der ånder langsomt. Samme grundkomposition overalt, unikt motiv pr. begreb.

## Hvad der er

Seks eksempel-SVG'er ligger i `hero-motiver/`:

- `01-dynamisk-stilhed.svg`
- `02-breath-of-life.svg`
- `03-primary-respiration.svg`
- `04-midtlinjen.svg`
- `06-motion-present.svg`
- `17-axial-fluctuations.svg`

De viser:
- Den fælles grundkomposition (mørk baggrund, central kerne med varm-hvid radial gradient, aura omkring)
- Hvordan motiverne lever som lag mellem aura og kerne
- Tekst-blok nederst (skillestreg + Cinzel-titel + Cormorant-undertitel)
- Åndedræts-animationen: alle cirkler ændrer radius på stedet, aldrig sideværts bevægelse, 8-sekunders synkron rytme

SVG'erne er vist og godkendt i dark mode. Lys version skal afledes fra samme struktur (andre farver — ses i filernes CSS-variabler `--motif-fill` og `--motif-stroke`).

## Opgave

Undersøg hvordan hero aktuelt er bygget i appen (begreb.html, kapitel.html, stadie.html, zone.html, oversigtssider). Se især hvordan kuglerne er lavet nu og hvordan dark/light toggle virker.

Foreslå en plan for hvordan det nye system integreres: én genbrugelig komponent, motiv pr. begreb som separate filer, fald-tilbage hvis motiv mangler.

**Vent på godkendelse før du skriver kode.**

## Næste skridt efter plan er godkendt

1. Ryd op: fjern de nuværende hero-kugler
2. Byg komponenten + grundkomposition
3. Integrér Dynamisk Stilhed-motivet som første test
4. Derefter de øvrige fem motiver, én ad gangen

De sidste 12 motiver (de mangler stadig: the-health, fulcrum, stillpoints, transmutation, the-neutral, automatic-shifting, den-iboende-behandlingsplan, fluid-body, the-lesion-field, potency, ignition, wholeness) bliver designet senere og tilføjet på samme måde.

## Vigtigt

- Ingen dikteret mappestruktur fra mig — du vurderer hvad der passer til projektet
- Brug plan mode før du skriver kode
- Commit på dansk, ingen Claude Code-signatur (jf. STATUS.md)
- Behold eksisterende funktionalitet: navigation, foldbare kort, relationer
