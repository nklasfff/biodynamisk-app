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
    DELE, CHAPTER_HERO, SAMLING_HERO, SUBSECTION_HERO,
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
# brugeren kan redigere. Ekstraheres delvist fra Python-konstanter,
# delvist fra SVG'erne.
# ============================================================================

# Manuelt opretholdt kontekst-information for de største illustrationer
# (positions-labels for koncentriske/venn/konstellations-layouts).
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
        ("Type", "Konstellation: 9 cirkler omkring centrum"),
        ("Center", "Embryologi"),
        ("Bevægelse", "Bevægelse / skaber form"),
        ("Væskedynamik", "Væske- / dynamik"),
        ("Metaboliske felter", "Metaboliske / felter"),
        ("Ekstragenetisk", "Ekstragenetisk / information"),
        ("Selvreferentiel", "Selvreferentiel / kapacitet"),
        ("Cellen", "Cellen som / bevægelse"),
        ("Periferi", "Periferi / til centrum"),
        ("Rytmer", "Rytmer af / aktivitet og hvile"),
        ("Kræfter", "Kræfter / livet igennem"),
    ],
    "begreber-figur.svg": [
        ("Type", "Konstellation: 18 cirkler — én pr. begreb"),
        ("Note", "Hvert begrebs-glyf har egen titel + tagline; redigeres pr. begreb under selve begreb-afsnittet."),
    ],
    "i-behandlingssituationen-figur.svg": [
        ("Type", "Behandlerens proces / klient-rejse"),
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
        ("Note", "Hver egenskab har titel + 2-linjers cirkel-tekst — listet pr. egenskab nedenfor (kapitel 6)."),
    ],
    "de-fem-rum-figur.svg": [
        ("Type", "Venn diagram med 5 overlappende cirkler"),
        ("Cirkel 1 (top)", "Den fysiske krop / Form bliver til flow"),
        ("Cirkel 2 (top-højre)", "Væskekroppen / Flowet forbinder felter"),
        ("Cirkel 3 (bund-højre)", "Det relationelle felt / Mødet med den dybere rytme"),
        ("Cirkel 4 (bund-venstre)", "Primary Respiration / Rytmen hviler i kilden"),
        ("Cirkel 5 (venstre)", "Dynamisk Stilhed / Kilden bliver til form"),
        ("Center", "De 5 Rum"),
    ],
    "klientmoenstre-figur.svg": [
        ("Type", "9 cirkler — én pr. klient-mønster"),
    ],
    "behandlerens-indre-rejse-figur.svg": [
        ("Type", "Konstellation: 5 stadier omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("A.T. Still", "A.T. / Still"),
        ("William G. Sutherland", "William G. / Sutherland"),
        ("Rollin E. Becker", "Rollin E. / Becker"),
        ("James Jealous", "James / Jealous"),
        ("Alle os", "Alle / os"),
    ],
    "de-syv-perspektiver-figur.svg": [
        ("Type", "Konstellation: 7 perspektiver"),
        ("Note", "Hvert perspektiv har titel + 2-linjers cirkeltekst — listet pr. perspektiv nedenfor (kapitel 10)."),
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
    ],
    "integration-figur.svg": [
        ("Type", "Konstellation: integrations-temaer"),
    ],
    "afslutning-figur.svg": [
        ("Type", "Konstellation"),
    ],
    "forord-figur.svg": [
        ("Type", "Konstellation: 5 osteopati-pionerer + 'Alle os' omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("A.T. Still", "A.T. / Still"),
        ("William G. Sutherland", "William G. / Sutherland"),
        ("Rollin E. Becker", "Rollin E. / Becker"),
        ("James Jealous", "James / Jealous"),
        ("Alle os", "Alle / os"),
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
    """Returnér liste af refleksionsspørgsmål fra et body-stykke."""
    cleaned = re.sub(r'^###+\s+.+$', '', body, flags=re.MULTILINE)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cleaned) if p.strip()]
    return paragraphs


def extract_svg_texts(svg_path: Path) -> list:
    """Returnér liste af tekstindhold fra alle <text> elementer i en SVG."""
    if not svg_path.exists():
        return []
    text = svg_path.read_text(encoding='utf-8')
    matches = re.findall(r'<text[^>]*>(.*?)</text>', text, re.DOTALL)
    cleaned = []
    for m in matches:
        t = re.sub(r'<[^>]+>', '', m).strip()
        if t:
            cleaned.append(t)
    return cleaned


def render_illustration(svg_navn: str, label: str = None) -> str:
    """Render en illustrations-tekst-blok som markdown."""
    overskrift = label or svg_navn
    out = f"**[ILLUSTRATION: {overskrift}]**\n\n"

    if svg_navn in KAPITEL_HERO_TEKSTER:
        for k, v in KAPITEL_HERO_TEKSTER[svg_navn]:
            out += f"- **{k}:** {v}\n"
    else:
        # Fallback: ekstraher fra SVG
        svg_path = ROOT / "hero-motiver" / svg_navn
        texts = extract_svg_texts(svg_path)
        if texts:
            out += "*Tekster ekstraheret fra SVG (i SVG-rækkefølge):*\n\n"
            for i, t in enumerate(texts, 1):
                out += f"- **Tekst {i}:** {t}\n"
        else:
            out += "*(ingen tekst-elementer fundet)*\n"
    out += "\n"
    return out


def render_glyf_for_begreb(filnavn: str, del_titel: str) -> str:
    """For begreb: returner glyfens tekstindhold."""
    glyf_navn = SUBSECTION_HERO.get(filnavn)
    if not glyf_navn:
        return ""
    glyf_path = ROOT / "hero-motiver" / glyf_navn
    texts = extract_svg_texts(glyf_path)
    if not texts:
        return ""
    out = f"**[ILLUSTRATION: Glyf — {del_titel}]**\n\n"
    for i, t in enumerate(texts, 1):
        out += f"- **Tekst {i}:** {t}\n"
    out += "\n"
    return out


def render_stadie_figur(filnavn: str, del_titel: str) -> str:
    """For stadie: returner stadie-figurens tekstindhold."""
    sub_navn = SUBSECTION_HERO.get(filnavn)
    if not sub_navn:
        return ""
    sub_path = ROOT / "hero-motiver" / sub_navn
    texts = extract_svg_texts(sub_path)
    if not texts:
        return ""
    out = f"**[ILLUSTRATION: Stadie-figur — {del_titel}]**\n\n"
    for i, t in enumerate(texts, 1):
        out += f"- **Tekst {i}:** {t}\n"
    out += "\n"
    return out


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
        2. Bevar markørerne `[BRØDTEKST: ...]`, `[ILLUSTRATION: ...]`,
           `[REFLEKSIONSSPØRGSMÅL]`, `[DAGLIG INVITATION]`, `[UNDERTITEL]`,
           `[PART-BESKRIVELSE]` præcis som de står — de bruges til round-trip.
        3. Bevar etiketterne i illustrations-listerne ("Center", "Top", etc.)
           som de står; redigér kun selve teksten efter kolon.
        4. Send det redigerede dokument retur når du er færdig.

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
    """Forord — bruger den redigerede bog-version (ikke app's info.html)."""
    from byg_bog import render_forord as bog_forord
    raw = bog_forord()
    # Fjern hero-illustration fra bog-rendering (vi har vores eget)
    raw = re.sub(r'```\{=latex\}.*?```\n?', '', raw, flags=re.DOTALL)
    raw = raw.replace("# Forord", "").strip()

    out = "\n# Forord\n\n"
    out += render_illustration("forord-figur.svg", "Forord-konstellation")
    out += "**[BRØDTEKST: Forord]**\n\n"
    out += raw + "\n\n"
    out += "---\n\n"
    return out


def render_kapitel_body_sektioner(body: str) -> str:
    """Render brødtekst-sektioner og refleksioner fra et body-stykke."""
    out = ""
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
    return out


def render_kapitel_fil(filnavn: str, kapitel_nr: int) -> str:
    """Render én markdown-fil som kapitel — med illustrationen inline."""
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

    # Kapitel-hero illustration inline
    hero_svg = CHAPTER_HERO.get(filnavn)
    if hero_svg:
        out += render_illustration(hero_svg, f"Kapitel-hero ({titel})")

    # Special-cases: list de underliggende konstellations-tekster lige under
    # hovedillustrationen, så brugeren kan editere dem nær hovedillustrationen
    if filnavn == "de-syv-perspektiver":
        out += "**[ILLUSTRATION: De 7 Perspektiver — konstellations-tekster]**\n\n"
        out += "*Hvert perspektiv har en fuld titel + to-linjers cirkeltekst (samme tekst genbruges i alle perspektivets cirkel-varianter).*\n\n"
        for fuld, l1, l2 in PERSPEKTIVER_FIGURER:
            out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
        out += "\n"
    elif filnavn == "de-otte-essentielle-egenskaber":
        out += "**[ILLUSTRATION: De 8 Egenskaber — konstellations-tekster]**\n\n"
        out += "*Hver egenskab har en fuld titel + to-linjers cirkeltekst.*\n\n"
        for fuld, l1, l2 in EGENSKABER_FIGURER:
            out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
        out += "\n"
        out += "**[UNDEROVERSKRIFTER: 8 Egenskaber — taglines]**\n\n"
        out += "*Korte taglines tilføjet under hver egenskab i bogen (ikke i kildemarkdown).*\n\n"
        for k, v in EGENSKAB_SUBTITLES.items():
            out += f"- **{k}** → {v}\n"
        out += "\n"
    elif filnavn == "de-fem-zoner":
        out += "**[ILLUSTRATION: De 5 Rum — venn-tekster]**\n\n"
        out += "*Hvert rum har sin egen venn-figur (rum-a-figur.svg ... rum-e-figur.svg). Tekstindhold pr. rum:*\n\n"
        for rum_titel, svg_navn in RUM_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{rum_titel}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "helheden-under-pres":
        out += "**[ILLUSTRATION: Helheden under pres — fire forskydnings-figurer]**\n\n"
        out += "*Hver forskydning har sin egen konstellations-figur:*\n\n"
        for label, svg_navn in HELHED_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{label}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "de-fire-guidede-oevelser":
        out += "**[ILLUSTRATION: De 4 Øvelser — koncentriske-figurer]**\n\n"
        out += "*Hver øvelse har sin egen koncentriske-ovaler-figur:*\n\n"
        for label, svg_navn in OEVELSE_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{label}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "andre-traditioner-og-specielle-temaer":
        out += "**[UNDEROVERSKRIFTER: Specielle Temaer — taglines]**\n\n"
        out += "*Korte taglines tilføjet under hvert speciel-tema i bogen.*\n\n"
        for k, v in SPECIELLE_TEMAER_SUBTITLES.items():
            out += f"- **{k}** → {v}\n"
        out += "\n"

    # Brødtekst-sektioner og refleksioner
    out += render_kapitel_body_sektioner(body)

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

    # Samling-hero illustration
    samling_svg = SAMLING_HERO.get(undermappe)
    if samling_svg:
        out += render_illustration(samling_svg, f"Samling-hero ({samling_titel})")

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

        # Glyf eller stadie-figur inline
        if undermappe == "begreber":
            out += render_glyf_for_begreb(filnavn, del_titel)
        elif undermappe == "stadier":
            out += render_stadie_figur(filnavn, del_titel)

        # Brødtekst og refleksioner
        out += render_kapitel_body_sektioner(body)

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
    from byg_bog import render_litteraturliste as bog_litt
    raw = bog_litt()
    raw = re.sub(r'^# Litteraturliste', '# Litteraturliste', raw, count=1, flags=re.MULTILINE)
    return "\n" + raw + "\n"


def render_alle_invitationer_bilag() -> str:
    """Bilag: alle 120 daglige invitationer (kildedata)."""
    out = "\n# Bilag — Alle 120 Daglige Invitationer (kildedata)\n\n"
    out += "*Kun 15 invitationer bruges i bogen (én pr. kapitel). Resten er reservedata. Hver kategori har 20 invitationer.*\n\n"
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
        "princip": "De 10 Biodynamiske Principper",
        "blechschmidt": "Blechschmidt-Principper",
        "perspektiv": "De 7 Perspektiver",
        "egenskab": "De 8 Essentielle Egenskaber",
        "zone": "De 5 Rum",
        "stadie": "De 5 Stadier",
    }
    for cat in rækkefølge:
        out += f"## {KATEGORI_NAVNE.get(cat, cat)}\n\n"
        for t in grupper[cat]:
            out += f"### {t['navn']}\n\n"
            out += f"- **Titel:** {t['navn']}\n"
            out += f"- **Evokation:** {t['evokation']}\n"
            out += f"- **Invitation:** {t['invitation']}\n\n"
    return out


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

    out.append(render_alle_invitationer_bilag())
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
            print("PANDOC FEJL:", r.stderr[-2000:], file=sys.stderr)
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
