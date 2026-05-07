#!/usr/bin/env python3
"""
byg_bog.py — Samler appens markdown-indhold til ét bog-manuskript og
genererer PDF via pandoc + xelatex.

Output:
  tools/output/manuskript.md      — samlet markdown
  tools/output/manuskript.pdf     — designet PDF (kræver pandoc + xelatex)

Bog-struktur:
  Forord (uddrag fra info.html "Bag denne app")
  DEL I — MODELLEN
    1. Den Biodynamiske Model
    2. Blechschmidts Principper
    3. De 18 Begreber (samling)
    4. I Behandlingssituationen
    5. Helheden Under Pres
    6. Ordliste
  DEL II — BEHANDLEREN
    7. De Otte Essentielle Egenskaber
    8. De Fem Rum
    9. Typiske Klientmønstre
  DEL III — REJSEN
    10. De Fem Stadier
    11. De Syv Perspektiver
    12. De Fire Guidede Øvelser
  DEL IV — INSPIRATION
    13. Andre Traditioner og Specielle Temaer
    14. Integration i Din Praksis
    15. Afslutning
  Appendiks A — Mit Spejl (arbejdshæfte)
  Appendiks B — Daglige Invitationer

Brug:
  python3 tools/byg_bog.py             # genererer markdown + PDF
  python3 tools/byg_bog.py --md         # kun markdown (hurtigere)
  python3 tools/byg_bog.py --html       # markdown + HTML (uden xelatex)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

# ============================================================================
# STIER
# ============================================================================

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
HERO = ROOT / "hero-motiver"
OUT = ROOT / "tools" / "output"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================================
# BOG-STRUKTUR
# ============================================================================

# Hver del har en titel og en liste af kapitler.
# Et "kapitel" er enten:
#   ("fil", "filnavn-uden-md")              — én markdown-fil bliver kapitel
#   ("samling", "Titel", [filnavne])         — flere filer samles til ét kapitel
#                                               (hver fil bliver et "###" afsnit)

DEL_I_MODELLEN = ("DEL I — MODELLEN", [
    ("fil", "den-biodynamiske-model"),
    ("fil", "blechschmidts-principper"),
    ("samling", "De 18 Begreber", "begreber", [
        "01-dynamisk-stilhed",
        "02-breath-of-life",
        "03-primary-respiration",
        "04-midtlinjen",
        "05-the-health",
        "06-motion-present",
        "07-fulcrum",
        "08-stillpoints",
        "09-transmutation",
        "10-the-neutral",
        "11-automatic-shifting",
        "12-den-iboende-behandlingsplan",
        "13-fluid-body",
        "14-the-lesion-field",
        "15-potency",
        "16-ignition",
        "17-axial-fluctuations",
        "18-wholeness",
    ]),
    ("fil", "i-behandlingssituationen"),
    ("fil", "helheden-under-pres"),
])

DEL_II_BEHANDLEREN = ("DEL II — BEHANDLEREN", [
    ("fil", "de-otte-essentielle-egenskaber"),
    ("fil", "de-fem-zoner"),
    ("fil", "typiske-klientmoenstre"),
])

DEL_III_REJSEN = ("DEL III — REJSEN", [
    ("samling", "De Fem Stadier", "stadier", [
        "00-behandlerens-indre-rejse",
        "01-foerste-stadie",
        "02-andet-stadie",
        "03-tredje-stadie",
        "04-fjerde-stadie",
        "05-femte-stadie",
        "06-den-levende-spiral",
        "07-stadier-refleksioner",
    ]),
    ("fil", "de-syv-perspektiver"),
    ("fil", "de-fire-guidede-oevelser"),
])

DEL_IV_INSPIRATION = ("DEL IV — INSPIRATION", [
    ("fil", "andre-traditioner-og-specielle-temaer"),
    ("fil", "integration-i-din-praksis"),
    ("fil", "afslutning"),
    ("fil", "ordliste"),
])

DELE = [DEL_I_MODELLEN, DEL_II_BEHANDLEREN, DEL_III_REJSEN, DEL_IV_INSPIRATION]


# ============================================================================
# ILLUSTRATIONS-MAPPING
# ============================================================================

HERO_DIR = "hero-motiver"

CHAPTER_HERO = {
    "den-biodynamiske-model": "24-modellen-oversigt.svg",
    "blechschmidts-principper": "28-blechschmidt.svg",
    "i-behandlingssituationen": "i-behandlingssituationen.svg",
    "helheden-under-pres": "helhed-1-balance.svg",
    "ordliste": "38-ordliste.svg",
    "de-otte-essentielle-egenskaber": "29-egenskaber-oversigt.svg",
    "de-fem-zoner": "37-zoner-oversigt.svg",
    "typiske-klientmoenstre": "30-klientmoenstre-oversigt.svg",
    "de-syv-perspektiver": "32-perspektiver-oversigt.svg",
    "de-fire-guidede-oevelser": "33-oevelser-oversigt.svg",
    "andre-traditioner-og-specielle-temaer": "34-traditioner-oversigt.svg",
    "integration-i-din-praksis": "35-integration-oversigt.svg",
    "afslutning": "36-afslutning-oversigt.svg",
}

SAMLING_HERO = {
    "begreber": "00-begreber-oversigt.svg",
    "stadier": "31-stadier-oversigt.svg",
}

SUBSECTION_HERO = {
    "01-dynamisk-stilhed": "01-dynamisk-stilhed.svg",
    "02-breath-of-life": "02-breath-of-life.svg",
    "03-primary-respiration": "03-primary-respiration.svg",
    "04-midtlinjen": "04-midtlinjen.svg",
    "05-the-health": "05-the-health.svg",
    "06-motion-present": "06-motion-present.svg",
    "07-fulcrum": "07-fulcrum.svg",
    "08-stillpoints": "08-stillpoints.svg",
    "09-transmutation": "09-transmutation.svg",
    "10-the-neutral": "10-the-neutral.svg",
    "11-automatic-shifting": "11-automatic-shifting.svg",
    "12-den-iboende-behandlingsplan": "12-den-iboende-behandlingsplan.svg",
    "13-fluid-body": "13-fluid-body.svg",
    "14-the-lesion-field": "14-the-lesion-field.svg",
    "15-potency": "15-potency.svg",
    "16-ignition": "16-ignition.svg",
    "17-axial-fluctuations": "17-axial-fluctuations.svg",
    "18-wholeness": "18-wholeness.svg",
    "00-behandlerens-indre-rejse": "26-rejsen-oversigt.svg",
    "01-foerste-stadie": "s1-foerste-stadie.svg",
    "02-andet-stadie": "s2-andet-stadie.svg",
    "03-tredje-stadie": "s3-tredje-stadie.svg",
    "04-fjerde-stadie": "s4-fjerde-stadie.svg",
    "05-femte-stadie": "s5-femte-stadie.svg",
    "06-den-levende-spiral": "s6-den-levende-spiral.svg",
    "07-stadier-refleksioner": "refleksion-A-aabne-rum.svg",
}


# Mappe til konverterede PDF-figurer (SVG → PDF via rsvg-convert)
FIGURES_DIR = OUT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def svg_til_pdf(svg_sti: Path) -> Path | None:
    """Konvertér SVG til PDF via rsvg-convert. Cacher resultatet.

    LaTeX kan ikke direkte include SVG; vi pre-konverterer til PDF.
    Kræver rsvg-convert (Linux: librsvg2-bin, macOS: brew install librsvg).
    """
    if not svg_sti.exists():
        return None
    pdf_sti = FIGURES_DIR / (svg_sti.stem + ".pdf")
    # Cache: konvertér kun hvis SVG er nyere end PDF
    if pdf_sti.exists() and pdf_sti.stat().st_mtime >= svg_sti.stat().st_mtime:
        return pdf_sti
    try:
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(pdf_sti), str(svg_sti)],
            check=True, capture_output=True, timeout=30,
        )
        return pdf_sti
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  ! Kunne ikke konvertere {svg_sti.name}: {e}", file=sys.stderr)
        return None


def hero_markdown(svg_navn: str, bredde_pct: int = 55) -> str:
    """LaTeX raw block der indsætter en SVG (via PDF-konvertering) centreret.

    Bruger filnavn alene — LaTeX finder figurerne via \\graphicspath sat
    i header-include (peger til tools/output/figures/).
    """
    if not svg_navn:
        return ""
    svg_sti = ROOT / HERO_DIR / svg_navn
    pdf_sti = svg_til_pdf(svg_sti)
    if not pdf_sti:
        return ""
    # Brug kun filnavn (uden mappe) — graphicspath i LaTeX-header sætter mappen
    return (
        "\n```{=latex}\n"
        "\\begin{center}\n"
        f"\\includegraphics[width=0.{bredde_pct}\\textwidth]{{{pdf_sti.name}}}\n"
        "\\end{center}\n"
        "```\n\n"
    )


# ============================================================================
# PARSING
# ============================================================================

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str):
    """Returner (frontmatter_dict, content_str)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip().strip('"').strip("'")
            fm[k.strip()] = v
    return fm, body


def strip_relationer(content: str) -> str:
    """Fjern '## Relationer'-sektioner — de er app-specifikke krydshenvisninger."""
    return re.sub(
        r"^## Relationer\s*\n.*?(?=^## |\Z)",
        "",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )


def strip_html_illustrations(content: str) -> str:
    """Fjern <div class='reflection-illustration'>...</div>-blokke."""
    return re.sub(
        r'<div class="reflection-illustration">.*?</div>\s*',
        "",
        content,
        flags=re.DOTALL,
    )


def strip_html_zone_markers(content: str) -> str:
    """Fjern andre app-specifikke HTML-blokke."""
    return re.sub(r"<div[^>]*>.*?</div>\s*", "", content, flags=re.DOTALL)


def bump_headings(content: str, levels: int = 1) -> str:
    """Skub alle '#'-niveauer ned med 'levels' niveauer."""
    if levels == 0:
        return content
    prefix = "#" * levels
    return re.sub(r"^(#{1,6})\s", lambda m: prefix + m.group(1) + " ",
                  content, flags=re.MULTILINE)


def transform_refleksion_til_kasse(content: str) -> str:
    """
    Konvertér refleksions-sektioner til pandoc fenced div så de kan styles
    som kasse i PDF'en.

    Reglerne:
      1. Matcher 'Til refleksion' eller 'Til Refleksion' eller 'Refleksioner over X'
      2. Captures content frem til næste heading af samme eller højere niveau
         (subsections under refleksionen er IKKE et stop)
      3. Hvis refleksionen har subsections (deeper headings) → hver subsection
         bliver sin egen kasse med subsection-titlen som overskrift
      4. Hvis ingen subsections → én kasse med hele indholdet
      5. Indenfor hver kasse adskilles paragraffer med en lille ◆-separator
    """
    illustration = hero_markdown("refleksion-A-aabne-rum.svg", bredde_pct=22)

    lines = content.split('\n')
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(
            r'^(#{2,6})\s+(Til [Rr]efleksion|Refleksioner over .+)\s*$',
            line,
        )
        if m:
            level = len(m.group(1))
            parent_title = m.group(2).strip()
            # Find slut på sektion: næste heading <= level
            j = i + 1
            while j < len(lines):
                nxt = re.match(r'^(#{1,6})\s', lines[j])
                if nxt and len(nxt.group(1)) <= level:
                    break
                j += 1
            section_body = '\n'.join(lines[i + 1:j])
            output.append(_render_refleksion_section(parent_title, section_body, illustration, level))
            i = j
        else:
            output.append(line)
            i += 1
    return '\n'.join(output)


def _render_refleksion_section(parent_title: str, body: str, illustration: str, level: int) -> str:
    """En kasse pr. subsection. Ingen subsections → én kasse med hele body."""
    sub_pattern = re.compile(rf'^(#{{{level + 1}}})\s+(.+)$', re.MULTILINE)
    parts = sub_pattern.split(body)
    pre = parts[0].strip() if parts else ''

    boxes = []
    if len(parts) <= 1:
        # Ingen subsections
        if pre:
            boxes.append(_make_refleksion_box(parent_title, pre, illustration))
    else:
        if pre:
            boxes.append(_make_refleksion_box(parent_title, pre, illustration))
        for k in range(1, len(parts), 3):
            title = parts[k + 1].strip() if k + 1 < len(parts) else ''
            sub_body = parts[k + 2].strip() if k + 2 < len(parts) else ''
            if sub_body:
                boxes.append(_make_refleksion_box(title, sub_body, illustration))

    if not boxes:
        return ''
    return '\n\n'.join(boxes) + '\n'


def _make_refleksion_box(title: str, body: str, illustration: str) -> str:
    """Byg én fenced div for en refleksions-kasse med ◆-separator mellem paragraffer.

    Hver enkelt refleksion forhindres i at splittes mellem sider via \\needspace.
    Boksen får altid \\clearpage før OG efter, så den står alene på sin egen side
    og næste kapitel/begreb starter på en frisk side.
    """
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]

    # \needspace sikrer at en refleksion ikke starter for tæt på sidens bund
    # (resulterer i forced page break hvis pladsen ikke rækker)
    needspace = (
        "\n```{=latex}\n"
        "\\needspace{6\\baselineskip}\n"
        "```\n\n"
    )

    diamond = (
        "\n\n```{=latex}\n"
        "\\vspace{1.2em}\n"
        "\\begin{center}\n"
        "{\\Large $\\blacklozenge$}\n"
        "\\end{center}\n"
        "\\vspace{1.2em}\n"
        "```\n\n"
    )

    # Saml paragraffer med diamond mellem og needspace før hver
    if paragraphs:
        body_parts = []
        for i, p in enumerate(paragraphs):
            if i > 0:
                body_parts.append(diamond)
            body_parts.append(needspace + p)
        body_str = '\n'.join(body_parts)
    else:
        body_str = ''

    # Sideskift før OG efter — så boksen står alene + næste indhold starter frisk
    sideskift = "\n\n```{=latex}\n\\clearpage\n```\n\n"

    return (
        f'{sideskift}'
        '\n::: refleksion\n'
        f'{illustration}'
        f'**{title}**\n\n'
        f'{body_str}\n'
        ':::\n'
        f'{sideskift}'
    )


def laes_md(path: Path):
    """Læs markdown-fil og returner (frontmatter, content)."""
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    return fm, body


# ============================================================================
# RENDERING
# ============================================================================

def render_kapitel_fil(filnavn: str, kapitel_nr: int, undermappe: str = None) -> str:
    """Render én markdown-fil som et bog-kapitel."""
    if undermappe:
        path = CONTENT / undermappe / f"{filnavn}.md"
    else:
        path = CONTENT / f"{filnavn}.md"

    if not path.exists():
        return f"\n## Kapitel {kapitel_nr}: {filnavn} (mangler)\n\n*Filen kunne ikke findes: {path}*\n"

    fm, body = laes_md(path)

    # Rens indhold
    body = strip_relationer(body)
    body = strip_html_illustrations(body)

    # Bump alle eksisterende ## til ### (så kapitlet selv er ##)
    body = bump_headings(body, 1)

    # Til refleksion → fenced div
    body = transform_refleksion_til_kasse(body)

    # Byg kapitel-overskrift
    titel = fm.get("titel", filnavn).strip()
    undertitel = fm.get("undertitel", "").strip()

    header = f"\n## Kapitel {kapitel_nr}: {titel}\n"
    if undertitel:
        header += f"\n*{undertitel}*\n"

    # Hero-illustration (lige under kapitel-titel, før indhold)
    hero_svg = CHAPTER_HERO.get(filnavn)
    hero = hero_markdown(hero_svg, bredde_pct=55) if hero_svg else ""

    # Daglige invitationer som afsluttende afsnit (hvis kapitel har en kategori)
    inv_kategori = INVITATIONER_KAPITEL_MAP.get(filnavn)
    invitationer = render_invitationer_for_kategori(inv_kategori, niveau=3) if inv_kategori else ""

    return header + "\n" + hero + body.strip() + "\n" + invitationer + "\n"


def render_samling(titel: str, undermappe: str, filnavne: list,
                   kapitel_nr: int) -> str:
    """Render en samling af filer som ét kapitel med ###-underafsnit."""
    out = [f"\n## Kapitel {kapitel_nr}: {titel}\n"]

    # Hero ved samlingens start
    samling_hero_svg = SAMLING_HERO.get(undermappe)
    if samling_hero_svg:
        out.append(hero_markdown(samling_hero_svg, bredde_pct=55))

    for filnavn in filnavne:
        path = CONTENT / undermappe / f"{filnavn}.md"
        if not path.exists():
            out.append(f"\n### {filnavn} (mangler)\n")
            continue

        fm, body = laes_md(path)
        body = strip_relationer(body)
        body = strip_html_illustrations(body)
        # Bump 2 levels: ## → ####, så samlingens entries er ### og deres sektioner ####
        body = bump_headings(body, 2)
        body = transform_refleksion_til_kasse(body)

        del_titel = fm.get("titel", filnavn).strip()
        del_undertitel = fm.get("undertitel", "").strip()

        out.append(f"\n### {del_titel}")
        if del_undertitel:
            out.append(f"\n*{del_undertitel}*\n")

        # Hero pr. underafsnit
        sub_hero_svg = SUBSECTION_HERO.get(filnavn)
        if sub_hero_svg:
            out.append(hero_markdown(sub_hero_svg, bredde_pct=45))

        out.append("\n" + body.strip() + "\n")

    # Daglige invitationer for samlingen (fx 'stadie'-kategori bag De Fem Stadier)
    inv_kategori = INVITATIONER_SAMLING_MAP.get(undermappe)
    if inv_kategori:
        out.append(render_invitationer_for_kategori(inv_kategori, niveau=3))

    return "\n".join(out)


def render_kapitel(spec, kapitel_nr: int) -> str:
    """Dispatcher: håndter ('fil', ...) og ('samling', ...)."""
    if spec[0] == "fil":
        return render_kapitel_fil(spec[1], kapitel_nr)
    elif spec[0] == "samling":
        _, titel, undermappe, filnavne = spec
        return render_samling(titel, undermappe, filnavne, kapitel_nr)
    else:
        raise ValueError(f"Ukendt spec: {spec}")


# ============================================================================
# FORORD og APPENDIKSER
# ============================================================================

# ============================================================================
# DAGLIGE INVITATIONER — fordelt pr. kategori, en gruppe pr. tematisk kapitel
# ============================================================================

# Tidligere fordeltes daglige invitationer pr. kategori inde i de tematiske
# kapitler. De er nu samlet bagest i bogen som Appendiks — derfor er disse
# maps tomme. Bevarede som hooks ifald de skal bruges igen.
INVITATIONER_KAPITEL_MAP: dict = {}
INVITATIONER_SAMLING_MAP: dict = {}

# Cache for at undgå at læse JSON flere gange
_MIKROTEKSTER_CACHE = None


def hent_mikrotekster():
    global _MIKROTEKSTER_CACHE
    if _MIKROTEKSTER_CACHE is None:
        path = ROOT / "content" / "daglig-draw" / "mikrotekster.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        _MIKROTEKSTER_CACHE = data.get("mikrotekster", [])
    return _MIKROTEKSTER_CACHE


def render_invitationer_for_kategori(kategori: str, niveau: int = 3) -> str:
    """Render alle mikrotekster for en given kategori som markdown-blok.

    `niveau` styrer overskrifts-dybden: 3 = ### for inde i kapitel.
    """
    teksters = [t for t in hent_mikrotekster() if t.get("kategori") == kategori]
    if not teksters:
        return ""

    # Hent label fra første tekst
    label = teksters[0].get("kategori_label", kategori).lower()
    # Lav til "principperne", "embryologien" osv. — eller bare bevar label
    overskrift_pre = "#" * niveau
    sub_pre = "#" * (niveau + 1)

    out = []
    out.append(f"\n{overskrift_pre} Daglige invitationer\n")
    out.append(
        "*En invitation pr. dag — eller blot en at hvile ved når der er behov.*\n"
    )

    for t in teksters:
        navn = t.get("navn", "")
        evokation = t.get("evokation", "")
        invitation = t.get("invitation", "")
        out.append(f"\n{sub_pre} {navn}\n")
        if evokation:
            out.append(evokation + "\n")
        if invitation:
            out.append(f"\n*{invitation}*\n")

    return "\n".join(out)


def render_litteraturliste() -> str:
    """Litteraturliste over inspirations-kilder bag bogen."""
    return dedent("""
        # Litteraturliste

        ## James Jealous, D.O.

        - **Audio Lectures** — © 2000-2025 Marnee Jealous Long – All Rights Reserved
        - **Healing and the Natural World** (1997)

        ## William Garner Sutherland, D.O.

        - **The Cranial Bowl** (1939)
        - **Teachings in the Science of Osteopathy** (redigeret af Anne L. Wales, 1990, posthumt udgivet)
        - **Contributions of Thought: The Collected Writings of William Garner Sutherland, D.O.** (redigeret af Adah Strand Sutherland og Anne L. Wales, 1967, 1971)

        ## Erich Blechschmidt, M.D.

        - **The Beginnings of Human Life** (1977) — Springer-Verlag
        - **The Ontogenetic Basis of Human Anatomy: A Biodynamic Approach to Development from Conception to Birth** (2004, posthumt udgivet, redigeret af Brian Freeman) — North Atlantic Books
        - **Biokinetics and Biodynamics of Human Differentiation** (med R.F. Gasser, 1978/2012) — North Atlantic Books

        ## Rollin E. Becker, D.O.

        - **Life in Motion: The Osteopathic Vision of Rollin E. Becker, D.O.** (1997, redigeret af Rachel E. Brooks, M.D.) — Stillness Press
        - **The Stillness of Life: The Osteopathic Philosophy of Rollin E. Becker, D.O.** (2000, redigeret af Rachel E. Brooks, M.D.) — Stillness Press

        ## Robert Fulford, D.O.

        - **Dr. Fulford's Touch of Life: The Healing Power of the Natural Life Force** (1996, med Gene Stone) — Pocket Books

        ## Charles Ridley, D.A.

        - **Stillness: Biodynamic Cranial Practice and the Evolution of Consciousness** (2006) — North Atlantic Books

        ## Michael Kern, D.O., R.C.S.T.

        - **Wisdom in the Body: The Craniosacral Approach to Essential Health** (1999, revideret 2005) — North Atlantic Books

        ## Franklyn Sills, R.C.S.T.

        - **Craniosacral Biodynamics, Volume One: The Breath of Life, Biodynamics, and Fundamental Skills** (2001) — North Atlantic Books
        - **Craniosacral Biodynamics, Volume Two: The Primal Midline and the Organization of the Body** (2004) — North Atlantic Books
        - **Foundations in Craniosacral Biodynamics, Volume One: The Breath of Life and Fundamental Skills** (2011) — North Atlantic Books
        - **Foundations in Craniosacral Biodynamics, Volume Two: The Sentient Embryo, Tissue Intelligence, and Trauma Resolution** (2012) — North Atlantic Books

        ## Michael Shea, Ph.D.

        - **Biodynamic Craniosacral Therapy, Volume One** (2007) — North Atlantic Books
        - **Biodynamic Craniosacral Therapy, Volume Two** (2008) — North Atlantic Books

        ## Francisco Varela

        - **The Embodied Mind: Cognitive Science and Human Experience** (1991, med Evan Thompson og Eleanor Rosch) — MIT Press
        - **The Tree of Knowledge: The Biological Roots of Human Understanding** (1987, med Humberto Maturana) — Shambhala

        ## Stephen Porges, Ph.D.

        - **The Polyvagal Theory: Neurophysiological Foundations of Emotions, Attachment, Communication, and Self-Regulation** (2011) — W.W. Norton
        - **The Pocket Guide to the Polyvagal Theory: The Transformative Power of Feeling Safe** (2017) — W.W. Norton

        ## Peter Levine, Ph.D.

        - **Waking the Tiger: Healing Trauma** (1997) — North Atlantic Books
        - **In an Unspoken Voice: How the Body Releases Trauma and Restores Goodness** (2010) — North Atlantic Books
        - **Trauma and Memory: Brain and Body in a Search for the Living Past** (2015) — North Atlantic Books

        ## Thomas Hübl

        - **Healing Collective Trauma: A Process for Integrating Our Intergenerational and Cultural Wounds** (2020) — Sounds True
        - **Attuned: Practicing Interdependence to Heal Our Trauma—and Our World** (2023) — Sounds True

        ## Andrew Taylor Still, M.D., D.O.

        - **Autobiography of Andrew Taylor Still** (1897, genudgivet mange gange)
        - **The Philosophy and Mechanical Principles of Osteopathy** (1902)
        - **Osteopathy: Research and Practice** (1910)
        - **Philosophy of Osteopathy** (1899)

        ## Alain Gehin, D.O.

        - **The Atlas of Manipulative Techniques for the Cranium and the Face** (2007, med François Ricard) — Elsevier
        - **Cranial Osteopathic Biomechanics, Pathomechanics and Diagnostics for Practitioners** (2007) — Churchill Livingstone

        ## Thomas Myers

        - **Anatomy Trains: Myofascial Meridians for Manual and Movement Therapists** (1st edition 2001, 4th edition 2020) — Elsevier
        - **BodyReading: Visual Assessment and the Anatomy Trains** (2010) — DVDs og undervisningsmateriale

        ## Giovanni Maciocia

        - **The Foundations of Chinese Medicine: A Comprehensive Text** (1st edition 1989, 3rd edition 2015) — Elsevier
        - **The Practice of Chinese Medicine** (1st edition 1994, 2nd edition 2007) — Churchill Livingstone
        - **The Psyche in Chinese Medicine** (2009) — Churchill Livingstone

        ## Jin Shin Jyutsu

        - Mary Burmeister — bragte Jin Shin Jyutsu til Vesten
            - **Jin Shin Jyutsu: Getting to Know (Help) Myself** (1985) — selvudgivet
            - **Introducing Jin Shin Jyutsu Is** (Books 1-3) — selvudgivet
        - Alice Burmeister & Tom Monte
            - **The Touch of Healing: Energizing the Body, Mind, and Spirit with Jin Shin Jyutsu** (1997) — Bantam Books

        ## The Web That Has No Weaver

        - Ted J. Kaptchuk, O.M.D.
            - **The Web That Has No Weaver: Understanding Chinese Medicine** (1st edition 1983, 2nd edition 2000) — McGraw-Hill

        ## Robert Schleip, Ph.D.

        - **Fascia: The Tensional Network of the Human Body** (2012, 2nd edition 2021, redigeret med Thomas Findley, Leon Chaitow, Peter Huijing) — Elsevier
        - **Fascia in Sport and Movement** (2015, 2nd edition 2021) — Handspring Publishing

        ## Jean-Pierre Barral, D.O.

        - **Visceral Manipulation** (1988, med Pierre Mercier) — Eastland Press
        - **Manual Thermal Evaluation** (2005) — North Atlantic Books
        - **The Thorax** (1991) — Eastland Press

        ## James L. Oschman, Ph.D.

        - **Energy Medicine: The Scientific Basis** (1st edition 2000, 2nd edition 2015) — Churchill Livingstone
        - **Energy Medicine in Therapeutics and Human Performance** (2003) — Butterworth-Heinemann
    """).strip() + "\n"


def render_appendiks_invitationer() -> str:
    """Saml alle 120 mikrotekster som ét appendiks bagest i bogen."""
    teksters = hent_mikrotekster()

    # Gruppér efter kategori_label
    grupper = {}
    rækkefølge = []
    for t in teksters:
        label = t.get("kategori_label", "Andet")
        if label not in grupper:
            rækkefølge.append(label)
            grupper[label] = []
        grupper[label].append(t)

    out = ["\n# Appendiks — Daglige Invitationer\n"]
    out.append(
        "*120 mikrotekster — én pr. dag, eller blot en at hvile ved når der er behov.*\n"
    )

    for label in rækkefølge:
        out.append(f"\n## {label.title()}\n")
        for t in grupper[label]:
            navn = t.get("navn", "")
            evokation = t.get("evokation", "")
            invitation = t.get("invitation", "")
            out.append(f"\n### {navn}\n")
            if evokation:
                out.append(f"\n{evokation}\n")
            if invitation:
                out.append(f"\n*{invitation}*\n")

    return "\n".join(out)


def render_forord() -> str:
    """Forord ekstraheret fra info.html 'Bag denne app'."""
    info = (ROOT / "info.html").read_text(encoding="utf-8")
    # Find sektionen
    m = re.search(
        r'<!-- Bag denne app -->.*?<section[^>]*>(.*?)</section>',
        info,
        re.DOTALL,
    )
    if not m:
        return "\n# Forord\n\n*(kunne ikke ekstrahere forord fra info.html)*\n"

    raw = m.group(1)
    # Strip HTML tags, behold paragraffer
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', raw, re.DOTALL)
    out = ["\n# Forord\n"]
    for p in paragraphs:
        clean = re.sub(r"<[^>]+>", "", p).strip()
        # Erstat <em>...</em> med _..._ (bevares fra HTML — gør markdown)
        clean = re.sub(r"<em>(.*?)</em>", r"*\1*", clean)
        if clean:
            out.append(clean + "\n")
    return "\n".join(out)



# ============================================================================
# SAMLET MANUSKRIPT
# ============================================================================

def byg_manuskript() -> str:
    out = []

    # Titelside
    out.append(dedent("""
        ---
        title: "Den Biodynamiske Model"
        subtitle: "En levende kompagnion"
        author: "Niklas Patursson"
        lang: da
        documentclass: book
        classoption:
          - openany
          - 11pt
        geometry:
          - paperwidth=148mm
          - paperheight=210mm
          - top=22mm
          - bottom=22mm
          - left=20mm
          - right=20mm
        mainfont: "TeX Gyre Pagella"
        sansfont: "TeX Gyre Heros"
        fontsize: 11pt
        linestretch: 1.35
        toc: true
        toc-depth: 2
        ...
    """).strip())

    # Note om typografi:
    # - Standard: TeX Gyre Pagella (serif, Garamond-lignende) + TeX Gyre Heros (sans).
    #   Disse er altid tilgængelige med texlive-fonts-recommended.
    # - Til endelig udgivelse: skift til 'Cormorant Garamond' og 'Cinzel' (samme
    #   som appens typografi) ved at ændre mainfont/sansfont ovenfor — kræver
    #   at fontene er installeret system-wide på maskinen der genererer PDF'en.

    # Forord
    out.append(render_forord())

    # Dele og kapitler
    kapitel_nr = 1
    for del_titel, kapitler in DELE:
        out.append(f"\n# {del_titel}\n")
        for spec in kapitler:
            out.append(render_kapitel(spec, kapitel_nr))
            kapitel_nr += 1

    # Bagstof: Litteraturliste, derefter Appendiks med daglige invitationer
    out.append(render_litteraturliste())
    out.append(render_appendiks_invitationer())

    return "\n\n".join(out)


# ============================================================================
# PANDOC
# ============================================================================

def latex_header_med_graphicspath() -> str:
    """Bygges dynamisk så graphicspath peger til den faktiske figures-mappe."""
    figures_path = str(FIGURES_DIR.resolve()).replace("\\", "/")
    root_path = str(ROOT.resolve()).replace("\\", "/")
    # graphicspath kræver INGEN mellemrum mellem inder-{} og indhold.
    # Vi tilføjer både figures/ (til kapitel-illustrationer) og roden
    # (til hero_dbm.png på forsiden).
    graphicspath = "\\graphicspath{{" + figures_path + "/}{" + root_path + "/}}"
    return dedent(rf"""
        \usepackage{{xcolor}}
        \usepackage{{amssymb}}
        \usepackage{{tcolorbox}}
        \tcbuselibrary{{breakable, skins}}
        \usepackage{{fancyhdr}}
        \usepackage{{tikz}}
        \usepackage{{needspace}}
        {graphicspath}
        \definecolor{{refleksionbg}}{{RGB}}{{248, 245, 238}}
        \definecolor{{refleksionborder}}{{RGB}}{{180, 165, 145}}
        \newtcolorbox{{refleksionbox}}{{
          enhanced,
          colback=refleksionbg,
          colframe=refleksionborder,
          boxrule=0.4pt,
          arc=2pt,
          breakable,
          left=10pt,
          right=10pt,
          top=8pt,
          bottom=8pt
        }}

        % Sidetal nederst til højre — også på chapter-start-sider
        \pagestyle{{fancy}}
        \fancyhf{{}}
        \fancyfoot[R]{{\thepage}}
        \renewcommand{{\headrulewidth}}{{0pt}}
        \renewcommand{{\footrulewidth}}{{0pt}}
        \fancypagestyle{{plain}}{{
          \fancyhf{{}}
          \fancyfoot[R]{{\thepage}}
          \renewcommand{{\headrulewidth}}{{0pt}}
          \renewcommand{{\footrulewidth}}{{0pt}}
        }}

        % Custom forside med hero_dbm.png som baggrund og overlay-tekst
        \renewcommand{{\maketitle}}{{
          \begin{{titlepage}}
          \thispagestyle{{empty}}
          \begin{{tikzpicture}}[remember picture, overlay]
            % Helsides baggrundsbillede
            \node[anchor=center, inner sep=0pt] at (current page.center)
              {{\includegraphics[width=\paperwidth, height=\paperheight]{{hero_dbm.png}}}};
            % Titel + undertitel placeret midt mellem top og havoverfladen
            \node[anchor=center, text=white, align=center] at ([yshift=0.20\paperheight]current page.center)
              {{{{\fontsize{{28}}{{34}}\selectfont Den Biodynamiske Model}}\\[1.2em]
               {{\fontsize{{16}}{{20}}\selectfont \textit{{En levende kompagnion}}}}}};
            % Forfatter nederst
            \node[anchor=center, text=white] at ([yshift=-0.40\paperheight]current page.center)
              {{{{\fontsize{{14}}{{18}}\selectfont Niklas Patursson}}}};
          \end{{tikzpicture}}
          \end{{titlepage}}
        }}
    """).strip()

# Pandoc filter for fenced div :::refleksion::: → tcolorbox
LUA_FILTER = dedent(r"""
function Div(el)
  if el.classes:includes("refleksion") then
    return {
      pandoc.RawBlock("latex", "\\begin{refleksionbox}"),
      pandoc.Div(el.content),
      pandoc.RawBlock("latex", "\\end{refleksionbox}")
    }
  end
end
""").strip()


def kor_pandoc(md_path: Path, fmt: str, out_path: Path) -> bool:
    """Kør pandoc til ønsket format. Returner True ved succes."""
    header_path = OUT / "_latex_header.tex"
    header_path.write_text(latex_header_med_graphicspath(), encoding="utf-8")

    filter_path = OUT / "_refleksion_filter.lua"
    filter_path.write_text(LUA_FILTER, encoding="utf-8")

    cmd = ["pandoc", str(md_path), "-o", str(out_path),
           "--top-level-division=part",
           "--toc",
           "--resource-path", str(OUT),
           f"--lua-filter={filter_path}"]

    if fmt == "pdf":
        cmd += ["--pdf-engine=xelatex",
                f"--include-in-header={header_path}"]
    elif fmt == "html":
        cmd += ["--standalone", "--mathjax"]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"PANDOC FEJL ({fmt}):", r.stderr[-2000:], file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"PANDOC TIMEOUT ({fmt})", file=sys.stderr)
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Saml app-indhold til bog-manuskript")
    parser.add_argument("--md", action="store_true",
                        help="Kun markdown (skip pandoc)")
    parser.add_argument("--html", action="store_true",
                        help="Markdown + HTML (uden xelatex)")
    args = parser.parse_args()

    print("Bygger manuskript fra content/-filer …")
    manuskript = byg_manuskript()

    md_path = OUT / "manuskript.md"
    md_path.write_text(manuskript, encoding="utf-8")
    print(f"  ✓ {md_path} ({len(manuskript):,} tegn)")

    if args.md:
        return

    # Default: PDF (medmindre --html angivet)
    if args.html:
        html_path = OUT / "manuskript.html"
        if kor_pandoc(md_path, "html", html_path):
            print(f"  ✓ {html_path}")
        else:
            print("  × HTML fejlede", file=sys.stderr)
            sys.exit(1)
    else:
        pdf_path = OUT / "manuskript.pdf"
        if kor_pandoc(md_path, "pdf", pdf_path):
            print(f"  ✓ {pdf_path}")
        else:
            print("  × PDF fejlede — prøv --html eller --md", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
