# Indholds-struktur

Al bogens tekst ligger som markdown-filer i `content/`. Én fil pr. enhed. Hver fil har frontmatter (YAML) med metadata og markdown-krop med selve teksten.

## Mappestruktur

```
content/
├── begreber/              (18 filer — de 18 biodynamiske begreber fra kapitel 3)
│   ├── 01-dynamisk-stilhed.md
│   ├── 02-breath-of-life.md
│   ├── 03-primary-respiration.md
│   ├── 04-midtlinjen.md
│   ├── 05-the-health.md
│   ├── 06-motion-present.md
│   ├── 07-fulcrum.md
│   ├── 08-stillpoints.md
│   ├── 09-transmutation.md
│   ├── 10-the-neutral.md
│   ├── 11-automatic-shifting.md
│   ├── 12-den-iboende-behandlingsplan.md
│   ├── 13-fluid-body.md
│   ├── 14-the-lesion-field.md
│   ├── 15-potency.md
│   ├── 16-ignition.md
│   ├── 17-axial-fluctuations.md
│   └── 18-wholeness.md
│
├── stadier/               (8 filer: 5 stadier + intro + spiral-afsnit + refleksioner fra kapitel 8)
│   ├── 00-behandlerens-indre-rejse.md
│   ├── 01-foerste-stadie.md
│   ├── 02-andet-stadie.md
│   ├── 03-tredje-stadie.md
│   ├── 04-fjerde-stadie.md
│   ├── 05-femte-stadie.md
│   ├── 06-den-levende-spiral.md
│   └── 07-stadier-refleksioner.md
│
└── [Enkeltstående kapitel-filer direkte i content/ root:]
    ├── de-fem-zoner.md                            (type: "zonesamling" — alle 5 zoner i én fil)
    ├── de-otte-essentielle-egenskaber.md          (type: "kvalitetssamling" — alle 8 kvaliteter i én fil)
    ├── de-syv-perspektiver.md                     (kapitel 9)
    ├── de-fire-guidede-oevelser.md                (kapitel 10)
    ├── blechschmidts-principper.md                (kapitel 2)
    ├── typiske-klientmoenstre.md                  (kapitel 7)
    ├── den-biodynamiske-model.md                  (kapitel 1)
    ├── i-behandlingssituationen.md                (kapitel 4)
    ├── andre-traditioner-og-specielle-temaer.md   (kapitel 11)
    ├── integration-i-din-praksis.md               (kapitel 12)
    └── afslutning.md                              (kapitel 13)
```

**Valg:** Kun begreber og stadier fik egne undermapper fordi de består af mange separate enheder (18 og 5). Alle andre kapitler ligger som enkeltstående filer direkte i `content/` root — dette var et bevidst valg for korte kapitler eller samlinger.

## Filnavngivning

- Alle små bogstaver
- Mellemrum bliver bindestreger
- Danske tegn: `æ→ae`, `ø→oe`, `å→aa`
- Nummer først hvis der er en naturlig rækkefølge (fx begrebernes nummer i kapitel 3)

## Frontmatter-format (YAML)

Hver fil starter med frontmatter mellem `---`-linjer. Standardfelter:

```yaml
---
id: "fulcrum"                        # Unik identifier, bruges i relationer.json
type: "begreb"                       # begreb | zone | kvalitet | stadie | perspektiv | oevelse | klientmoenster | princip | essay | tradition | sektion | zonesamling | kvalitetssamling
nummer: 7                            # Nummer i kapitlet (hvis relevant)
gruppe: "behandlings-faenomen"       # principiel | behandlings-faenomen | patologisk (kun for begreber)
titel: "Fulcrum"                     # Vises øverst i Cinzel versaler
undertitel: "det dynamiske omdrejningspunkt"  # Kursiv i Cormorant
hero: "enkelt-kugle"                 # enkelt-kugle | 3-cirkel | 2-cirkel | venn | konstellation | abstrakt
---
```

**Type-specifikke felter:**

For zoner:
```yaml
venstre_titel: "Den medbragte tilstand"
midt_titel: "Væskekroppens vågnende respons"
hoejre_titel: "Åbningen mod det relationelle"
```

For øvelser:
```yaml
varighed_minutter: 20
indtalt_lyd: false  # Kun true hvis lyd eksisterer
```

## Markdown-krop-struktur

Efter frontmatter følger indholdet, organiseret i sektioner med `##`-overskrifter. Hver `##`-sektion bliver et foldbart kort på siden.

```markdown
## Intro

Et omdrejningspunkt, hvorom bevægelse sker. Al bevægelse sker i relation
til et fulcrum — det er en slags bevægelsens midtlinje.

## Det grundlæggende

I den biodynamiske tradition betragtes et fulcrum som både skabende,
orkestrerende og balancerende kroppens bevægelser...

## Sunde fulcrums

Sunde, naturlige fulcrums er bevægelige og dynamiske...

## Dysfunktionelle fulcrums

Dysfunktionelle fulcrums bevæges ikke i relation til helheden...

## Relationer

Se `relationer.json` — ingen prosa her.

## Til refleksion

Hvordan genkender du forskellen mellem sunde bevægelige fulcrums og
rigide dysfunktionelle — de falske omdrejningspunkter kroppen har etableret?

Hvad sker der når et falskt fulcrum opløses?
```

**Særlige sektions-navne der behandles specielt:**

- `## Intro` → Den korte tekst der altid vises (ikke foldbart, står direkte under titlen)
- `## Relationer` → Ikke prosa; indholdet hentes fra `relationer.json` for dette `id`
- `## Til refleksion` → Refleksionsspørgsmål, rendres i kursiv

Alle andre `##`-sektioner bliver foldbare kort med sektionens navn som overskrift.

## Relationer.json

Krydshenvisninger mellem enheder. Ét objekt pr. enhed med dens `id` som nøgle:

```json
{
  "fulcrum": {
    "haenger_sammen_med": [
      { "id": "midtlinjen", "type": "begreb" },
      { "id": "stillpoints", "type": "begreb" },
      { "id": "motion-present", "type": "begreb" },
      { "id": "lesion-field", "type": "begreb" }
    ],
    "lever_ogsaa_i": [
      { "id": "a-fysisk-krop", "type": "zone", "kort_beskrivelse": "Midtlinjen som naturligt fulcrum" },
      { "id": "b-vaeskekrop", "type": "zone", "kort_beskrivelse": "Oprindelig midtlinje som stabilt fulcrum" },
      { "id": "kroppens-dynamiske-landskaber", "type": "oevelse", "kort_beskrivelse": "Øvelse om fulcrums og stillpoints" }
    ]
  },
  "stillpoints": { ... }
}
```

**Regler:**
- `haenger_sammen_med` = andre enheder af **samme type** (fx andre begreber for et begreb)
- `lever_ogsaa_i` = enheder af **anden type** hvor denne enhed spiller en rolle
- Alle referencer går begge veje — hvis A peger på B, skal B pege på A
- Relationer bygges ud fra bogens egne krydshenvisninger (ikke opfundet)

## Hvordan appen loader indhold

1. Ved opstart: appen loader `relationer.json` (én fil, hurtigt)
2. Ved naviagtion til en side: appen loader den pågældende markdown-fil
3. Parser frontmatter → metadata til layout
4. Parser markdown-krop → foldbare kort
5. Relationer-kortet renderes fra `relationer.json`

Ingen server, ingen build-step. Markdown parses klient-side (fx med `marked.js` eller lignende lille library).

## Service worker-caching

Alle markdown-filer og `relationer.json` caches af service workeren ved første besøg. Derefter fungerer appen offline. Når en ny version deployes (nyt indhold eller ændringer), opdateres cachen automatisk via service worker.

## Opdatering af indhold

Når Niklas opdaterer bogen eller tilføjer noget:
1. Redigér den relevante markdown-fil
2. Commit og push til GitHub
3. GitHub Pages deployer automatisk
4. Brugere får opdateringen næste gang de åbner appen

Ingen database, ingen admin-panel — markdown-filerne ER indholdet.
