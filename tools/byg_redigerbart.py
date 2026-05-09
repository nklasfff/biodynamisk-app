#!/usr/bin/env python3
"""
byg_redigerbart.py — Generér ét samlet redigerbart Word-udkast med ALT
indhold fra bogen i klartekst-format. Round-trip: brugeren redigerer
direkte i Word, sender filen retur, og ændringer kan applikeres tilbage
til kildematerialet (content/*.md, hero-motiver/*.svg, mikrotekster.json,
byg_bog.py-konstanter).

Output:
  tools/output/manuskript-redigerbar.docx

Brug:
  python3 tools/byg_redigerbart.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from byg_bog import (
    ROOT, CONTENT, OUT,
    DELE,
    PERSPEKTIVER_FIGURER, EGENSKABER_FIGURER,
    RUM_HERO_FIGURER, HELHED_HERO_FIGURER, OEVELSE_HERO_FIGURER,
    EGENSKAB_SUBTITLES, SPECIELLE_TEMAER_SUBTITLES,
    KATEGORI_ORDEN,
    hent_mikrotekster, laes_md, strip_relationer, strip_html_illustrations,
    _kapitel_kategori_indeks, _vaelg_invitation_for_kapitel,
)


# ============================================================================
# ILLUSTRATIONS-INVENTAR
# ============================================================================
#
# For hver hero-illustration: en strukturet beskrivelse af tekstindholdet
# brugeren kan redigere. Bygges op manuelt for de største illustrationer
# (kapitel-heroes), genereres fra Python-konstanter for serierne.
# ============================================================================

# Kapitel-hero-illustrationers tekstindhold (manuelt opretholdt for at
# bevare kontekst og position).
KAPITEL_HERO_TEKSTER = {
    "den-biodynamiske-model-figur.svg": [
        ("Type", "5 koncentriske ovaler omkring en mørk kerne"),
        ("Ydre oval (lysest)", "De Embryologiske Kræfter / iboende intelligens fra foster til heling"),
        ("Næstydre oval", "Kroppen som Ubrudt Helhed / et integreret kontinuum fra første celle"),
        ("Midt", "Den Kontinuerlige Tilblivelse / uafbrudt flyden-til — aldrig statisk"),
        ("Næstinder", "Enhedens Paradoks / The Neutral — fri til alle retninger"),
        ("Inder", "Felters Dynamik og Grænser / grænseflader som indgange til nyt"),
        ("Center (mørkest)", "DEN BIODYNAMISKE MODEL / når livets kræfter mødes"),
    ],
    "embryologi-figur.svg": [
        ("Type", "Konstellation: 8 cirkler omkring centrum 'Embryologi'"),
        ("Center", "Embryologi"),
        ("Cirkel 1", "Bevægelse / skaber form"),
        ("Cirkel 2", "Væske- / dynamik"),
        ("Cirkel 3", "Metaboliske / felter"),
        ("Cirkel 4", "Ekstragenetisk / information"),
        ("Cirkel 5", "Selvreferentiel / kapacitet"),
        ("Cirkel 6", "Cellen som / bevægelse"),
        ("Cirkel 7", "Periferi / til centrum"),
        ("Cirkel 8", "Rytmer af / aktivitet og hvile"),
        ("Cirkel 9", "Kræfter / livet igennem"),
    ],
    "begreber-figur.svg": [
        ("Type", "Konstellation: 18 cirkler — én pr. begreb"),
        ("Note", "Hvert begrebs-glyf har sin egen titel + tagline; redigeres pr. glyf nedenfor"),
    ],
    "i-behandlingssituationen-figur.svg": [
        ("Type", "Klient-rejse / behandlerens proces"),
        ("Note", "Tekster på figur ekstraheres direkte fra SVG — se 'auto-ekstraherede'"),
    ],
    "helheden-under-pres-figur.svg": [
        ("Type", "Fire forskydnings-stadier"),
        ("Stadie 1", "Helheden lever"),
        ("Stadie 2", "Første forskydning"),
        ("Stadie 3", "Ubalancen breder sig"),
        ("Stadie 4", "Det kroniske mønster"),
    ],
    "ordliste-figur.svg": [
        ("Type", "Konstellation: 7 kategorier omkring 'Vendinger & Betydninger'"),
        ("Center", "Vendinger & Betydninger"),
        ("Top", "De 18 / Biodynamiske / Begreber"),
        ("Top-højre", "Termer fra / Andre / Traditioner"),
        ("Højre", "Embryologiske / Termer"),
        ("Bund-højre", "Nervesystem / og Regulering"),
        ("Bund-venstre", "Rytmer og / Bevægelser"),
        ("Venstre", "Terapeutiske / Processer"),
        ("Top-venstre", "Behandlings- / termer"),
    ],
    "otte-egenskaber-figur.svg": [
        ("Type", "Konstellation: 8 essentielle egenskaber omkring centrum"),
        ("Note", "Tekster vises i Egenskab-konstellationen nedenfor (PERSPEKTIVER/EGENSKABER auto-genereret)"),
    ],
    "de-fem-rum-figur.svg": [
        ("Type", "Venn diagram med 5 overlappende cirkler"),
        ("Cirkel 1 (top)", "Den fysiske krop / Form bliver til flow"),
        ("Cirkel 2", "Væskekroppen / Flowet forbinder felter"),
        ("Cirkel 3 (bund-højre)", "Det relationelle felt / Mødet med den dybere rytme"),
        ("Cirkel 4 (bund-venstre)", "Primary Respiration / Rytmen hviler i kilden"),
        ("Cirkel 5 (venstre)", "Dynamisk Stilhed / Kilden bliver til form"),
        ("Center", "De 5 Rum"),
    ],
    "klientmoenstre-figur.svg": [
        ("Type", "9 cirkler — én pr. klient-mønster"),
        ("Note", "Tekster ekstraheres fra SVG direkte"),
    ],
    "behandlerens-indre-rejse-figur.svg": [
        ("Type", "Konstellation: 5 stadier omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("Stadie 1", "A.T. / Still"),
        ("Stadie 2", "William G. / Sutherland"),
        ("Stadie 3", "Rollin E. / Becker"),
        ("Stadie 4", "James / Jealous"),
        ("Stadie 5", "Alle / os"),
        ("Note", "Forord-figuren bruger samme layout — se forord-figur.svg"),
    ],
    "de-syv-perspektiver-figur.svg": [
        ("Type", "Konstellation: 7 perspektiver (samme som perspektiv-glyfer)"),
        ("Note", "Tekster genereret fra PERSPEKTIVER_FIGURER — redigér i konstellation nedenfor"),
    ],
    "de-fire-oevelser-figur.svg": [
        ("Type", "Venn med 4 overlappende cirkler"),
        ("Top", "At Opleve The Neutral / Lytten der vækker indre viden"),
        ("Højre", "Kroppens Egen Viden / Indsigt møder åndedrættet"),
        ("Bund", "Vejrtrækningen Som En Levende Proces / Åndedrættet bevæger landskabet"),
        ("Venstre", "Kroppens Dynamiske Landskaber / Bevægelsen finder hvile"),
        ("Center", "De 4 Guidede Øvelser"),
    ],
    "traditioner-figur.svg": [
        ("Type", "Konstellation: traditioner og specielle temaer"),
        ("Note", "Tekster ekstraheres fra SVG direkte"),
    ],
    "integration-figur.svg": [
        ("Type", "Konstellation"),
        ("Note", "Tekster ekstraheres fra SVG direkte"),
    ],
    "afslutning-figur.svg": [
        ("Type", "Konstellation"),
        ("Note", "Tekster ekstraheres fra SVG direkte"),
    ],
    "forord-figur.svg": [
        ("Type", "Konstellation: 5 osteopati-pionerer + 'Alle os' omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("Top", "A.T. / Still"),
        ("Top-højre", "William G. / Sutherland"),
        ("Bund-højre", "Rollin E. / Becker"),
        ("Bund-venstre", "James / Jealous"),
        ("Venstre", "Alle / os"),
    ],
}


# ============================================================================
# HJÆLPERE
# ============================================================================

def parse_sektioner(body: str):
    """Split body på '## Heading' og returnér liste af (heading, content)-pairs."""
    pattern = re.compile(r'^(##+)\s+(.+?)\s*$', re.MULTILINE)
    matches = list(pattern.finditer(body))
    sections = []
    if not matches:
        return [("", body.strip())]
    # Pre-content (før første heading)
    if matches[0].start() > 0:
        pre = body[:matches[0].start()].strip()
        if pre:
            sections.append(("", pre))
    for i, m in enumerate(matches):
        heading = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections.append((heading, content))
    return sections


def parse_refleksioner(body: str):
    """Returnér liste af refleksionsspørgsmål fra et body-stykke.

    Body kan have ### subsektioner med spørgsmål, eller direkte
    paragraffer som spørgsmål. Hver paragraf = ét spørgsmål.
    """
    # Strip eventuelle ### subheadings
    cleaned = re.sub(r'^###+\s+.+$', '', body, flags=re.MULTILINE)
    # Split på blanke linjer
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cleaned) if p.strip()]
    return paragraphs


def extract_svg_texts(svg_path: Path) -> list:
    """Returnér liste af tekstindhold fra alle <text> elementer i en SVG."""
    if not svg_path.exists():
        return []
    text = svg_path.read_text(encoding='utf-8')
    # Match <text ...>content</text> (kan indeholde tspans, men vi henter
    # bare den synlige tekst). Strip eventuelle inner tags.
    matches = re.findall(r'<text[^>]*>(.*?)</text>', text, re.DOTALL)
    cleaned = []
    for m in matches:
        # Fjern inner tags og whitespace
        t = re.sub(r'<[^>]+>', '', m).strip()
        if t:
            cleaned.append(t)
    return cleaned


def md_blockquote(text: str) -> str:
    """Konvertér tekst til et indrykket blockquote (vises som indrykning i Word)."""
    lines = text.split('\n')
    return '\n'.join(f'> {ln}' if ln else '>' for ln in lines)


# ============================================================================
# RENDERING
# ============================================================================

def render_intro_side() -> str:
    return dedent("""
        ---
        title: "Den Biodynamiske Model — Redigerbart Udkast"
        subtitle: "Komplet manuskript til redigering"
        author: "Niklas Patursson"
        lang: da
        toc: true
        toc-depth: 2
        ...

        # Vejledning

        Dette dokument indeholder ALT redigerbart indhold fra bogen i ét samlet
        Word-format: brødtekst, illustrationstekster, refleksionsspørgsmål og
        daglige invitationer.

        **Sådan bruger du dokumentet:**

        1. Redigér frit i Word — alt under en heading kan ændres.
        2. Bevar headings og markører som `[BRØDTEKST: ...]`, `[ILLUSTRATION: ...]`,
           `[REFLEKSIONSSPØRGSMÅL]`, `[DAGLIG INVITATION]` præcis som de står.
        3. Send det redigerede dokument retur når du er færdig.

        **Strukturmarkører:**

        - `[BRØDTEKST: Afsnitsnavn]` — almindelig brødtekst i et afsnit.
        - `[ILLUSTRATION: Beskrivelse]` — tekstindholdet i en illustration,
          listet position-for-position. Redigér tekst men bevar etiketterne
          (Center, Top, etc.) som de står.
        - `[REFLEKSIONSSPØRGSMÅL]` — refleksionsspørgsmål, ét pr. liste-element.
        - `[DAGLIG INVITATION]` — den daglige invitation til kapitlet
          (titel/evokation/invitation).

        Markdown-formatering (kursiv `*tekst*`, fed `**tekst**`) bevares ind
        i Word og tilbage. Lange dashes (—) kan skrives direkte. Citater og
        indrykning bruges minimalt.

        ---
    """).strip() + "\n\n"


def render_part(part_nr: int, titel: str, beskrivelse: str) -> str:
    roman = ['I', 'II', 'III', 'IV'][part_nr - 1]
    return (
        f"\n# Part {roman} — {titel}\n\n"
        f"**[PART-BESKRIVELSE]**\n\n"
        f"{beskrivelse}\n\n"
        "---\n\n"
    )


def render_forord() -> str:
    info_html = (ROOT / "info.html").read_text(encoding='utf-8')
    m = re.search(
        r'<!-- Bag denne app -->.*?<section[^>]*>(.*?)</section>',
        info_html, re.DOTALL,
    )
    forord_text = ""
    if m:
        raw = m.group(1)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', raw, re.DOTALL)
        cleaned = []
        for p in paragraphs:
            clean = re.sub(r'<[^>]+>', '', p).strip()
            if clean:
                cleaned.append(clean)
        forord_text = "\n\n".join(cleaned)

    out = "\n# Forord\n\n"
    out += "**[BRØDTEKST: Forord]**\n\n"
    out += forord_text + "\n\n"
    out += "**[ILLUSTRATION: Forord-konstellation]**\n\n"
    for label, text in KAPITEL_HERO_TEKSTER.get("forord-figur.svg", []):
        out += f"- **{label}:** {text}\n"
    out += "\n---\n\n"
    return out


def render_illustration_block(svg_navn: str, hovedoverskrift: str = None) -> str:
    """Render en illustrations-tekst-blok som markdown."""
    overskrift = hovedoverskrift or svg_navn
    out = f"**[ILLUSTRATION: {overskrift}]**\n\n"

    if svg_navn in KAPITEL_HERO_TEKSTER:
        for label, text in KAPITEL_HERO_TEKSTER[svg_navn]:
            out += f"- **{label}:** {text}\n"
    else:
        # Fallback: ekstraher fra SVG
        svg_path = ROOT / "hero-motiver" / svg_navn
        texts = extract_svg_texts(svg_path)
        if texts:
            out += "*Auto-ekstraherede tekster (i SVG-rækkefølge):*\n\n"
            for i, t in enumerate(texts, 1):
                out += f"- **Tekst {i}:** {t}\n"
        else:
            out += "*(ingen tekst-elementer fundet i SVG)*\n"
    out += "\n"
    return out


def render_perspektiver_konstellation() -> str:
    """De 7 perspektiver — fra PERSPEKTIVER_FIGURER konstanten."""
    out = "**[ILLUSTRATION: De 7 Perspektiver — konstellation]**\n\n"
    out += "*Hvert perspektiv har en fuld titel og to-linjers tekst der vises i cirklen.*\n\n"
    for fuld, l1, l2 in PERSPEKTIVER_FIGURER:
        out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
    out += "\n"
    return out


def render_egenskaber_konstellation() -> str:
    """De 8 egenskaber — fra EGENSKABER_FIGURER konstanten."""
    out = "**[ILLUSTRATION: De 8 Egenskaber — konstellation]**\n\n"
    out += "*Hver egenskab har en fuld titel og to-linjers tekst der vises i cirklen.*\n\n"
    for fuld, l1, l2 in EGENSKABER_FIGURER:
        out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
    out += "\n"
    return out


def render_kapitel_fil(filnavn: str, kapitel_nr: int, undermappe: str = None) -> str:
    """Render én markdown-fil som kapitel."""
    if undermappe:
        path = CONTENT / undermappe / f"{filnavn}.md"
    else:
        path = CONTENT / f"{filnavn}.md"

    if not path.exists():
        return f"\n# Kapitel {kapitel_nr}: {filnavn} (mangler)\n\n"

    fm, body = laes_md(path)
    body = strip_relationer(body)
    body = strip_html_illustrations(body)

    titel = fm.get("titel", filnavn).strip()
    undertitel = fm.get("undertitel", "").strip()

    out = f"\n# Kapitel {kapitel_nr}: {titel}\n\n"
    if undertitel:
        out += f"**[UNDERTITEL]** {undertitel}\n\n"

    sections = parse_sektioner(body)
    for heading, content in sections:
        if not content.strip() and not heading:
            continue
        if heading.lower().startswith("til refleksion"):
            out += "**[REFLEKSIONSSPØRGSMÅL]**\n\n"
            for i, q in enumerate(parse_refleksioner(content), 1):
                out += f"{i}. {q}\n\n"
        elif heading.lower() == "relationer":
            continue
        elif heading:
            out += f"**[BRØDTEKST: {heading}]**\n\n"
            out += content + "\n\n"
        else:
            out += content + "\n\n"

    # Daglig invitation
    inv = _vaelg_invitation_for_kapitel(kapitel_nr)
    if inv:
        out += "**[DAGLIG INVITATION]**\n\n"
        out += f"- **Kategori:** {inv['kategori']}\n"
        out += f"- **Titel:** {inv['navn']}\n"
        out += f"- **Evokation:** {inv['evokation']}\n"
        out += f"- **Invitation:** {inv['invitation']}\n\n"

    out += "---\n\n"
    return out


def render_samling(samling_titel: str, undermappe: str, filnavne: list,
                    kapitel_nr: int) -> str:
    """Render en samling (begreber eller stadier) som ét kapitel."""
    out = f"\n# Kapitel {kapitel_nr}: {samling_titel}\n\n"

    # Special konstellationer for kendte samlinger
    # (begreber-figur og behandlerens-indre-rejse-figur har egne tekster)
    samling_hero = {
        "begreber": "begreber-figur.svg",
        "stadier": "behandlerens-indre-rejse-figur.svg",
    }
    if undermappe in samling_hero:
        out += render_illustration_block(samling_hero[undermappe],
                                          f"Samling-hero — {samling_titel}")

    for filnavn in filnavne:
        path = CONTENT / undermappe / f"{filnavn}.md"
        if not path.exists():
            out += f"\n## {filnavn} (mangler)\n\n"
            continue

        fm, body = laes_md(path)
        body = strip_relationer(body)
        body = strip_html_illustrations(body)

        del_titel = fm.get("titel", filnavn).strip()
        del_undertitel = fm.get("undertitel", "").strip()

        out += f"\n## {del_titel}\n\n"
        if del_undertitel:
            out += f"**[UNDERTITEL]** {del_undertitel}\n\n"

        # Glyf for begreb (hvis det er begreber-samling)
        if undermappe == "begreber":
            glyf_navn = f"glyf-{filnavn}.svg"
            glyf_path = ROOT / "hero-motiver" / glyf_navn
            if glyf_path.exists():
                texts = extract_svg_texts(glyf_path)
                if texts:
                    out += f"**[ILLUSTRATION: Glyf for {del_titel}]**\n\n"
                    for i, t in enumerate(texts, 1):
                        out += f"- **Tekst {i}:** {t}\n"
                    out += "\n"

        # Stadie-figur (hvis det er stadier-samling)
        if undermappe == "stadier":
            stadie_match = re.match(r'^0(\d)-', filnavn)
            if stadie_match:
                stadie_nr = stadie_match.group(1)
                stadie_navn = f"stadie-{stadie_nr}-figur.svg"
                stadie_path = ROOT / "hero-motiver" / stadie_navn
                if stadie_path.exists():
                    texts = extract_svg_texts(stadie_path)
                    if texts:
                        out += f"**[ILLUSTRATION: Stadie-figur — {del_titel}]**\n\n"
                        for i, t in enumerate(texts, 1):
                            out += f"- **Tekst {i}:** {t}\n"
                        out += "\n"

        sections = parse_sektioner(body)
        for heading, content in sections:
            if not content.strip() and not heading:
                continue
            if heading.lower().startswith("til refleksion"):
                out += "**[REFLEKSIONSSPØRGSMÅL]**\n\n"
                for i, q in enumerate(parse_refleksioner(content), 1):
                    out += f"{i}. {q}\n\n"
            elif heading.lower() == "relationer":
                continue
            elif heading:
                out += f"**[BRØDTEKST: {heading}]**\n\n"
                out += content + "\n\n"
            else:
                out += content + "\n\n"

    # Daglig invitation
    inv = _vaelg_invitation_for_kapitel(kapitel_nr)
    if inv:
        out += "**[DAGLIG INVITATION]**\n\n"
        out += f"- **Kategori:** {inv['kategori']}\n"
        out += f"- **Titel:** {inv['navn']}\n"
        out += f"- **Evokation:** {inv['evokation']}\n"
        out += f"- **Invitation:** {inv['invitation']}\n\n"

    out += "---\n\n"
    return out


def render_litteraturliste() -> str:
    """Litteraturliste — bygges fra byg_bog.render_litteraturliste()."""
    from byg_bog import render_litteraturliste as bog_litt
    raw = bog_litt()
    # Justér første heading til level 1
    raw = re.sub(r'^# Litteraturliste', '# Litteraturliste', raw, count=1, flags=re.MULTILINE)
    return "\n" + raw + "\n"


# ============================================================================
# SAMLET MANUSKRIPT
# ============================================================================

def byg_redigerbart_udkast() -> str:
    out = []
    out.append(render_intro_side())
    out.append(render_forord())

    kapitel_nr = 1
    for part_idx, (part_titel, part_beskrivelse, kapitler) in enumerate(DELE):
        out.append(render_part(part_idx + 1, part_titel, part_beskrivelse))
        for spec in kapitler:
            if spec[0] == "fil":
                out.append(render_kapitel_fil(spec[1], kapitel_nr))
            elif spec[0] == "samling":
                _, titel, undermappe, filnavne = spec
                out.append(render_samling(titel, undermappe, filnavne, kapitel_nr))
            kapitel_nr += 1

    # Hovedhero-illustrationer for hvert kapitel som ekstra inventar
    out.append("\n# Bilag — Kapitel-hero-illustrationer\n\n")
    out.append("*Tekstindhold i hver kapitel-hero (samme illustration som vist i selve kapitlet, listet samlet for nem editing).*\n\n")

    KAPITEL_HEROES = {
        1: ("Kapitel 1: Den Biodynamiske Model", "den-biodynamiske-model-figur.svg"),
        2: ("Kapitel 2: Blechschmidts Embryologi", "embryologi-figur.svg"),
        3: ("Kapitel 3: De 18 Begreber (samling-hero)", "begreber-figur.svg"),
        4: ("Kapitel 4: I Behandlingssituationen", "i-behandlingssituationen-figur.svg"),
        5: ("Kapitel 5: Helheden Under Pres", "helheden-under-pres-figur.svg"),
        6: ("Kapitel 6: De 8 Essentielle Egenskaber", "otte-egenskaber-figur.svg"),
        7: ("Kapitel 7: De 5 Rum", "de-fem-rum-figur.svg"),
        8: ("Kapitel 8: Typiske Klientmønstre", "klientmoenstre-figur.svg"),
        9: ("Kapitel 9: De Fem Stadier (samling-hero)", "behandlerens-indre-rejse-figur.svg"),
        10: ("Kapitel 10: De 7 Perspektiver", "de-syv-perspektiver-figur.svg"),
        11: ("Kapitel 11: De 4 Guidede Øvelser", "de-fire-oevelser-figur.svg"),
        12: ("Kapitel 12: Andre Traditioner", "traditioner-figur.svg"),
        13: ("Kapitel 13: Integration", "integration-figur.svg"),
        14: ("Kapitel 14: Rejsen Ud & Hjem", "afslutning-figur.svg"),
        15: ("Kapitel 15: Ordliste", "ordliste-figur.svg"),
    }
    for nr, (label, svg) in KAPITEL_HEROES.items():
        out.append(f"## {label}\n\n")
        out.append(render_illustration_block(svg, label))

    # De 7 perspektiver og de 8 egenskaber konstellationer
    out.append("\n# Bilag — Perspektiv- og Egenskabs-konstellationer\n\n")
    out.append("*Hver perspektiv- og egenskab-figur har en fuld titel + to-linjers cirkeltekst. Listet samlet for nem editing.*\n\n")
    out.append("## De 7 Perspektiver\n\n")
    out.append(render_perspektiver_konstellation())
    out.append("## De 8 Essentielle Egenskaber\n\n")
    out.append(render_egenskaber_konstellation())

    # Underoverskrifter (egenskab + specielle temaer)
    out.append("\n# Bilag — Underoverskrifter (8 egenskaber + Specielle Temaer)\n\n")
    out.append("*Korte taglines under hver overskrift. Disse er manuelt tilføjet i bog-output (ikke i kildemarkdown).*\n\n")
    out.append("## 8 Essentielle Egenskaber — undertitler\n\n")
    for titel, sub in EGENSKAB_SUBTITLES.items():
        out.append(f"- **{titel}** → {sub}\n")
    out.append("\n## Specielle Temaer — undertitler\n\n")
    for titel, sub in SPECIELLE_TEMAER_SUBTITLES.items():
        out.append(f"- **{titel}** → {sub}\n")
    out.append("\n")

    # Alle 120 daglige invitationer
    out.append("\n# Bilag — Alle 120 Daglige Invitationer (kildedata)\n\n")
    out.append("*Kun 15 invitationer bruges i bogen (én pr. kapitel). Resten kan vælges fra her — eller bruges fremtidigt. Hver kategori har 20 invitationer.*\n\n")
    teksters = hent_mikrotekster()
    grupper = {}
    rækkefølge = []
    for t in teksters:
        cat = t.get("kategori", "andet")
        if cat not in grupper:
            rækkefølge.append(cat)
            grupper[cat] = []
        grupper[cat].append(t)

    KATEGORI_NAVNE = {
        "princip": "DE 10 BIODYNAMISKE PRINCIPPER",
        "blechschmidt": "BLECHSCHMIDT-PRINCIPPER",
        "perspektiv": "DE 7 PERSPEKTIVER",
        "egenskab": "DE 8 ESSENTIELLE EGENSKABER",
        "zone": "DE 5 RUM",
        "stadie": "DE 5 STADIER",
    }
    for cat in rækkefølge:
        out.append(f"## {KATEGORI_NAVNE.get(cat, cat).title()}\n\n")
        for t in grupper[cat]:
            out.append(f"### {t['navn']}\n\n")
            out.append(f"- **Titel:** {t['navn']}\n")
            out.append(f"- **Evokation:** {t['evokation']}\n")
            out.append(f"- **Invitation:** {t['invitation']}\n\n")

    out.append(render_litteraturliste())

    return "\n".join(out)


# ============================================================================
# PANDOC
# ============================================================================

def kor_pandoc(md_path: Path, out_path: Path) -> bool:
    cmd = ["pandoc", str(md_path), "-o", str(out_path),
           "--toc", "--toc-depth=2"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"PANDOC FEJL:", r.stderr[-2000:], file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("PANDOC TIMEOUT", file=sys.stderr)
        return False


def main():
    print("Bygger redigerbart udkast …")
    md = byg_redigerbart_udkast()

    md_path = OUT / "manuskript-redigerbar.md"
    md_path.write_text(md, encoding='utf-8')
    print(f"  ✓ {md_path} ({len(md):,} tegn)")

    docx_path = OUT / "manuskript-redigerbar.docx"
    if kor_pandoc(md_path, docx_path):
        print(f"  ✓ {docx_path}")
    else:
        print("  × DOCX fejlede", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
