# Sidetyper

Appen har et begrænset antal sidetyper. Hver sidetype har ét fast layout som genbruges. Dette holder kodebasen enkel og brugerens navigation forudsigelig.

## Niveau 1 — Oversigtssider

Høj-niveau indgange. Brugeren ser hvad en sektion indeholder og vælger hvor hun vil hen.

### Hjemmeskærm

Appens startpunkt. Ankomstrum.

```
┌─────────────────────────────────────┐
│  [hero-billedet: havet]             │
│                                     │
│  Kort invitation i Cormorant        │
│                                     │
│  ─────                              │
│                                     │
│  ○ Modellen                         │
│  ○ Behandleren                      │
│  ○ Rejsen                           │
│  ○ Inspiration                      │
│                                     │
└─────────────────────────────────────┘
```

- Hero-billedet (havbilledet eller abstrakt motiv — ikke fastlagt)
- Kort invitations-tekst (1-3 linjer, Cormorant 17px)
- Fire indgange, hver som et klikbart område med titel og kort beskrivelse
- Ingen bundnavigation her (hjemmeskærmen er udgangspunkt, ikke destination)

### Sektionsoversigt (fx "Modellen")

Når man trykker på en af de fire indgange, lander man her.

```
┌─────────────────────────────────────┐
│ ‹ Hjem              [label top]     │
│                                     │
│ [hero-illustration]                 │
│                                     │
│ MODELLEN                            │
│ modellens ontologi                  │
│ ─────                               │
│                                     │
│ Kort intro-tekst om sektionen       │
│                                     │
│ ○ De grundlæggende principper       │
│ ○ Blechschmidts embryologi          │
│ ○ De 18 begreber                    │
│ ○ I behandlingssituationen          │
│                                     │
│ [bundnavigation]                    │
└─────────────────────────────────────┘
```

- Tilbage-knap øverst til venstre
- Hero-illustration (konstellation eller abstrakt — passende til sektionen)
- Sektionstitel i Cinzel
- Kort intro-undertitel kursiv
- Skillestreg
- Intro-tekst (1-2 paragraffer, Cormorant)
- Liste af underkategorier, hver som et stort kort-lignende element
- Bundnavigation i bunden

### Gruppeoversigt (fx "De 18 begreber")

Underkategori-visning. Her er de 18 begreber inddelt i de tre naturlige grupper.

```
┌─────────────────────────────────────┐
│ ‹ Modellen          [label top]     │
│                                     │
│ DE 18 BEGREBER                      │
│ modellens grundord                  │
│ ─────                               │
│                                     │
│ PRINCIPIELLE · 9                    │
│   1. Dynamisk Stilhed               │
│   2. Breath of Life                 │
│   3. Primary Respiration            │
│   ...                               │
│                                     │
│ BEHANDLINGS-FÆNOMENER · 8           │
│   10. The Neutral                   │
│   11. Motion Present                │
│   ...                               │
│                                     │
│ PATOLOGISK · 1                      │
│   18. The Lesion Field              │
│                                     │
│ [bundnavigation]                    │
└─────────────────────────────────────┘
```

- Gruppe-label i Cinzel som visuel inddeler
- Hver enhed er klikbar (leder til Niveau 2-side)
- Nummereret liste
- Ingen hero-illustration her (listen er det primære)

## Niveau 2 — Enhedssider

Én enhed (begreb, zone, kvalitet osv.) som sit eget rum. Dette er appens hovedskærm — her sker læsningen.

### Begrebsside (gælder alle 18 begreber)

```
┌─────────────────────────────────────┐
│ ‹ Modellen         DE 18 BEGREBER  │
│                                     │
│ BEHANDLINGS-FÆNOMEN · 7             │
│                                     │
│ [sfærisk kugle-illustration]        │
│                                     │
│ FULCRUM                             │
│ det dynamiske omdrejningspunkt      │
│ ─────                               │
│                                     │
│ Et omdrejningspunkt, hvorom         │
│ bevægelse sker. Al bevægelse sker   │
│ i relation til et fulcrum...        │
│                                     │
│ ▎ Det grundlæggende              ▾ │
│ ▎ Sunde fulcrums                 ▾ │
│ ▎ Dysfunktionelle fulcrums       ▾ │
│ ▎ Relationer                     ▾ │
│ ▎ Til refleksion                 ▾ │
│                                     │
│ [bundnavigation]                    │
└─────────────────────────────────────┘
```

**Struktur:**
1. Tilbage-knap + lille label
2. Kategori-label (Cinzel, 10-11px)
3. Hero-illustration (sfærisk kugle, se `hero-illustrationer.md`)
4. Hovedtitel i versaler (Cinzel 32px)
5. Undertitel kursiv (Cormorant italic 16px)
6. Skillestreg
7. Kort intro-tekst (altid synlig, Cormorant 17px)
8. Foldbare kort (3-6 stk, variabelt pr. begreb)

**Hvilke kort vises?** Afgjort af begrebets markdown-fil. Alle begreber har mindst "Det grundlæggende" og "Relationer". Andre kort er begrebs-specifikke.

### Zone-side (gælder alle 5 zoner)

Zoner har 3-cirkel-struktur fra bogen: venstre (medbragt tilstand) + midt (zonens essens) + højre (åbning opad).

```
┌─────────────────────────────────────┐
│ ‹ Behandleren      DE 5 RUM      │
│                                     │
│ RUM B · 2                          │
│                                     │
│ [3-cirkel hero illustration]        │
│   ○       ●       ○                 │
│                                     │
│ VÆSKEKROPPEN                        │
│ broen mellem energi og form         │
│ ─────                               │
│                                     │
│ Intro-tekst om zonen                │
│                                     │
│ ▎ Den medbragte tilstand         ▾ │
│ ▎ Væskekroppens vågnende respons ▾ │
│ ▎ Åbningen mod det relationelle  ▾ │
│ ▎ Begreber der bor her           ▾ │
│ ▎ Til refleksion                 ▾ │
│                                     │
│ [bundnavigation]                    │
└─────────────────────────────────────┘
```

Samme grundstruktur som begrebssiden, men hero er 3-cirkel. De tre foldbare kort efter hero følger bogens tre-cirkel-struktur.

### Kvalitetsside (8 kvaliteter)

Samme grundstruktur som begrebssiden. Hero er enkelt-kugle. Kort:
- Det grundlæggende
- Uddybning (bogens udvidelse af kvaliteten)
- Relationer til andre kvaliteter
- Til refleksion

### Stadieside (5 stadier), Perspektivside (7 perspektiver), Klientmønsterside (9 mønstre), Øvelsesside (4 øvelser), Princip-side (9 Blechschmidt), Essay-side (5 intro-essays), Tradition-side

Alle følger begrebsside-mønstret. Hero og kort tilpasses efter indholdet i den pågældende markdown-fil.

### Øvelsesside — særlige aspekter

Guidede øvelser har en lidt anden karakter. Skal designes så brugeren kan læse den fulde tekst i ét flow, eller klikke sig gennem sektionerne. Overvej:
- Fuld-tekst-visning som default (ikke kun foldbare kort)
- Evt. lyd-afspilning hvis Niklas indtaler (ikke fastlagt)
- Timer-indikator for øvelsens længde

## Universelle elementer på alle Niveau 2-sider

- **Top-navigation:** Tilbage-knap + kategori-label i Cinzel
- **Bundnavigation:** De fire faner (Modellen, Behandleren, Rejsen, Inspiration)
- **Aktiv fane fremhæves** i bundnavigationen afhængigt af hvor man er
- **Tilbage-knap** går altid ét niveau op (Niveau 2 → Niveau 1)

## Niveau 3 — Indhold i foldet kort

Ikke en separat side, men indholdet der foldes ud inde i et kort på en Niveau 2-side. Se `design-system.md` for kort-specifikationen.

**Hvad kan ligge i et foldet kort:**
- Prosa-tekst (Cormorant 16px, line-height 1.75)
- Pills med relationer (til andre enheder)
- Kursive citater eller refleksionsspørgsmål (Cormorant italic)
- Aldrig nested foldbare kort (hvis noget er kompliceret nok til det, skal det være sin egen side)

## Søgning

Simpel tekstsøgning over alle markdown-filer. Input i toppen af en særlig søge-side eller som overlay.

- Søger i titler, undertitler, og brødtekst
- Resultater grupperes efter type (begreber, zoner, osv.)
- Klik → Niveau 2-side
- Ingen AI-baseret semantisk søgning i første version
