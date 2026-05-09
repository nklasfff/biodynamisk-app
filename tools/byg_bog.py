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
import textwrap
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

DEL_I_MODELLEN = (
    "Modellen",
    "Den biodynamiske model fra dens kilder hos Sutherland og Blechschmidt til Jealous' samlende vision. De atten kerne-begreber, behandlingssituationens dynamik, og det landskab der opstår når helheden kommer under pres.",
    [
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

DEL_II_BEHANDLEREN = (
    "Behandleren",
    "Behandleren er det vigtigste instrument i den biodynamiske praksis. De otte essentielle egenskaber, de fem rum hvor behandlingen finder sted — fra den fysiske krop til dynamisk stilhed — og de mønstre klienter typisk møder os med.",
    [
    ("fil", "de-otte-essentielle-egenskaber"),
    ("fil", "de-fem-zoner"),
    ("fil", "typiske-klientmoenstre"),
])

DEL_III_REJSEN = (
    "Rejsen",
    "Behandleren udvikler sig gennem fem stadier, der opleves som en spiral snarere end en stige. De syv perspektiver giver dybde til praksis, og fire guidede øvelser træner sansningen af det biodynamiske felt.",
    [
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

DEL_IV_INSPIRATION = (
    "Inspiration",
    "Den biodynamiske model står ikke alene. Mødet med andre traditioner og specielle temaer, integration i din eksisterende praksis, en samlet refleksion over rejsen ud og hjem — og en ordliste til de centrale begreber.",
    [
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
    "den-biodynamiske-model": "den-biodynamiske-model-figur.svg",
    "blechschmidts-principper": "embryologi-figur.svg",
    "i-behandlingssituationen": "i-behandlingssituationen-figur.svg",
    "helheden-under-pres": "helheden-under-pres-figur.svg",
    "ordliste": "ordliste-figur.svg",
    "de-otte-essentielle-egenskaber": "otte-egenskaber-figur.svg",
    "de-fem-zoner": "de-fem-rum-figur.svg",
    "typiske-klientmoenstre": "klientmoenstre-figur.svg",
    "de-syv-perspektiver": "de-syv-perspektiver-figur.svg",
    "de-fire-guidede-oevelser": "de-fire-oevelser-figur.svg",
    "andre-traditioner-og-specielle-temaer": "traditioner-figur.svg",
    "integration-i-din-praksis": "integration-figur.svg",
    "afslutning": "afslutning-figur.svg",
}

SAMLING_HERO = {
    "begreber": "begreber-figur.svg",
    "stadier": "behandlerens-indre-rejse-figur.svg",
}

SUBSECTION_HERO = {
    "01-dynamisk-stilhed": "glyf-01-dynamisk-stilhed.svg",
    "02-breath-of-life": "glyf-02-breath-of-life.svg",
    "03-primary-respiration": "glyf-03-primary-respiration.svg",
    "04-midtlinjen": "glyf-04-midtlinjen.svg",
    "05-the-health": "glyf-05-the-health.svg",
    "06-motion-present": "glyf-06-motion-present.svg",
    "07-fulcrum": "glyf-07-fulcrum.svg",
    "08-stillpoints": "glyf-08-stillpoints.svg",
    "09-transmutation": "glyf-09-transmutation.svg",
    "10-the-neutral": "glyf-10-the-neutral.svg",
    "11-automatic-shifting": "glyf-11-automatic-shifting.svg",
    "12-den-iboende-behandlingsplan": "glyf-12-den-iboende-behandlingsplan.svg",
    "13-fluid-body": "glyf-13-fluid-body.svg",
    "14-the-lesion-field": "glyf-14-the-lesion-field.svg",
    "15-potency": "glyf-15-potency.svg",
    "16-ignition": "glyf-16-ignition.svg",
    "17-axial-fluctuations": "glyf-17-axial-fluctuations.svg",
    "18-wholeness": "glyf-18-wholeness.svg",
    "01-foerste-stadie": "stadie-1-figur.svg",
    "02-andet-stadie": "stadie-2-figur.svg",
    "03-tredje-stadie": "stadie-3-figur.svg",
    "04-fjerde-stadie": "stadie-4-figur.svg",
    "05-femte-stadie": "stadie-5-figur.svg",
    "06-den-levende-spiral": "den-levende-spiral-figur.svg",
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
    return _konverter_svg(svg_sti, "pdf")


def svg_til_png(svg_sti: Path) -> Path | None:
    """Konvertér SVG til PNG via rsvg-convert. Cacher resultatet.

    Bruges til DOCX-output hvor Word ikke håndterer SVG godt.
    """
    return _konverter_svg(svg_sti, "png", scale=2)


def _konverter_svg(svg_sti: Path, fmt: str, scale: int = 1) -> Path | None:
    if not svg_sti.exists():
        return None
    out_sti = FIGURES_DIR / (svg_sti.stem + "." + fmt)
    if out_sti.exists() and out_sti.stat().st_mtime >= svg_sti.stat().st_mtime:
        return out_sti
    cmd = ["rsvg-convert", "-f", fmt, "-o", str(out_sti)]
    if fmt == "png" and scale != 1:
        # Større opløsning til PNG (Word-rendering)
        cmd += ["-z", str(scale)]
    cmd.append(str(svg_sti))
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        return out_sti
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  ! Kunne ikke konvertere {svg_sti.name} til {fmt}: {e}", file=sys.stderr)
        return None


def konverter_til_docx_md(md_text: str) -> str:
    """Konvertér PDF-manuskriptet til DOCX-venligt markdown.

    Erstatter alle raw LaTeX-blokke med pandoc-markdown ekvivalenter:
      - \\includegraphics{X.pdf} → centreret PNG-figur via raw OpenXML
      - \\blacklozenge-blok → centreret ◆-paragraph + luftrum
      - \\clearpage → Word-sideskift via raw OpenXML
      - \\needspace → tomme linjer for luft

    For hver PDF-figur sikres at der findes en tilsvarende PNG-version.
    """
    # OpenXML-snippets — virker i pandoc DOCX-output via ```{=openxml}
    docx_pagebreak = (
        "\n\n```{=openxml}\n"
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
        "```\n\n"
    )
    docx_centered_paragraph = (
        '\n\n```{=openxml}\n'
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:t xml:space="preserve">{indhold}</w:t></w:r></w:p>\n'
        '```\n\n'
    )

    # 1. \includegraphics-blokke → centreret markdown-figur med PNG.
    # Vi bruger en ekstra blank linje før og en `:::` div med center-class for
    # at få pandoc til at wrappe figuren i en centreret paragraph i Word.
    def erstat_includegraphics(m):
        block = m.group(0)
        width_match = re.search(r'width=0\.(\d+)\\textwidth', block)
        file_match = re.search(r'\{([\w\-]+)\.pdf\}', block)
        if not file_match:
            return ''
        navn = file_match.group(1)
        bredde_pct = int(width_match.group(1)) if width_match else 55
        # Sørg for at PNG findes — tjek både hero-motiver/ og figures/
        # (oval-side-SVG'er ligger i figures/)
        svg_sti = ROOT / HERO_DIR / (navn + ".svg")
        if not svg_sti.exists():
            svg_sti = FIGURES_DIR / (navn + ".svg")
        if svg_sti.exists():
            svg_til_png(svg_sti)

        figur_md = f'![]({navn}.png){{width={bredde_pct}% fig-align="center"}}'

        # Hvis blokken indeholder \clearpage (oval-sider efter kapitler),
        # skal vi konvertere til DOCX-sideskift før og efter figuren.
        if "\\clearpage" in block:
            return (f'\n\n{docx_pagebreak}\n{figur_md}\n{docx_pagebreak}\n\n')
        return f'\n\n{figur_md}\n\n'

    # Tillad valgfrie LaTeX-kommandoer (\clearpage, \thispagestyle, \null\vfill
    # osv.) før \begin{center} og efter \end{center} inden for samme raw-blok.
    md_text = re.sub(
        r'```\{=latex\}\s*'
        r'(?:\\[a-zA-Z@]+\*?(?:\{[^}]*\})?\s*)*'
        r'\\begin\{center\}\s*\\includegraphics[^}]+\{[^}]+\}\s*\\end\{center\}\s*'
        r'(?:\\[a-zA-Z@]+\*?(?:\{[^}]*\})?\s*)*'
        r'```',
        erstat_includegraphics,
        md_text,
        flags=re.DOTALL,
    )

    # 2. Diamant-blokke → centreret ◆ med luft omkring (tomme paragraffer)
    md_text = re.sub(
        r'```\{=latex\}\s*\\vspace[^`]+\\blacklozenge[^`]+```',
        '\n\n```{=openxml}\n'
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t>◆</w:t></w:r></w:p>\n'
        '```\n\n',
        md_text,
        flags=re.DOTALL,
    )

    # 3. \clearpage → Word-sideskift. Konsekutive \clearpage-blokke
    # (med valgfri whitespace mellem) erstattes med ÉN sideskift for at
    # undgå tomme sider når flere clearpages stables (fx refleksions-
    # boks's afsluttende \clearpage + næste underkapitels indledende).
    md_text = re.sub(
        r'(?:```\{=latex\}\s*\\clearpage\s*```\s*)+',
        docx_pagebreak,
        md_text,
        flags=re.DOTALL,
    )

    # 4. \needspace → fjernes (sideskift håndterer struktur)
    md_text = re.sub(
        r'```\{=latex\}\s*\\needspace[^`]+```',
        '',
        md_text,
        flags=re.DOTALL,
    )

    # 4b. Refleksions-titler (\\textbf{...}) i raw LaTeX → centreret bold tekst
    # via OpenXML (pandoc dropper LaTeX raw blocks for DOCX).
    def erstat_refleksion_titel(m):
        titel = m.group(1).strip()
        return (
            '\n\n```{=openxml}\n'
            '<w:p>'
            '<w:pPr><w:jc w:val="center"/><w:spacing w:before="200" w:after="120"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t xml:space="preserve">{titel}</w:t></w:r>'
            '</w:p>\n'
            '```\n\n'
        )
    md_text = re.sub(
        r'```\{=latex\}\s*\\vspace\{1em\}\s*\\begin\{center\}\s*\\textbf\{([^}]+)\}\s*\\end\{center\}[^`]+```',
        erstat_refleksion_titel,
        md_text,
        flags=re.DOTALL,
    )

    # 5. Forside: indsæt hero_dbm.png + titel som første side, før Forord.
    # Kopier hero_dbm.png til figures/ så pandoc finder den via resource-path.
    hero_src = ROOT / "hero_dbm.png"
    hero_dst = FIGURES_DIR / "hero_dbm.png"
    if hero_src.exists():
        if not hero_dst.exists() or hero_dst.stat().st_mtime < hero_src.stat().st_mtime:
            import shutil
            shutil.copy(hero_src, hero_dst)
        forside = (
            '\n\n![](hero_dbm.png){width=100% fig-align="center"}\n\n'
            + docx_pagebreak
        )
        # Indsæt lige før '# Forord'
        md_text = md_text.replace('\n# Forord\n', forside + '\n# Forord\n', 1)

    return md_text


# ============================================================================
# PERSPEKTIV-FIGURER
# ============================================================================
#
# Hver af de 7 perspektiver får sin egen "konstellations-figur" med det
# aktuelle perspektiv i centrum og de øvrige 6 omkring i 6 mindre cirkler.
# Genererer SVG'er ud fra en fælles template.
# ============================================================================

# (canonical_titel, linje_1, linje_2)
# linje_1 og linje_2 bruges i selve cirklen (lowercase som i template)
PERSPEKTIVER_FIGURER = [
    ("Barnets Øjne og Livets Tempo", "Barnets øjne og", "livets tempo"),
    ("Stilhedens Skabende Kraft", "Stilhedens", "skabende kraft"),
    ("Modenhedens Samtidige Lag", "Modenhedens", "samtidige lag"),
    ("Bevægelsens Paradoks", "Bevægelsens", "paradoks"),
    ("At Blive Fundet af Verden", "At blive fundet", "af verden"),
    ("Gavens Forløsning", "Gavens", "forløsning"),
    ("Den Daglige Fordybelse", "Den daglige", "fordybelse"),
]

# 6 outer positions (clockwise from top): (cx, cy, gradient, text_color)
PERSPEKTIV_POSITIONS = [
    (500, 180, "g0", "#2D3748"),      # top — lys, mørk tekst
    (777.13, 340, "g1", "#2D3748"),   # top-right
    (777.13, 660, "g4", "#F7FAFC"),   # bottom-right
    (500, 820, "g3", "#F7FAFC"),      # bottom
    (222.87, 660, "g5", "#F7FAFC"),   # bottom-left
    (222.87, 340, "g2", "#2D3748"),   # top-left
]


def _build_perspektiv_svg(active_idx: int) -> str:
    """Byg én konstellations-SVG med perspektiv #active_idx i centrum."""
    center = PERSPEKTIVER_FIGURER[active_idx]
    others = [
        PERSPEKTIVER_FIGURER[(active_idx + i) % 7]
        for i in range(1, 7)
    ]

    # SVG-defs (gradients) — kopieret fra template
    defs = """  <defs>
    <radialGradient id="g0" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#E2E8F0"/>
      <stop offset="100%" stop-color="#CBD5E0"/>
    </radialGradient>
    <radialGradient id="g1" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#CBD5E0"/>
      <stop offset="100%" stop-color="#B8C2CE"/>
    </radialGradient>
    <radialGradient id="g2" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#B8C2CE"/>
      <stop offset="100%" stop-color="#A0AEC0"/>
    </radialGradient>
    <radialGradient id="g3" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#A0AEC0"/>
      <stop offset="100%" stop-color="#8A98AB"/>
    </radialGradient>
    <radialGradient id="g4" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#8A98AB"/>
      <stop offset="100%" stop-color="#718096"/>
    </radialGradient>
    <radialGradient id="g5" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#718096"/>
      <stop offset="100%" stop-color="#5A6678"/>
    </radialGradient>
    <radialGradient id="g6" cx="50%" cy="48%" r="68%">
      <stop offset="0%" stop-color="#4A5568"/>
      <stop offset="100%" stop-color="#2D3748"/>
    </radialGradient>
  </defs>"""

    # Linjer mellem alle cirkler — statiske
    lines = """  <g stroke="#718096" stroke-width="1" stroke-linecap="round" stroke-dasharray="1.5 5" fill="none" opacity="0.5">
    <line x1="500" y1="180" x2="500" y2="500"/>
    <line x1="777.13" y1="340" x2="500" y2="500"/>
    <line x1="777.13" y1="660" x2="500" y2="500"/>
    <line x1="500" y1="820" x2="500" y2="500"/>
    <line x1="222.87" y1="660" x2="500" y2="500"/>
    <line x1="222.87" y1="340" x2="500" y2="500"/>
    <line x1="500" y1="180" x2="777.13" y2="340"/>
    <line x1="500" y1="180" x2="777.13" y2="660"/>
    <line x1="500" y1="180" x2="500" y2="820"/>
    <line x1="500" y1="180" x2="222.87" y2="660"/>
    <line x1="500" y1="180" x2="222.87" y2="340"/>
    <line x1="777.13" y1="340" x2="777.13" y2="660"/>
    <line x1="777.13" y1="340" x2="500" y2="820"/>
    <line x1="777.13" y1="340" x2="222.87" y2="660"/>
    <line x1="777.13" y1="340" x2="222.87" y2="340"/>
    <line x1="777.13" y1="660" x2="500" y2="820"/>
    <line x1="777.13" y1="660" x2="222.87" y2="660"/>
    <line x1="777.13" y1="660" x2="222.87" y2="340"/>
    <line x1="500" y1="820" x2="222.87" y2="660"/>
    <line x1="500" y1="820" x2="222.87" y2="340"/>
    <line x1="222.87" y1="660" x2="222.87" y2="340"/>
  </g>"""

    # Cirkler — 6 outer + 1 center (statisk).
    # Radii er 5% større end template (97 vs 92, 116 vs 110) så teksten
    # får mere luft inde i cirklerne.
    circles_lines = []
    for (cx, cy, gid, _color) in PERSPEKTIV_POSITIONS:
        circles_lines.append(
            f'  <circle cx="{cx}" cy="{cy}" r="97" fill="url(#{gid})"/>'
        )
    circles_lines.append(
        '  <circle cx="500" cy="500" r="116" fill="url(#g6)"/>'
    )
    circles = "\n".join(circles_lines)

    # Tekster — grupperede efter farve (mørk vs lys) for matchende fyld
    dark_texts = []   # Tekst på lyse cirkler — #2D3748
    light_texts = []  # Tekst på mørke cirkler — #F7FAFC
    for (cx, cy, _gid, color), (_titel, l1, l2) in zip(PERSPEKTIV_POSITIONS, others):
        # 2-linjet tekst — y-offset omkring cirkel-center
        block = (
            f'      <text x="{cx}" y="{cy - 8}">{l1}</text>\n'
            f'      <text x="{cx}" y="{cy + 18}">{l2}</text>'
        )
        if color == "#2D3748":
            dark_texts.append(block)
        else:
            light_texts.append(block)

    # Center-tekst (på mørkeste cirkel — altid lys tekst, lidt større)
    center_text = (
        f'      <text x="500" y="490">{center[1]}</text>\n'
        f'      <text x="500" y="522">{center[2]}</text>'
    )

    texts = (
        '  <g font-style="italic" font-weight="500" text-anchor="middle" '
        'dominant-baseline="middle" letter-spacing="0.015em">\n'
        '    <g font-size="22" fill="#2D3748">\n'
        + "\n".join(dark_texts) + "\n"
        '    </g>\n'
        '    <g font-size="22" fill="#F7FAFC">\n'
        + "\n".join(light_texts) + "\n"
        '    </g>\n'
        '    <g font-size="28" fill="#F7FAFC">\n'
        + center_text + "\n"
        '    </g>\n'
        '  </g>'
    )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'style="font-family: \'TeX Gyre Pagella\', Palatino, serif;">\n'
        + defs + "\n\n"
        + lines + "\n\n"
        + circles + "\n\n"
        + texts + "\n"
        + '</svg>\n'
    )
    return svg


def perspektiv_filnavn(idx: int) -> str:
    """Returnér filnavn for perspektiv #idx (1-indexed via slug)."""
    slugs = [
        "perspektiv-1-barnets-oejne",
        "perspektiv-2-stilhedens-kraft",
        "perspektiv-3-modenhedens-lag",
        "perspektiv-4-bevaegelsens-paradoks",
        "perspektiv-5-blive-fundet",
        "perspektiv-6-gavens-forloesning",
        "perspektiv-7-daglige-fordybelse",
    ]
    return slugs[idx]


def generer_perspektiv_svgs():
    """Generer 7 SVG-filer i hero-motiver/, én pr. perspektiv."""
    for idx in range(7):
        svg = _build_perspektiv_svg(idx)
        sti = ROOT / HERO_DIR / (perspektiv_filnavn(idx) + ".svg")
        sti.write_text(svg, encoding="utf-8")


def injicer_perspektiv_figurer(body: str) -> str:
    """For hvert perspektiv-afsnit: clearpage + overskrift + centreret
    kursiv-undertitel + konstellations-figur.

    Body er på dette tidspunkt heading-bumpet, så perspektiv-titler står
    som '### Title' (level 3). I kilden følges hver titel af en kursiv
    underoverskrift (*— tagline*) som her konverteres til centreret
    underoverskrift, placeret over figuren.
    """
    generer_perspektiv_svgs()
    titel_til_idx = {p[0]: i for i, p in enumerate(PERSPEKTIVER_FIGURER)}

    def replace(m):
        heading_line = m.group(1)
        titel = m.group(2).strip()
        italic_text = m.group(3).replace('\n', ' ').strip()
        if titel not in titel_til_idx:
            return m.group(0)
        idx = titel_til_idx[titel]
        svg_navn = perspektiv_filnavn(idx) + ".svg"
        figur = hero_markdown(svg_navn, bredde_pct=66)
        return (
            clearpage_block()
            + heading_line
            + centreret_undertitel(italic_text)
            + figur
        )

    pattern = re.compile(
        r'(^### ([^\n]+)\n)'                               # heading
        r'\n+\*((?:[^*\n]|\n(?!\n))+?)\*\s*\n',            # *italic subtitle*
        re.MULTILINE,
    )
    return pattern.sub(replace, body)


# ============================================================================
# EGENSKAB-FIGURER (de 8 essentielle egenskaber)
# ============================================================================
#
# Samme princip som perspektiv-figurer — hver af de 8 egenskaber får sin
# egen figur med egenskaben i centrum og de øvrige 7 omkring.
# ============================================================================

# (canonical_titel_med_nummer, linje_1, linje_2)
EGENSKABER_FIGURER = [
    ("1. Neutral lytten uden agenda",       "Neutral lytten",       "uden agenda"),
    ("2. Selvregulering af nervesystemet",  "Selvregulering af",    "nervesystemet"),
    ("3. Sansning af den terapeutiske proces", "Sansning af den",   "terapeutiske proces"),
    ("4. Tålmodighed & uvished",            "Tålmodighed",          "& uvished"),
    ("5. At mærke helhedens prioritering",  "At mærke helhedens",   "prioritering"),
    ("6. Synkron bevægelse med kroppen",    "Synkron bevægelse",    "med kroppen"),
    ("7. Kvalitet i berøringen",            "Kvalitet i",           "berøringen"),
    ("8. Sans for behandlingens rytme",     "Sans for",             "behandlingens rytme"),
]

# 7 outer positions clockwise from top: (cx, cy, gradient_id, text_color)
EGENSKAB_POSITIONS = [
    (500, 180,        "g0", "#2D3748"),  # top — lys, mørk tekst
    (750.19, 300.48,  "g1", "#2D3748"),  # top-right — lys, mørk tekst
    (811.98, 571.21,  "g2", "#F7FAFC"),  # right — medium, lys tekst
    (638.84, 788.31,  "g3", "#F7FAFC"),  # bottom-right
    (361.16, 788.31,  "g4", "#F7FAFC"),  # bottom-left
    (188.02, 571.21,  "g5", "#F7FAFC"),  # left
    (249.81, 300.48,  "g6", "#F7FAFC"),  # top-left
]


def _build_egenskab_svg(active_idx: int) -> str:
    """Byg én konstellations-SVG med egenskab #active_idx i centrum."""
    center = EGENSKABER_FIGURER[active_idx]
    others = [
        EGENSKABER_FIGURER[(active_idx + i) % 8]
        for i in range(1, 8)
    ]

    # Defs (gradients)
    defs = """  <defs>
    <radialGradient id="g0" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#E2E8F0"/>
      <stop offset="100%" stop-color="#CBD5E0"/>
    </radialGradient>
    <radialGradient id="g1" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#CBD5E0"/>
      <stop offset="100%" stop-color="#B8C2CE"/>
    </radialGradient>
    <radialGradient id="g2" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#B8C2CE"/>
      <stop offset="100%" stop-color="#A0AEC0"/>
    </radialGradient>
    <radialGradient id="g3" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#A0AEC0"/>
      <stop offset="100%" stop-color="#8A98AB"/>
    </radialGradient>
    <radialGradient id="g4" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#8A98AB"/>
      <stop offset="100%" stop-color="#718096"/>
    </radialGradient>
    <radialGradient id="g5" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#718096"/>
      <stop offset="100%" stop-color="#5A6678"/>
    </radialGradient>
    <radialGradient id="g6" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#5A6678"/>
      <stop offset="100%" stop-color="#4A5568"/>
    </radialGradient>
    <radialGradient id="gC" cx="50%" cy="48%" r="68%">
      <stop offset="0%" stop-color="#4A5568"/>
      <stop offset="100%" stop-color="#2D3748"/>
    </radialGradient>
  </defs>"""

    # Linjer mellem alle cirkler — programmatisk genereret
    all_centers = [(500, 500)] + [(p[0], p[1]) for p in EGENSKAB_POSITIONS]
    line_pairs = []
    for i in range(len(all_centers)):
        for j in range(i + 1, len(all_centers)):
            line_pairs.append((all_centers[i], all_centers[j]))
    lines_xml = []
    for (a, b) in line_pairs:
        lines_xml.append(
            f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>'
        )
    lines = (
        '  <g stroke="#718096" stroke-width="1" stroke-linecap="round" '
        'stroke-dasharray="1.5 5" fill="none" opacity="0.5">\n'
        + "\n".join(lines_xml) + "\n"
        '  </g>'
    )

    # Cirkler — 7 outer + 1 center.
    # Radii er 5% større end template (101.43 → 106.50, 120 → 126).
    circles_lines = []
    for (cx, cy, gid, _color) in EGENSKAB_POSITIONS:
        circles_lines.append(
            f'  <circle cx="{cx}" cy="{cy}" r="106.50" fill="url(#{gid})"/>'
        )
    circles_lines.append(
        '  <circle cx="500" cy="500" r="126" fill="url(#gC)"/>'
    )
    circles = "\n".join(circles_lines)

    # Texts — grupperede efter farve
    def _xml_escape(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    dark_texts = []
    light_texts = []
    for (cx, cy, _gid, color), (_titel, l1, l2) in zip(EGENSKAB_POSITIONS, others):
        l1e, l2e = _xml_escape(l1), _xml_escape(l2)
        block = (
            f'      <text x="{cx}" y="{cy - 8}">{l1e}</text>\n'
            f'      <text x="{cx}" y="{cy + 18}">{l2e}</text>'
        )
        if color == "#2D3748":
            dark_texts.append(block)
        else:
            light_texts.append(block)

    cl1, cl2 = _xml_escape(center[1]), _xml_escape(center[2])
    center_text = (
        f'      <text x="500" y="488">{cl1}</text>\n'
        f'      <text x="500" y="518">{cl2}</text>'
    )

    texts = (
        '  <g font-style="italic" font-weight="500" text-anchor="middle" '
        'dominant-baseline="middle" letter-spacing="0.015em">\n'
        '    <g font-size="22" fill="#2D3748">\n'
        + "\n".join(dark_texts) + "\n"
        '    </g>\n'
        '    <g font-size="22" fill="#F7FAFC">\n'
        + "\n".join(light_texts) + "\n"
        '    </g>\n'
        '    <g font-size="26" fill="#F7FAFC">\n'
        + center_text + "\n"
        '    </g>\n'
        '  </g>'
    )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'style="font-family: \'TeX Gyre Pagella\', Palatino, serif;">\n'
        + defs + "\n\n"
        + lines + "\n\n"
        + circles + "\n\n"
        + texts + "\n"
        + '</svg>\n'
    )
    return svg


def egenskab_filnavn(idx: int) -> str:
    """Returnér filnavn for egenskab #idx (0-indexed via slug)."""
    slugs = [
        "egenskab-1-neutral-lytten",
        "egenskab-2-selvregulering",
        "egenskab-3-sansning-proces",
        "egenskab-4-taalmodighed",
        "egenskab-5-helhedens-prioritering",
        "egenskab-6-synkron-bevaegelse",
        "egenskab-7-kvalitet-beroering",
        "egenskab-8-sans-rytme",
    ]
    return slugs[idx]


def generer_egenskab_svgs():
    """Generer 8 SVG-filer i hero-motiver/, én pr. egenskab."""
    for idx in range(8):
        svg = _build_egenskab_svg(idx)
        sti = ROOT / HERO_DIR / (egenskab_filnavn(idx) + ".svg")
        sti.write_text(svg, encoding="utf-8")


def injicer_egenskab_figurer(body: str) -> str:
    """For hver egenskab-afsnit: clearpage + overskrift + centreret
    underoverskrift (fra EGENSKAB_SUBTITLES) + konstellations-figur.

    Egenskaber har ikke en kursiv-undertitel i kildematerialet — undertitlen
    skrives ind via EGENSKAB_SUBTITLES-dictionariet.
    """
    generer_egenskab_svgs()
    titel_til_idx = {p[0]: i for i, p in enumerate(EGENSKABER_FIGURER)}

    def replace(m):
        heading_line = m.group(1)
        titel = m.group(2).strip()
        if titel not in titel_til_idx:
            return m.group(0)
        idx = titel_til_idx[titel]
        svg_navn = egenskab_filnavn(idx) + ".svg"
        figur = hero_markdown(svg_navn, bredde_pct=66)
        sub_text = EGENSKAB_SUBTITLES.get(titel, "")
        sub_block = centreret_undertitel(sub_text) if sub_text else ""
        return clearpage_block() + heading_line + sub_block + figur

    pattern = re.compile(r'(^### ([^\n]+)\n)', re.MULTILINE)
    return pattern.sub(replace, body)


# ============================================================================
# STADIE-FIGURER (de 5 stadier i behandlerens indre rejse)
# ============================================================================
#
# Samme konstellations-stil som "Helheden Under Pres" (helhed-1-figur):
# 6 ydre cirkler i regulær hexagon + 1 mørk centrum-cirkel.
# Hver stadie har sin egen kerne-kvalitet i centrum og 6 omkringliggende
# kvaliteter destilleret fra kapitlets bold-koncepter.
# ============================================================================

# (titel, center_word, [outer-1..outer-6])
# Ydre kvaliteter starter klokken 12 og roterer med uret.
STADIER_FIGURER = [
    (
        "Det Første Stadie", "Søgen",
        ["Tankestøj", "Protokol", "Tvivl", "Fejlsøgning", "Anspændthed", "Kontrol"],
    ),
    (
        "Det Andet Stadie", "Pause",
        ["Mellemrum", "Intuition", "Empati", "Væskekrop", "Sensitivitet", "Lethed"],
    ),
    (
        "Det Tredje Stadie", "Felt",
        ["Resonans", "Regulering", "Synkroni", "Fælles rum", "Atmosfære", "Bro"],
    ),
    (
        "Det Fjerde Stadie", "Long Tide",
        ["Langsomhed", "Instinkt", "Tomhed", "Hjem", "Mysterie", "Stemme"],
    ),
    (
        "Det Femte Stadie", "Enhed",
        ["Blueprint", "Transmutation", "Skabelse", "Opløsning", "Nåde", "Drøm"],
    ),
]

# Samme hexagon-positioner som helhed-1-figur (regulær hexagon, radius 280
# omkring centrum 500,500). Klokken 12, 2, 4, 6, 8, 10.
# Format: (cx, cy, gradient_id, text_color)
STADIE_POSITIONS = [
    (500.00, 220.00, "g0", "#061D2B"),  # 12 — lys, mørk tekst
    (742.49, 360.00, "g1", "#061D2B"),  #  2 — lys, mørk tekst
    (742.49, 640.00, "g2", "#F5F2E9"),  #  4 — medium, lys tekst
    (500.00, 780.00, "g3", "#F5F2E9"),  #  6
    (257.51, 640.00, "g4", "#F5F2E9"),  #  8
    (257.51, 360.00, "g5", "#F5F2E9"),  # 10
]

# Linjer mellem alle hexagon-punkter — statisk
STADIE_LINES = """  <g stroke="#576570" stroke-width="1" stroke-linecap="round" stroke-dasharray="1.5 5" fill="none" opacity="0.55">
    <line x1="500" y1="220" x2="500" y2="500"/>
    <line x1="742.49" y1="360" x2="500" y2="500"/>
    <line x1="742.49" y1="640" x2="500" y2="500"/>
    <line x1="500" y1="780" x2="500" y2="500"/>
    <line x1="257.51" y1="640" x2="500" y2="500"/>
    <line x1="257.51" y1="360" x2="500" y2="500"/>

    <line x1="500" y1="220" x2="742.49" y2="360"/>
    <line x1="500" y1="220" x2="742.49" y2="640"/>
    <line x1="500" y1="220" x2="500" y2="780"/>
    <line x1="500" y1="220" x2="257.51" y2="640"/>
    <line x1="500" y1="220" x2="257.51" y2="360"/>
    <line x1="742.49" y1="360" x2="742.49" y2="640"/>
    <line x1="742.49" y1="360" x2="500" y2="780"/>
    <line x1="742.49" y1="360" x2="257.51" y2="640"/>
    <line x1="742.49" y1="360" x2="257.51" y2="360"/>
    <line x1="742.49" y1="640" x2="500" y2="780"/>
    <line x1="742.49" y1="640" x2="257.51" y2="640"/>
    <line x1="742.49" y1="640" x2="257.51" y2="360"/>
    <line x1="500" y1="780" x2="257.51" y2="640"/>
    <line x1="500" y1="780" x2="257.51" y2="360"/>
    <line x1="257.51" y1="640" x2="257.51" y2="360"/>
  </g>"""

# Gradient-defs delt af alle 5 stadier
STADIE_DEFS = """  <defs>
    <radialGradient id="g0" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#D6E4EB"/>
      <stop offset="100%" stop-color="#B7CBD6"/>
    </radialGradient>
    <radialGradient id="g1" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#A5BBC8"/>
      <stop offset="100%" stop-color="#89A3B1"/>
    </radialGradient>
    <radialGradient id="g2" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#7794A4"/>
      <stop offset="100%" stop-color="#587787"/>
    </radialGradient>
    <radialGradient id="g3" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#345261"/>
      <stop offset="100%" stop-color="#203C4A"/>
    </radialGradient>
    <radialGradient id="g4" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#1B3745"/>
      <stop offset="100%" stop-color="#0E2733"/>
    </radialGradient>
    <radialGradient id="g5" cx="50%" cy="48%" r="65%">
      <stop offset="0%" stop-color="#0B222D"/>
      <stop offset="100%" stop-color="#041620"/>
    </radialGradient>
    <radialGradient id="gC" cx="50%" cy="48%" r="68%">
      <stop offset="0%" stop-color="#020F17"/>
      <stop offset="100%" stop-color="#000408"/>
    </radialGradient>
  </defs>"""


def _build_stadie_svg(idx: int) -> str:
    """Byg én konstellations-SVG for stadie #idx (0-indexed)."""
    _titel, center_word, outer_words = STADIER_FIGURER[idx]

    # Cirkler — 6 ydre + 1 centrum
    circles_lines = []
    for (cx, cy, gid, _color) in STADIE_POSITIONS:
        circles_lines.append(
            f'  <circle cx="{cx}" cy="{cy}" r="80" fill="url(#{gid})"/>'
        )
    circles_lines.append(
        '  <circle cx="500" cy="500" r="100" fill="url(#gC)"/>'
    )
    circles = "\n".join(circles_lines)

    # Tekster grupperet efter farve
    dark_texts = []
    light_texts = []
    for (cx, cy, _gid, color), word in zip(STADIE_POSITIONS, outer_words):
        block = f'      <text x="{cx}" y="{cy + 2}">{word}</text>'
        if color == "#061D2B":
            dark_texts.append(block)
        else:
            light_texts.append(block)

    center_text = f'      <text x="500" y="500">{center_word}</text>'

    texts = (
        '  <g font-style="italic" font-weight="700" text-anchor="middle" '
        'dominant-baseline="middle" letter-spacing="0.015em">\n'
        '    <g font-size="22" fill="#061D2B">\n'
        + "\n".join(dark_texts) + "\n"
        '    </g>\n'
        '    <g font-size="22" fill="#F5F2E9">\n'
        + "\n".join(light_texts) + "\n"
        '    </g>\n'
        '    <g font-size="26" fill="#F5F2E9">\n'
        + center_text + "\n"
        '    </g>\n'
        '  </g>'
    )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'style="font-family: \'TeX Gyre Pagella\', Palatino, serif;">\n'
        + STADIE_DEFS + "\n\n"
        + STADIE_LINES + "\n\n"
        + circles + "\n\n"
        + texts + "\n"
        + '</svg>\n'
    )
    return svg


def stadie_filnavn(idx: int) -> str:
    """Returnér filnavn for stadie #idx (0-indexed)."""
    slugs = [
        "stadie-1-figur",
        "stadie-2-figur",
        "stadie-3-figur",
        "stadie-4-figur",
        "stadie-5-figur",
    ]
    return slugs[idx]


def generer_stadie_svgs():
    """Generer 5 SVG-filer i hero-motiver/, én pr. stadie."""
    for idx in range(5):
        svg = _build_stadie_svg(idx)
        sti = ROOT / HERO_DIR / (stadie_filnavn(idx) + ".svg")
        sti.write_text(svg, encoding="utf-8")


# Mapping fra zone-overskrift → hero-figur. Kan udvides med Rum B-E senere.
RUM_HERO_FIGURER = {
    "Rum A — Den Fysiske Krop": "rum-a-figur.svg",
    "Rum B — Væskekroppen": "rum-b-figur.svg",
    "Rum C — Det Relationelle Felt": "rum-c-figur.svg",
    "Rum D — The Long Tide / Primary Respiration": "rum-d-figur.svg",
    "Rum E — Dynamisk Stilhed": "rum-e-figur.svg",
}


def injicer_rum_figurer(body: str) -> str:
    """For hvert Rum X-afsnit: clearpage + overskrift + centreret kursiv
    intro + venn-figur.

    Body er heading-bumpet, så Rum-titler står som '### Rum A — ...' og
    følges af en kursiv intro-paragraf i kildematerialet.
    """
    def replace(m):
        heading_line = m.group(1)
        titel = m.group(2).strip()
        italic_text = m.group(3).replace('\n', ' ').strip()
        svg_navn = RUM_HERO_FIGURER.get(titel)
        if not svg_navn:
            return m.group(0)
        figur = hero_markdown(svg_navn, bredde_pct=85)
        return (
            clearpage_block()
            + heading_line
            + centreret_undertitel(italic_text)
            + figur
        )

    pattern = re.compile(
        r'(^### (Rum [A-E] — [^\n]+)\n)'
        r'\n+\*((?:[^*\n]|\n(?!\n))+?)\*\s*\n',
        re.MULTILINE,
    )
    return pattern.sub(replace, body)


# Mapping for "Helheden Under Pres" — fire grader af pres som
# konstellations-figurer. Hver overskrift får sin egen figur.
HELHED_HERO_FIGURER = {
    "Helheden lever":       "helhed-1-figur.svg",
    "Første forskydning":   "helhed-2-figur.svg",
    "Ubalancen breder sig": "helhed-3-figur.svg",
    "Det kroniske mønster": "helhed-4-figur.svg",
}


def injicer_helhed_figurer(body: str) -> str:
    """Indsæt konstellations-figur over hver matching '### Heading'.

    Body er heading-bumpet, så de fire afsnits-titler står som '### ...'.
    Fjerner samtidig den eksisterende inline ![](hero-motiver/helhed-*.svg)
    så bogen kun viser den nye konstellations-figur (de animerede SVG'er
    bevares til appen).
    """
    # Fjern de gamle inline-billeder først
    body = re.sub(
        r'^!\[[^\]]*\]\(hero-motiver/helhed-\d+-[^)]+\.svg\)\s*$\n?',
        '',
        body,
        flags=re.MULTILINE,
    )

    needspace = (
        "\n```{=latex}\n\\needspace{20\\baselineskip}\n```\n\n"
    )

    def replace(m):
        titel = m.group(1).strip()
        svg_navn = HELHED_HERO_FIGURER.get(titel)
        if not svg_navn:
            return m.group(0)
        figur = hero_markdown(svg_navn, bredde_pct=95)
        return needspace + figur + m.group(0)

    return re.sub(
        r'^### (.+?)$',
        replace,
        body,
        flags=re.MULTILINE,
    )


# Mapping for de 4 guidede øvelser. Kan udvides med #2-4 senere.
OEVELSE_HERO_FIGURER = {
    "1. At Opleve The Neutral": "oevelse-1-neutral-figur.svg",
    "2. Kroppens Egen Viden": "oevelse-2-kroppens-viden-figur.svg",
    "3. Kroppens Dynamiske Landskaber": "oevelse-3-dynamiske-landskaber-figur.svg",
    "4. Vejrtrækningen Som En Levende Proces": "oevelse-4-vejrtraekning-figur.svg",
}


def injicer_oevelse_figurer(body: str) -> str:
    """For hver øvelse: clearpage + overskrift + centreret kursiv-undertitel
    + figur.

    Hver øvelse i kildematerialet følges af en kursiv-undertitel
    (*— en guidet øvelse i ...*).
    """
    def replace(m):
        heading_line = m.group(1)
        titel = m.group(2).strip()
        italic_text = m.group(3).replace('\n', ' ').strip()
        svg_navn = OEVELSE_HERO_FIGURER.get(titel)
        if not svg_navn:
            return m.group(0)
        figur = hero_markdown(svg_navn, bredde_pct=95)
        return (
            clearpage_block()
            + heading_line
            + centreret_undertitel(italic_text)
            + figur
        )

    pattern = re.compile(
        r'(^### (\d+\. [^\n]+)\n)'
        r'\n+\*((?:[^*\n]|\n(?!\n))+?)\*\s*\n',
        re.MULTILINE,
    )
    return pattern.sub(replace, body)


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


def hero_circular_markdown(svg_navn: str, bredde_pct: int = 33,
                            viewport: tuple | None = None,
                            image_bredde_pct: int | None = None) -> str:
    """Cropper billedet til en cirkel.

    bredde_pct: cirklens diameter (i procent af \\textwidth).
    viewport: (llx, lly, urx, ury) i PDF-points — cropper PDF før clip.
    image_bredde_pct: billedets bredde (i procent af \\textwidth) — hvis
        sat større end bredde_pct, fylder billedet ud over cirkel-clipet
        så cirklen tydeligt skærer hjørnerne af.
    """
    if not svg_navn:
        return ""
    svg_sti = ROOT / HERO_DIR / svg_navn
    pdf_sti = svg_til_pdf(svg_sti)
    if not pdf_sti:
        return ""
    radius = bredde_pct / 200.0
    if image_bredde_pct is None:
        image_bredde_pct = bredde_pct
    img_bredde = image_bredde_pct / 100.0

    if viewport:
        vp_str = " ".join(str(v) for v in viewport)
        include = (
            f"\\includegraphics[viewport={vp_str}, clip, "
            f"width={img_bredde}\\textwidth]{{{pdf_sti.name}}}"
        )
    else:
        include = (
            f"\\includegraphics[width={img_bredde}\\textwidth]"
            f"{{{pdf_sti.name}}}"
        )

    # Brug TikZ's "path picture" — node med cirkel-form hvor billedet
    # automatisk cropes til formen. Dette virker pålideligt ift. \clip+\node
    # som ofte ikke clipper noden.
    diameter = radius * 2  # cirklens diameter som decimal
    return (
        "\n```{=latex}\n"
        "\\begin{center}\n"
        "\\begin{tikzpicture}\n"
        f"\\node[circle, minimum size={diameter}\\textwidth, "
        f"inner sep=0pt, draw=none, "
        f"path picture={{"
        f"\\node at (path picture bounding box.center) "
        f"{{{include}}};"
        f"}}] {{}};\n"
        "\\end{tikzpicture}\n"
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
    # Som før (firkantet illustration), bare 20% større (33 → 40)
    illustration = hero_markdown("refleksion-A-aabne-rum.svg", bredde_pct=48)

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


def transform_alle_sektioner_til_refleksion_kasser(content: str, level: int = 4) -> str:
    """Wrap hver sektion på det givne heading-niveau i en refleksions-kasse.

    Bruges til filer hvor ALT indhold er refleksioner (fx
    stadier-refleksioner), og hver overskrift skal blive til sin egen
    boks med tilhørende paragraffer.
    """
    illustration = hero_markdown("refleksion-A-aabne-rum.svg", bredde_pct=48)

    pattern = re.compile(rf'^(#{{{level}}})\s+(.+)$', re.MULTILINE)
    parts = pattern.split(content)
    pre = parts[0]  # alt før første heading på dette niveau

    boxes = []
    for k in range(1, len(parts), 3):
        title = parts[k + 1].strip() if k + 1 < len(parts) else ''
        body = parts[k + 2].strip() if k + 2 < len(parts) else ''
        if title and body:
            boxes.append(_make_refleksion_box(title, body, illustration))

    if not boxes:
        return content
    return pre + '\n\n'.join(boxes) + '\n'


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

    # Saml paragraffer med diamond mellem og needspace før hver, og en
    # afsluttende ruder efter sidste spørgsmål
    if paragraphs:
        body_parts = []
        for i, p in enumerate(paragraphs):
            if i > 0:
                body_parts.append(diamond)
            body_parts.append(needspace + p)
        body_parts.append(diamond)
        body_str = '\n'.join(body_parts)
    else:
        body_str = ''

    # Sideskift før OG efter — så boksen står alene + næste indhold starter frisk
    sideskift = "\n\n```{=latex}\n\\clearpage\n```\n\n"

    # Normalisér 'refleksion' → 'Refleksion' (stort R) i overskrifter som
    # 'Til refleksion'. Andre titler ('Den fælles kilde' osv.) er uændret.
    display_title = title.replace('Til refleksion', 'Til Refleksion')
    # Escape LaTeX special characters i titlen
    display_title = display_title.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')

    # Overskrift centreret med luftrum mellem illustration og overskrift
    heading = (
        "\n```{=latex}\n"
        "\\vspace{1em}\n"
        "\\begin{center}\n"
        f"\\textbf{{{display_title}}}\n"
        "\\end{center}\n"
        "\\vspace{0.4em}\n"
        "```\n\n"
    )

    return (
        f'{sideskift}'
        '\n::: refleksion\n'
        f'{illustration}'
        f'{heading}'
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

    # Special: ordliste — konvertér <details><summary>Ord</summary>...</details>
    # til '**Ord**\n\n...' så hvert beskrevne ord vises i fed.
    if filnavn == "ordliste":
        body = transform_ordliste_til_fed(body)

    # Andre Traditioner: split tradition-headings 'X — Y' til titel + centreret
    # underoverskrift, og indsæt underoverskrifter (fra dict) for specielle
    # temaer som kun har enkle titler.
    if filnavn == "andre-traditioner-og-specielle-temaer":
        body = split_heading_ved_streg(body, level=3)
        body = insaet_underoverskrifter_fra_dict(
            body, SPECIELLE_TEMAER_SUBTITLES, level=4,
        )

    # Special: i bestemte kapitler samles refleksions-subsections til én
    # boks. Fjern #### subheadings KUN inden for '### Til refleksion'-sektionen
    # (så øvrige sektioner med subsections bevarer deres struktur).
    if filnavn in {"i-behandlingssituationen", "helheden-under-pres",
                   "integration-i-din-praksis"}:
        m = re.search(r'^### Til [Rr]efleksion\b', body, re.MULTILINE)
        if m:
            start = m.end()
            next_m = re.search(r'^### ', body[start:], re.MULTILINE)
            end = start + next_m.start() if next_m else len(body)
            section = body[start:end]
            cleaned = re.sub(r'^####\s+.+$\n?', '', section, flags=re.MULTILINE)
            body = body[:start] + cleaned + body[end:]

    # Special: andre-traditioner — erstat hele refleksions-sektionen med 9
    # udvalgte spørgsmål (én pr. underafsnit + 2 fra åbnings-/afslutningstema)
    if filnavn == "andre-traditioner-og-specielle-temaer":
        m = re.search(r'^### Til [Rr]efleksion\b', body, re.MULTILINE)
        if m:
            start = m.start()
            next_m = re.search(r'^### ', body[m.end():], re.MULTILINE)
            end = m.end() + next_m.start() if next_m else len(body)
            ni_refleksioner = "\n".join([
                "### Til refleksion",
                "",
                "Hvordan genkender du den samme essens i forskellige traditioner — om det er tensegrity, TCM eller Jin Shin Jyutsu? Kan du se hvordan de alle arbejder med kroppens iboende visdom gennem forskellige indgange?",
                "",
                "Kan du arbejde med flere traditioner samtidigt uden at miste den biodynamiske essens — at de embryologiske kræfter ved hvordan processen skal udfoldes? Hvad kræver denne integration af dig?",
                "",
                "Hvordan arbejder du med forståelsen af at alt påvirker alt — at en låsning i foden kan skabe problemer i nakken? Kan du følge disse fascielle linjer som vitaliserende floder i væskekroppen?",
                "",
                "Hvordan integrerer du arbejdet med meridianer i den biodynamiske kontekst — kan du mærke hvordan de ekstraordinære meridianer har dyb forbindelse til de embryologiske kræfter? Hvad åbner denne kombination for?",
                "",
                "Hvordan har TCM's systemiske forståelse hjulpet dig til at se sammenhænge du ellers ville have overset? Kan du genkende når tilsyneladende urelaterede symptomer har fælles oprindelse?",
                "",
                "Har du oplevet den radikale forbedring når arvæv endelig transformeres — den pludselige frigivelse af bundet livskraft? Hvad fortæller dette dig om det fastlåste potentiale?",
                "",
                "Hvordan oplever du at simultant arbejde med flere systemer skaber kraftigere terapeutisk respons? Kan du mærke hvordan nervesystem, meridianer og fascielinjer naturligt finder resonans?",
                "",
                "Hvordan holder du den biodynamiske essens som centrum mens du tillader andre traditioner at bidrage? Kan du skelne mellem at låne teknikker og at integrere forståelse?",
                "",
                "Kan du se hvordan alle traditioner ultimativt peger mod samme sandhed — at kroppen kender vejen til heling? Hvordan bruger du denne fælles visdom uden at skabe forvirring?",
                "",
                "",
            ])
            body = body[:start] + ni_refleksioner + body[end:]

    # Special: andre-traditioner — indsæt sort ruder mellem hver tradition
    # og mellem hvert speciel-tema (efter refleksions-replacement, før
    # transform_refleksion_til_kasse så ruder ikke havner inde i boksen).
    if filnavn == "andre-traditioner-og-specielle-temaer":
        body = insaet_ruder_mellem_traditioner(body)

    # Til refleksion → fenced div (skal ske FØR perspektiv-figur-injection
    # så de ikke havner inde i refleksions-boksen)
    body = transform_refleksion_til_kasse(body)

    # Special-case: perspektiver — inject konstellations-figur før hver titel.
    # Sker efter både bumping og refleksions-transform — så figurerne
    # placeres rent oven over perspektiv-overskrifterne på level 3 (###).
    if filnavn == "de-syv-perspektiver":
        body = injicer_perspektiv_figurer(body)

    # Special-case: 8 essentielle egenskaber — samme princip
    if filnavn == "de-otte-essentielle-egenskaber":
        body = injicer_egenskab_figurer(body)

    # Special-case: De 5 Rum — venn-figur inject over Rum A's overskrift
    if filnavn == "de-fem-zoner":
        body = injicer_rum_figurer(body)

    # Special-case: De 4 Guidede Øvelser — figur inject over hver øvelse-titel
    if filnavn == "de-fire-guidede-oevelser":
        body = injicer_oevelse_figurer(body)

    # Special-case: Helheden Under Pres — fire konstellations-figurer over
    # hvert af de fire afsnit (Helheden lever, Første forskydning, ...)
    if filnavn == "helheden-under-pres":
        body = injicer_helhed_figurer(body)

    # Byg kapitel-overskrift
    titel = fm.get("titel", filnavn).strip()
    undertitel = fm.get("undertitel", "").strip()

    header = f"\n## Kapitel {kapitel_nr}: {titel}\n"
    if undertitel:
        header += centreret_undertitel(undertitel)

    # Hero-illustration (lige under kapitel-titel, før indhold) — max bredde
    hero_svg = CHAPTER_HERO.get(filnavn)
    hero = hero_markdown(hero_svg, bredde_pct=95) if hero_svg else ""

    # Daglige invitationer som afsluttende afsnit (hvis kapitel har en kategori)
    inv_kategori = INVITATIONER_KAPITEL_MAP.get(filnavn)
    invitationer = render_invitationer_for_kategori(inv_kategori, niveau=3) if inv_kategori else ""

    return header + "\n" + hero + body.strip() + "\n" + invitationer + "\n"


def centreret_undertitel(text: str) -> str:
    """Returnér markdown der renderes som centreret kursiv undertitel i både
    PDF (raw LaTeX) og DOCX (raw OpenXML).

    Pandoc dropper {=latex} for DOCX og {=openxml} for PDF, så hver format
    plukker den rette variant.
    """
    if not text:
        return ""
    text = text.strip()
    esc_xml = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (
        "\n```{=latex}\n"
        f"\\begin{{center}}\\itshape {text}\\end{{center}}\n"
        "```\n\n"
        "```{=openxml}\n"
        '<w:p><w:pPr><w:jc w:val="center"/>'
        '<w:spacing w:before="120" w:after="240"/></w:pPr>'
        f'<w:r><w:rPr><w:i/></w:rPr><w:t xml:space="preserve">{esc_xml}</w:t></w:r>'
        '</w:p>\n'
        "```\n\n"
    )


def clearpage_block() -> str:
    """Sideskift for både PDF og DOCX (\\clearpage). DOCX-konverteren
    transformerer \\clearpage til <w:br type=page/> via rule 3 — så vi
    emit'er KUN LaTeX-formen for at undgå dobbelt-emit (= tomme sider)."""
    return "\n```{=latex}\n\\clearpage\n```\n\n"


# Underoverskrifter til kapitler hvor de mangler i kildemateriale
EGENSKAB_SUBTITLES = {
    "1. Neutral lytten uden agenda":            "— at møde uden at vide hvad der skal ske",
    "2. Selvregulering af nervesystemet":       "— behandlerens iboende ankerpunkt",
    "3. Sansning af den terapeutiske proces":   "— at lytte til processens egen retning",
    "4. Tålmodighed & uvished":                 "— at hvile i det endnu ikke vidende",
    "5. At mærke helhedens prioritering":       "— at følge hvor systemet selv vil hen",
    "6. Synkron bevægelse med kroppen":         "— at være med, ikke imod",
    "7. Kvalitet i berøringen":                 "— fra søgende hænder til lyttende",
    "8. Sans for behandlingens rytme":          "— at fornemme hvornår noget begynder og slutter",
}

SPECIELLE_TEMAER_SUBTITLES = {
    "Arbejde med angst":                  "— at møde det der overvælder",
    "Arbejde med den døende":             "— at ledsage gennem den sidste tærskel",
    "Traumatiske tilstande":              "— den fastlåste energi der søger udløsning",
    "Arbejde med hjernerystelser":        "— det fine arbejde med hjernens hvælvinger",
    "Vagus":                              "— helhedens nerve, helingens broer",
    "Midtlinjen":                         "— kroppens første struktur og dybeste reference",
    "Åndedrættet":                        "— livets primære rytme",
    "Introduktion til arbejdet med børn": "— at møde den åbne, formgivende krop",
}


def split_heading_ved_streg(body: str, level: int = 3) -> str:
    """Konvertér '### X — Y' til '### X' + centreret undertitel('Y').

    Kun headings med præcis ét ' — ' (em-dash med mellemrum) splittes.
    """
    pattern = re.compile(
        rf'^(#{{{level}}}) ([^—\n]+?) — ([^\n]+)\s*$',
        re.MULTILINE,
    )
    def replace(m):
        prefix = m.group(1)
        title = m.group(2).strip()
        subtitle_text = m.group(3).strip()
        return f'{prefix} {title}\n' + centreret_undertitel(subtitle_text)
    return pattern.sub(replace, body)


def insaet_underoverskrifter_fra_dict(body: str, mapping: dict, level: int) -> str:
    """For hver overskrift på det givne niveau (3 eller 4) hvor titlen findes
    i mapping: indsæt centreret kursiv underoverskrift lige under.
    """
    pattern = re.compile(rf'^(#{{{level}}}) ([^\n]+?)\s*$', re.MULTILINE)
    def replace(m):
        title = m.group(2).strip()
        sub = mapping.get(title)
        if sub:
            return m.group(0) + '\n' + centreret_undertitel(sub)
        return m.group(0)
    return pattern.sub(replace, body)


def ruder_separator() -> str:
    """Lille sort ruder centreret med luft over og under — bruges som
    blød skiller mellem fx traditions-titler eller specielle-temaer."""
    return (
        "\n```{=latex}\n"
        "\\begin{center}\\vspace{0.4em}{\\large$\\blacklozenge$}\\vspace{0.4em}\\end{center}\n"
        "```\n\n"
        "```{=openxml}\n"
        '<w:p><w:pPr><w:jc w:val="center"/>'
        '<w:spacing w:before="200" w:after="200"/></w:pPr>'
        '<w:r><w:rPr><w:sz w:val="32"/></w:rPr><w:t>◆</w:t></w:r></w:p>\n'
        "```\n\n"
    )


def centrer_kursiv_underoverskrifter(body: str) -> str:
    """Find '### Heading\\n\\n*kursiv-paragraf*\\n' og erstat den kursive
    paragraf med centreret undertitel (raw LaTeX + raw OpenXML).

    Den kursive paragraf kan være én eller flere linjer, men må ikke
    indeholde tomme linjer (paragraf-pause).
    """
    pattern = re.compile(
        r'(^### [^\n]+\n)\n+'                          # heading + tomme linjer
        r'\*([^\n](?:[^*\n]|\n(?!\n))*?)\*'             # *kursiv*
        r'(?=\s*\n\n|\s*$)',                            # efterfulgt af blank linje eller slut
        re.MULTILINE,
    )

    def replace(m):
        heading = m.group(1)
        text = m.group(2).replace('\n', ' ').strip()
        return heading + centreret_undertitel(text)

    return pattern.sub(replace, body)


def insaet_ruder_mellem_traditioner(body: str) -> str:
    """For andre-traditioner: indsæt sort ruder mellem hver tradition (###)
    og mellem hvert speciel-tema (####). Springer over Intro, Specielle Temaer
    parent-heading, Til refleksion og Relationer.
    """
    diamond = ruder_separator()
    SKIP = ("Intro", "Specielle Temaer", "Til refleksion",
            "Til Refleksion", "Relationer")

    # Indsæt ruder før hver ### sektion (undtagen den første ikke-skip-sektion)
    h3 = list(re.finditer(r'^### (.+?)\s*$', body, re.MULTILINE))
    insert_at = []
    seen_first = False
    for m in h3:
        title = m.group(1).strip()
        if any(title.startswith(s) for s in SKIP):
            continue
        if seen_first:
            insert_at.append(m.start())
        seen_first = True
    for pos in reversed(insert_at):
        body = body[:pos] + diamond + body[pos:]

    # Indsæt ruder mellem #### sektioner (alle er specielle temaer i denne fil)
    h4 = list(re.finditer(r'^#### (.+?)\s*$', body, re.MULTILINE))
    insert_at = []
    seen_first = False
    for m in h4:
        if seen_first:
            insert_at.append(m.start())
        seen_first = True
    for pos in reversed(insert_at):
        body = body[:pos] + diamond + body[pos:]

    return body


def transform_ordliste_til_fed(body: str) -> str:
    """For ordliste.md: konvertér <details><summary>Ord</summary>def</details>
    til '**Ord**\\n\\ndef\\n'. Hvert beskrevne ord står herefter i fed.
    """
    return re.sub(
        r'<details>\s*<summary>(.+?)</summary>\s*(.*?)\s*</details>',
        lambda m: f'**{m.group(1).strip()}**\n\n{m.group(2).strip()}\n',
        body,
        flags=re.DOTALL,
    )


def strip_begreb_subsections(body: str) -> str:
    """For begreb-filer: behold kun #### Intro, #### Det grundlæggende og
    #### Til refleksion. Alle øvrige tema-subsektioners heading-linjer
    fjernes så body-teksten flyder ind under foregående sektion.
    """
    KEEP = {"Intro", "Det grundlæggende"}
    def keep_or_strip(m):
        title = m.group(1).strip()
        if title in KEEP or title.startswith("Til ") or title.startswith("Refleksioner "):
            return m.group(0)
        return ''
    return re.sub(r'^####\s+(.+?)\s*$\n?', keep_or_strip, body, flags=re.MULTILINE)


def render_samling(titel: str, undermappe: str, filnavne: list,
                   kapitel_nr: int) -> str:
    """Render en samling af filer som ét kapitel med ###-underafsnit."""
    # Special-case: stadier — generer de 5 konstellations-figurer på forhånd
    # så SUBSECTION_HERO kan finde dem.
    if undermappe == "stadier":
        generer_stadie_svgs()

    out = [f"\n## Kapitel {kapitel_nr}: {titel}\n"]

    # Hero ved samlingens start
    samling_hero_svg = SAMLING_HERO.get(undermappe)
    if samling_hero_svg:
        # Alle samling-heroes renderes i max bredde
        out.append(hero_markdown(samling_hero_svg, bredde_pct=95))

    for entry_idx, filnavn in enumerate(filnavne):
        # Hver underafsnit (stadie/begreb) starter på frisk side. Den første
        # entry følger samling-headeren naturligt og får ikke clearpage.
        if entry_idx > 0:
            out.append(clearpage_block())

        path = CONTENT / undermappe / f"{filnavn}.md"
        if not path.exists():
            out.append(f"\n### {filnavn} (mangler)\n")
            continue

        fm, body = laes_md(path)
        body = strip_relationer(body)
        body = strip_html_illustrations(body)
        # Special: stadie-filer (01-05) — strip 'Til refleksion'-sektion i bogen
        # (refleksionerne er konsolideret til én boks under Den Levende Spiral).
        if undermappe == "stadier" and filnavn in {
            "01-foerste-stadie", "02-andet-stadie", "03-tredje-stadie",
            "04-fjerde-stadie", "05-femte-stadie"
        }:
            body = re.sub(r'^## Til [Rr]efleksion\s*$.*?(?=^## |\Z)',
                          '', body, flags=re.MULTILINE | re.DOTALL)

        # Bump 2 levels: ## → ####, så samlingens entries er ### og deres sektioner ####
        body = bump_headings(body, 2)

        # Special: begreber — behold kun Intro og Det grundlæggende
        # (alle øvrige tema-subsektioner får fjernet deres heading-linjer)
        if undermappe == "begreber":
            body = strip_begreb_subsections(body)

        body = transform_refleksion_til_kasse(body)

        # Special: hele filer med kun refleksioner (fx 07-stadier-refleksioner)
        # — kun Den Levende Spiral som ÉN refleksions-boks med 5 spørgsmål.
        # Stadie 1-5 refleksioner droppes (de er allerede dækket af den-levende-spiral-teksten).
        if filnavn == "07-stadier-refleksioner":
            body = (
                "#### Den Levende Spiral — Rejsen som Helhed\n\n"
                "De fem stadier er ikke trin på en stige men en levende spiral hvor vi konstant bevæger os mellem forskellige dybder og kvaliteter.\n\n"
                "Hvordan oplever du at bære elementer af alle fem stadier samtidigt — begynderens uro sammen med dybere visdom? Kan du rumme hele spektret uden at dømme nogle dele som bedre end andre?\n\n"
                "Når du ser tilbage på din udvikling, kan du se hvordan hvert stadie bragte præcis de gaver og udfordringer du behøvede? Hvad fortæller dette dig om processens egen intelligens?\n\n"
                "Når du efter års praksis pludselig befinder dig i begynderens uro, kan du møde dette som spiralens natur snarere end tilbagefald? Hvad åbnes der i dig, når du genkender at du genbesøger første stadie med dybere forståelse?\n\n"
                "Hvordan oplever du tredje stadies funktion som vital bro mellem det personlige og det universelle? Kan du mærke hvordan dine nærmeste relationer er træningsfeltet, der forbereder dig til de større felter gennem The Long Tide?\n\n"
                "Hvordan forholder du dig til at udviklingen ikke kan forceres — at den udfolder sig i sin egen rytme styret af de samme embryologiske kræfter du arbejder med? Kan du stole på at din udvikling følger sin egen perfekte timing?\n"
            )
            body = transform_alle_sektioner_til_refleksion_kasser(body, level=4)

        del_titel = fm.get("titel", filnavn).strip()
        del_undertitel = fm.get("undertitel", "").strip()

        # 07-stadier-refleksioner droppes som section — kun refleksions-boksen
        if filnavn != "07-stadier-refleksioner":
            out.append(f"\n### {del_titel}")
            if del_undertitel:
                out.append(centreret_undertitel(del_undertitel))

        # Hero pr. underafsnit (ikke for refleksions-filer — illustrationen
        # ligger inde i hver boks). Begreb-figurerne renderes dobbelt så
        # store som de øvrige underafsnits-figurer.
        sub_hero_svg = SUBSECTION_HERO.get(filnavn)
        if sub_hero_svg and filnavn != "07-stadier-refleksioner":
            sub_bredde = 95 if undermappe in {"begreber", "stadier"} else 54
            out.append(hero_markdown(sub_hero_svg, bredde_pct=sub_bredde))

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


# ============================================================================
# DAGLIGE INVITATIONER — én oval-side efter hvert kapitel
# ============================================================================
#
# Efter hvert kapitel placeres en helsides figur med én oval indeholdende én
# daglig invitation (titel, evokation, invitation). Kapitlerne roterer
# gennem de seks kategorier (princip, blechschmidt, perspektiv, egenskab,
# zone, stadie) i round-robin — så hver kategori bruges mindst 2 gange
# (15 kapitler / 6 kategorier → 3 kategorier får 3 invitationer, 3 får 2).
# Inden for hver kategori vælges mikroteksterne sekventielt, så ingen
# invitation gentages.
# ============================================================================

KATEGORI_ORDEN = ["princip", "blechschmidt", "perspektiv", "egenskab", "zone", "stadie"]


def _kapitel_kategori_indeks(kapitel_nr: int) -> int:
    """Returnér kategori-indeks (0-5) for et kapitel — round-robin."""
    return (kapitel_nr - 1) % 6


def _vaelg_invitation_for_kapitel(kapitel_nr: int) -> dict:
    """Vælg én mikrotekst for et givet kapitel.

    Inden for hver kategori bruges mikroteksterne sekventielt — den k'te gang
    en kategori bruges, vælges k'te mikrotekst (modulo antal i kategorien).
    """
    teksters = hent_mikrotekster()
    by_cat: dict[str, list[dict]] = {cat: [] for cat in KATEGORI_ORDEN}
    for t in teksters:
        cat = t.get("kategori")
        if cat in by_cat:
            by_cat[cat].append(t)

    # Tæl hvor mange gange den valgte kategori er brugt før dette kapitel
    cat = KATEGORI_ORDEN[_kapitel_kategori_indeks(kapitel_nr)]
    use_count = sum(
        1 for n in range(1, kapitel_nr)
        if _kapitel_kategori_indeks(n) == _kapitel_kategori_indeks(kapitel_nr)
    )
    idx = use_count % len(by_cat[cat])
    return by_cat[cat][idx]


# Layout-konstanter for én oval. Matcher den frittstående oval brugt i chat
# (viewBox 1100×700, ellipse cx=550 cy=350 rx=520 ry=240).
_OVAL_F_TITLE = 32
_OVAL_F_BODY = 22
_OVAL_LH_TITLE = 42
_OVAL_LH_BODY = 30
_OVAL_GAP_TITLE_EVOK = 25
_OVAL_GAP_EVOK_INV = 60
_OVAL_WRAP = 58


def _xml_escape_text(s: str) -> str:
    return (s.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;")
              .replace('"', "&quot;"))


def _byg_oval_indhold(cx: int, cy: int, rx: int, ry: int, t: dict) -> str:
    """Byg én oval (ellipse + tekst) som SVG-fragment, centreret omkring cy."""
    title = t.get("navn", "")
    evokation = t.get("evokation", "")
    invitation = t.get("invitation", "")

    ev_lines = textwrap.wrap(evokation, _OVAL_WRAP, break_long_words=False) or [""]
    iv_lines = textwrap.wrap(invitation, _OVAL_WRAP, break_long_words=False) or [""]

    block_h = (_OVAL_LH_TITLE + _OVAL_GAP_TITLE_EVOK
               + len(ev_lines) * _OVAL_LH_BODY
               + _OVAL_GAP_EVOK_INV
               + len(iv_lines) * _OVAL_LH_BODY)
    top = cy - block_h / 2

    parts = [f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#3F4A5C"/>']
    parts.append(
        '  <g fill="#F5F2E9" text-anchor="middle" dominant-baseline="middle" '
        'font-style="italic" letter-spacing="0.015em">'
    )
    title_y = top + _OVAL_LH_TITLE / 2
    parts.append(
        f'    <text x="{cx}" y="{title_y:.1f}" font-size="{_OVAL_F_TITLE}" '
        f'font-weight="700">{_xml_escape_text(title)}</text>'
    )

    y0_e = top + _OVAL_LH_TITLE + _OVAL_GAP_TITLE_EVOK + _OVAL_LH_BODY / 2
    for i, ln in enumerate(ev_lines):
        parts.append(
            f'    <text x="{cx}" y="{y0_e + i*_OVAL_LH_BODY:.1f}" '
            f'font-size="{_OVAL_F_BODY}" font-weight="500">{_xml_escape_text(ln)}</text>'
        )

    y0_i = (top + _OVAL_LH_TITLE + _OVAL_GAP_TITLE_EVOK
            + len(ev_lines) * _OVAL_LH_BODY
            + _OVAL_GAP_EVOK_INV + _OVAL_LH_BODY / 2)
    for i, ln in enumerate(iv_lines):
        parts.append(
            f'    <text x="{cx}" y="{y0_i + i*_OVAL_LH_BODY:.1f}" '
            f'font-size="{_OVAL_F_BODY}" font-weight="500">{_xml_escape_text(ln)}</text>'
        )

    parts.append('  </g>')
    return "\n".join(parts)


def byg_invitations_side_svg(invitation: dict) -> str:
    """Én oval på en landscape-canvas (1100×700).

    Når billedet rendres i bogen ved 95% bredde og vertikalt centreres med
    \\null\\vfill, flyder ovalen serenisk midt på siden med rigeligt luft
    over og under.
    """
    cx, cy, rx, ry = 550, 350, 520, 240
    inner = _byg_oval_indhold(cx, cy, rx, ry, invitation)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 700" '
        'style="font-family: \'TeX Gyre Pagella\', Palatino, serif;">\n'
        '  <rect width="1100" height="700" fill="#ffffff"/>\n'
        + inner + "\n"
        + '</svg>\n'
    )


def render_invitations_side(kapitel_nr: int) -> str:
    """Returnér markdown for en helsides oval-side efter et kapitel."""
    invitation = _vaelg_invitation_for_kapitel(kapitel_nr)
    svg = byg_invitations_side_svg(invitation)

    # Skriv SVG til figures/ — graphicspath inkluderer den, og PDF/PNG cacher der
    sti = FIGURES_DIR / f"_invitationer-kap-{kapitel_nr:02d}.svg"
    sti.write_text(svg, encoding="utf-8")

    pdf_sti = svg_til_pdf(sti)
    if not pdf_sti:
        return ""
    # Forhånds-generér PNG til DOCX-pipeline
    svg_til_png(sti)

    # Én sammenhængende raw-LaTeX-blok så pandoc ikke indsætter parskip-glue
    # mellem elementerne — det er afgørende for at \vfill faktisk centrerer
    # billedet på siden. erstat_includegraphics i konverter_til_docx_md()
    # bruger en regex der matcher \\includegraphics inden i blokken.
    return (
        "\n```{=latex}\n"
        "\\clearpage\n"
        "\\thispagestyle{empty}\n"
        "\\null\\vfill\n"
        "\\begin{center}\n"
        f"\\includegraphics[width=0.95\\textwidth]{{{pdf_sti.name}}}\n"
        "\\end{center}\n"
        "\\vfill\\null\n"
        "\\clearpage\n"
        "```\n\n"
    )


# ============================================================================
# PART-SIDER — egne sider med PART I/II/III/IV, titel, beskrivelse, ruder
# ============================================================================

_PART_ROMAN = ["I", "II", "III", "IV", "V", "VI"]


def render_part_page(part_nr: int, titel: str, beskrivelse: str) -> str:
    """Helsides part-side med 'PART N', titel, kort beskrivelse, ruder.

    Emit'er to raw blokke side-om-side: én {=latex} til PDF og én {=openxml}
    til DOCX. Pandoc kasserer den ikke-relevante variant for hvert format.
    """
    roman = _PART_ROMAN[part_nr - 1]
    # Escape underscore osv. til LaTeX (titler er simple, men beskrivelser
    # kan have specialtegn). For nu — alle vores titler er rene ord.

    latex = (
        "\n```{=latex}\n"
        "\\clearpage\n"
        "\\thispagestyle{empty}\n"
        "\\null\\vfill\n"
        "\\begin{center}\n"
        f"  {{\\Large\\scshape Part {roman}}}\\\\[2.4em]\n"
        f"  {{\\Huge\\bfseries {titel}}}\\\\[2.4em]\n"
        "  \\begin{minipage}{0.72\\textwidth}\n"
        f"    \\centering\\itshape\\normalsize {beskrivelse}\n"
        "  \\end{minipage}\\\\[2.4em]\n"
        "  {\\Large $\\blacklozenge$}\n"
        "\\end{center}\n"
        "\\vfill\\null\n"
        f"\\addcontentsline{{toc}}{{part}}{{Part {roman} — {titel}}}\n"
        "\\clearpage\n"
        "```\n\n"
    )

    # OpenXML til DOCX: page break, PART N, titel, beskrivelse, ruder, page break.
    # Bruger Heading1 style så TOC samler det op.
    def esc(s: str) -> str:
        return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    openxml = (
        "```{=openxml}\n"
        # Page break før
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
        # Stort tomt rum øverst
        '<w:p><w:pPr><w:spacing w:before="2400"/></w:pPr></w:p>\n'
        # PART N (centreret, små kapitæler, mellemstor)
        '<w:p><w:pPr><w:jc w:val="center"/>'
        '<w:spacing w:before="0" w:after="480"/></w:pPr>'
        '<w:r><w:rPr><w:smallCaps/><w:sz w:val="40"/>'
        '<w:color w:val="2D3748"/></w:rPr>'
        f'<w:t xml:space="preserve">Part {roman}</w:t></w:r></w:p>\n'
        # Titel (Heading1 så TOC samler op, men vi tilsidesætter med run-styling)
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/>'
        '<w:jc w:val="center"/>'
        '<w:spacing w:before="0" w:after="600"/></w:pPr>'
        '<w:r><w:rPr><w:b/><w:sz w:val="72"/>'
        '<w:color w:val="2D3748"/></w:rPr>'
        f'<w:t xml:space="preserve">{esc(titel)}</w:t></w:r></w:p>\n'
        # Beskrivelse (italic, indent på begge sider for ~70% bredde)
        '<w:p><w:pPr><w:jc w:val="center"/>'
        '<w:ind w:left="1700" w:right="1700"/>'
        '<w:spacing w:before="0" w:after="600"/></w:pPr>'
        '<w:r><w:rPr><w:i/><w:sz w:val="22"/>'
        '<w:color w:val="2D3748"/></w:rPr>'
        f'<w:t xml:space="preserve">{esc(beskrivelse)}</w:t></w:r></w:p>\n'
        # Ruder
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:rPr><w:sz w:val="36"/>'
        '<w:color w:val="2D3748"/></w:rPr><w:t>◆</w:t></w:r></w:p>\n'
        # Page break efter
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
        "```\n\n"
    )

    return latex + openxml


def render_litteraturliste() -> str:
    """Litteraturliste over inspirations-kilder bag bogen."""
    return dedent("""
        # Litteraturliste

        ### James Jealous, D.O.

        - **Audio Lectures** — © 2000-2025 Marnee Jealous Long – All Rights Reserved
        - **Healing and the Natural World** (1997)

        ### William Garner Sutherland, D.O.

        - **The Cranial Bowl** (1939)
        - **Teachings in the Science of Osteopathy** (redigeret af Anne L. Wales, 1990, posthumt udgivet)
        - **Contributions of Thought: The Collected Writings of William Garner Sutherland, D.O.** (redigeret af Adah Strand Sutherland og Anne L. Wales, 1967, 1971)

        ### Erich Blechschmidt, M.D.

        - **The Beginnings of Human Life** (1977) — Springer-Verlag
        - **The Ontogenetic Basis of Human Anatomy: A Biodynamic Approach to Development from Conception to Birth** (2004, posthumt udgivet, redigeret af Brian Freeman) — North Atlantic Books
        - **Biokinetics and Biodynamics of Human Differentiation** (med R.F. Gasser, 1978/2012) — North Atlantic Books

        ### Rollin E. Becker, D.O.

        - **Life in Motion: The Osteopathic Vision of Rollin E. Becker, D.O.** (1997, redigeret af Rachel E. Brooks, M.D.) — Stillness Press
        - **The Stillness of Life: The Osteopathic Philosophy of Rollin E. Becker, D.O.** (2000, redigeret af Rachel E. Brooks, M.D.) — Stillness Press

        ### Robert Fulford, D.O.

        - **Dr. Fulford's Touch of Life: The Healing Power of the Natural Life Force** (1996, med Gene Stone) — Pocket Books

        ### Charles Ridley, D.A.

        - **Stillness: Biodynamic Cranial Practice and the Evolution of Consciousness** (2006) — North Atlantic Books

        ### Michael Kern, D.O., R.C.S.T.

        - **Wisdom in the Body: The Craniosacral Approach to Essential Health** (1999, revideret 2005) — North Atlantic Books

        ### Franklyn Sills, R.C.S.T.

        - **Craniosacral Biodynamics, Volume One: The Breath of Life, Biodynamics, and Fundamental Skills** (2001) — North Atlantic Books
        - **Craniosacral Biodynamics, Volume Two: The Primal Midline and the Organization of the Body** (2004) — North Atlantic Books
        - **Foundations in Craniosacral Biodynamics, Volume One: The Breath of Life and Fundamental Skills** (2011) — North Atlantic Books
        - **Foundations in Craniosacral Biodynamics, Volume Two: The Sentient Embryo, Tissue Intelligence, and Trauma Resolution** (2012) — North Atlantic Books

        ### Michael Shea, Ph.D.

        - **Biodynamic Craniosacral Therapy, Volume One** (2007) — North Atlantic Books
        - **Biodynamic Craniosacral Therapy, Volume Two** (2008) — North Atlantic Books

        ### Francisco Varela

        - **The Embodied Mind: Cognitive Science and Human Experience** (1991, med Evan Thompson og Eleanor Rosch) — MIT Press
        - **The Tree of Knowledge: The Biological Roots of Human Understanding** (1987, med Humberto Maturana) — Shambhala

        ### Stephen Porges, Ph.D.

        - **The Polyvagal Theory: Neurophysiological Foundations of Emotions, Attachment, Communication, and Self-Regulation** (2011) — W.W. Norton
        - **The Pocket Guide to the Polyvagal Theory: The Transformative Power of Feeling Safe** (2017) — W.W. Norton

        ### Peter Levine, Ph.D.

        - **Waking the Tiger: Healing Trauma** (1997) — North Atlantic Books
        - **In an Unspoken Voice: How the Body Releases Trauma and Restores Goodness** (2010) — North Atlantic Books
        - **Trauma and Memory: Brain and Body in a Search for the Living Past** (2015) — North Atlantic Books

        ### Thomas Hübl

        - **Healing Collective Trauma: A Process for Integrating Our Intergenerational and Cultural Wounds** (2020) — Sounds True
        - **Attuned: Practicing Interdependence to Heal Our Trauma—and Our World** (2023) — Sounds True

        ### Andrew Taylor Still, M.D., D.O.

        - **Autobiography of Andrew Taylor Still** (1897, genudgivet mange gange)
        - **The Philosophy and Mechanical Principles of Osteopathy** (1902)
        - **Osteopathy: Research and Practice** (1910)
        - **Philosophy of Osteopathy** (1899)

        ### Alain Gehin, D.O.

        - **The Atlas of Manipulative Techniques for the Cranium and the Face** (2007, med François Ricard) — Elsevier
        - **Cranial Osteopathic Biomechanics, Pathomechanics and Diagnostics for Practitioners** (2007) — Churchill Livingstone

        ### Thomas Myers

        - **Anatomy Trains: Myofascial Meridians for Manual and Movement Therapists** (1st edition 2001, 4th edition 2020) — Elsevier
        - **BodyReading: Visual Assessment and the Anatomy Trains** (2010) — DVDs og undervisningsmateriale

        ### Giovanni Maciocia

        - **The Foundations of Chinese Medicine: A Comprehensive Text** (1st edition 1989, 3rd edition 2015) — Elsevier
        - **The Practice of Chinese Medicine** (1st edition 1994, 2nd edition 2007) — Churchill Livingstone
        - **The Psyche in Chinese Medicine** (2009) — Churchill Livingstone

        ### Jin Shin Jyutsu

        - Mary Burmeister — bragte Jin Shin Jyutsu til Vesten
            - **Jin Shin Jyutsu: Getting to Know (Help) Myself** (1985) — selvudgivet
            - **Introducing Jin Shin Jyutsu Is** (Books 1-3) — selvudgivet
        - Alice Burmeister & Tom Monte
            - **The Touch of Healing: Energizing the Body, Mind, and Spirit with Jin Shin Jyutsu** (1997) — Bantam Books

        ### The Web That Has No Weaver

        - Ted J. Kaptchuk, O.M.D.
            - **The Web That Has No Weaver: Understanding Chinese Medicine** (1st edition 1983, 2nd edition 2000) — McGraw-Hill

        ### Robert Schleip, Ph.D.

        - **Fascia: The Tensional Network of the Human Body** (2012, 2nd edition 2021, redigeret med Thomas Findley, Leon Chaitow, Peter Huijing) — Elsevier
        - **Fascia in Sport and Movement** (2015, 2nd edition 2021) — Handspring Publishing

        ### Jean-Pierre Barral, D.O.

        - **Visceral Manipulation** (1988, med Pierre Mercier) — Eastland Press
        - **Manual Thermal Evaluation** (2005) — North Atlantic Books
        - **The Thorax** (1991) — Eastland Press

        ### James L. Oschman, Ph.D.

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
    # Hero-illustration lige under titel
    hero = hero_markdown("forord-figur.svg", bredde_pct=95)
    if hero:
        out.append(hero)
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
        toc-depth: 0
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

    # Dele og kapitler — hver del får sin egen part-side med titel,
    # kort beskrivelse og ruder; kapitler følger på efterfølgende sider.
    kapitel_nr = 1
    for part_idx, (part_titel, part_beskrivelse, kapitler) in enumerate(DELE):
        out.append(render_part_page(part_idx + 1, part_titel, part_beskrivelse))
        for spec in kapitler:
            out.append(render_kapitel(spec, kapitel_nr))
            # Helsides oval-side med én daglig invitation efter hvert kapitel
            out.append(render_invitations_side(kapitel_nr))
            kapitel_nr += 1

    # Bagstof: kun Litteraturliste (det tidligere appendiks med 120
    # daglige invitationer er fjernet — invitationerne fordeles nu som
    # trio-sider efter hvert kapitel)
    out.append(render_litteraturliste())

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
        \usepackage{{titlesec}}
        {graphicspath}

        % Centrér kapitel-, sektion- og subsektion-overskrifter.
        % Tomme labels {{}} fjerner auto-prefiks (vi har 'Kapitel N:' i selve
        % titlen via markdown og vil ikke have et ekstra 'Chapter N' ovenover).
        \titleformat{{\chapter}}[block]
          {{\normalfont\Huge\bfseries\centering}}{{}}{{0pt}}{{}}
        \titlespacing*{{\chapter}}{{0pt}}{{40pt}}{{30pt}}
        \titleformat{{\section}}[block]
          {{\normalfont\Large\bfseries\centering}}{{}}{{0pt}}{{}}
        \titlespacing*{{\section}}{{0pt}}{{20pt}}{{12pt}}
        \titleformat{{\subsection}}[block]
          {{\normalfont\large\bfseries\centering}}{{}}{{0pt}}{{}}
        \titlespacing*{{\subsection}}{{0pt}}{{16pt}}{{8pt}}
        % Refleksions-boks: lys blå-slate fra samme palet som Potency,
        % men med klar blå chroma bevaret (ingen mix med hvid — Potency
        % er grå-leanende og bliver helt grå når den fortyndes)
        \definecolor{{refleksioncenter}}{{HTML}}{{B7CBD6}}
        \definecolor{{refleksionedge}}{{HTML}}{{A5BBC8}}
        \newtcolorbox{{refleksionbox}}{{
          enhanced,
          interior style={{
            shading=radial,
            inner color=refleksioncenter,
            outer color=refleksionedge,
          }},
          frame hidden,
          arc=8pt,
          breakable,
          left=10pt,
          right=10pt,
          top=8pt,
          bottom=8pt
        }}

        % TOC-dybde: kun parts og kapitler — ingen sektioner/subsektioner
        \setcounter{{tocdepth}}{{0}}

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
    elif fmt == "docx":
        # DOCX: skip lua-filter (LaTeX-only).
        # --toc-depth=2 sikrer at TOC kun viser parts og kapitler — ikke
        # forfattere, sub-begreber, individuelle invitationer osv.
        cmd = ["pandoc", str(md_path), "-o", str(out_path),
               "--top-level-division=part",
               "--toc",
               "--toc-depth=2",
               "--resource-path", str(FIGURES_DIR)]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"PANDOC FEJL ({fmt}):", r.stderr[-2000:], file=sys.stderr)
            return False

        # DOCX post-processing: pandoc respekterer ikke fig-align="center"
        # i markdown for DOCX. Vi modificerer document.xml direkte:
        # 1. Centrér alle paragraffer der indeholder et billede
        # 2. Tilføj synlig boks (border + shading) omkring refleksions-paragraffer
        if fmt == "docx":
            post_process_docx(out_path)

        return True
    except subprocess.TimeoutExpired:
        print(f"PANDOC TIMEOUT ({fmt})", file=sys.stderr)
        return False


def post_process_docx(docx_path):
    """Modify document.xml efter pandoc har skabt docx'en."""
    import zipfile, re
    from pathlib import Path as P

    docx_path = P(docx_path)
    with zipfile.ZipFile(docx_path, 'r') as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    doc_xml = files['word/document.xml'].decode('utf-8')

    # 1. Centrér alle paragraffer der indeholder <w:drawing>
    def center_image_paragraphs(xml: str) -> str:
        result = []
        pos = 0
        while True:
            p_start = xml.find('<w:p', pos)
            if p_start == -1:
                result.append(xml[pos:])
                break
            tag_end_lt = xml.find('>', p_start)
            if tag_end_lt == -1:
                result.append(xml[pos:])
                break
            p_end = xml.find('</w:p>', tag_end_lt)
            if p_end == -1:
                result.append(xml[pos:])
                break
            p_end += len('</w:p>')

            paragraph = xml[p_start:p_end]
            result.append(xml[pos:p_start])

            if '<w:drawing>' in paragraph:
                if '<w:pPr>' in paragraph and '<w:jc ' not in paragraph:
                    paragraph = paragraph.replace(
                        '<w:pPr>', '<w:pPr><w:jc w:val="center"/>', 1
                    )
                elif '<w:pPr>' not in paragraph:
                    open_tag_end = paragraph.find('>') + 1
                    paragraph = (paragraph[:open_tag_end]
                                 + '<w:pPr><w:jc w:val="center"/></w:pPr>'
                                 + paragraph[open_tag_end:])

            result.append(paragraph)
            pos = p_end

        return ''.join(result)

    doc_xml = center_image_paragraphs(doc_xml)

    # 2. Refleksionsbokse: centrér og sæt synlig boks (kant + lyseblå
    # baggrund) om alle paragraffer fra refleksion-illustration til næste
    # sideskift. Word fletter automatisk konsekutive paragraffer med ens
    # border+shading til én sammenhængende boks.
    PBDR_REFLEKSION = (
        '<w:pBdr>'
        '<w:top w:val="single" w:sz="6" w:space="1" w:color="A5BBC8"/>'
        '<w:left w:val="single" w:sz="6" w:space="4" w:color="A5BBC8"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="1" w:color="A5BBC8"/>'
        '<w:right w:val="single" w:sz="6" w:space="4" w:color="A5BBC8"/>'
        '</w:pBdr>'
    )
    SHD_REFLEKSION = '<w:shd w:val="clear" w:color="auto" w:fill="B7CBD6"/>'

    def style_refleksion_blocks(xml: str) -> str:
        result = []
        pos = 0
        inside = False
        while True:
            p_start = xml.find('<w:p', pos)
            if p_start == -1:
                result.append(xml[pos:])
                break
            tag_end = xml.find('>', p_start) + 1
            p_end = xml.find('</w:p>', tag_end)
            if p_end == -1:
                result.append(xml[pos:])
                break
            p_end += len('</w:p>')

            paragraph = xml[p_start:p_end]
            result.append(xml[pos:p_start])

            illustration_para = 'refleksion-A-aabne-rum' in paragraph

            # Indsæt padding-paragraf med boks-styling FØR illustrationen,
            # så der er luft (med boksens baggrundsfarve) over den.
            if illustration_para and not inside:
                padding_p = (
                    '<w:p><w:pPr>'
                    + PBDR_REFLEKSION + SHD_REFLEKSION
                    + '<w:jc w:val="center"/>'
                    + '<w:spacing w:before="0" w:after="0"/>'
                    + '</w:pPr></w:p>'
                )
                result.append(padding_p)

            if illustration_para:
                inside = True

            had_pagebreak = 'w:type="page"' in paragraph

            # Anvend boks-styling på alle refleksions-paragraffer (undtagen
            # selve sideskift-paragraffen som markerer afslutningen).
            if inside and not had_pagebreak:
                # 1. Centrer (jc) — tilføj efter pStyle eller sidst i pPr
                if '<w:jc ' not in paragraph:
                    if '<w:pPr>' in paragraph:
                        paragraph = paragraph.replace(
                            '<w:pPr>', '<w:pPr><w:jc w:val="center"/>', 1
                        )
                    else:
                        open_tag_end = paragraph.find('>') + 1
                        paragraph = (paragraph[:open_tag_end]
                                     + '<w:pPr><w:jc w:val="center"/></w:pPr>'
                                     + paragraph[open_tag_end:])

                # 2. Border + shading — indsat før jc for at overholde
                # OOXML-skemaets pPr-element-rækkefølge (pBdr/shd før jc).
                box_xml = PBDR_REFLEKSION + SHD_REFLEKSION
                if '<w:jc ' in paragraph:
                    paragraph = paragraph.replace('<w:jc ', box_xml + '<w:jc ', 1)
                elif '<w:pPr>' in paragraph:
                    paragraph = paragraph.replace(
                        '<w:pPr>', '<w:pPr>' + box_xml, 1
                    )
                else:
                    open_tag_end = paragraph.find('>') + 1
                    paragraph = (paragraph[:open_tag_end]
                                 + '<w:pPr>' + box_xml + '</w:pPr>'
                                 + paragraph[open_tag_end:])

            result.append(paragraph)
            pos = p_end

            if had_pagebreak:
                inside = False

        return ''.join(result)

    doc_xml = style_refleksion_blocks(doc_xml)

    # 3. Centrér og farv mørkeblå alle Heading1-4 paragraffer
    # (kapitel-overskrifter og alle subheadings i body).
    def style_heading_paragraphs(xml: str) -> str:
        DARK_BLUE = "2D3748"
        result = []
        pos = 0
        while True:
            p_start = xml.find('<w:p', pos)
            if p_start == -1:
                result.append(xml[pos:])
                break
            tag_end = xml.find('>', p_start) + 1
            p_end = xml.find('</w:p>', tag_end)
            if p_end == -1:
                result.append(xml[pos:])
                break
            p_end += len('</w:p>')

            paragraph = xml[p_start:p_end]
            result.append(xml[pos:p_start])

            if re.search(r'<w:pStyle w:val="Heading[1-4]"\s*/>', paragraph):
                # Centrer — jc skal stå EFTER pStyle ifølge OOXML-skemaet
                if '<w:jc ' not in paragraph:
                    paragraph = re.sub(
                        r'(<w:pStyle w:val="Heading[1-4]"\s*/>)',
                        r'\1<w:jc w:val="center"/>',
                        paragraph,
                        count=1,
                    )

                # Farv mørkeblå (tilføj color til alle runs hvis ikke allerede)
                def add_color(run_match):
                    run = run_match.group(0)
                    if 'w:color' in run:
                        return run
                    if '<w:rPr>' in run:
                        return run.replace(
                            '<w:rPr>',
                            f'<w:rPr><w:color w:val="{DARK_BLUE}"/>',
                            1
                        )
                    open_tag_end = run.find('>') + 1
                    return (run[:open_tag_end]
                            + f'<w:rPr><w:color w:val="{DARK_BLUE}"/></w:rPr>'
                            + run[open_tag_end:])

                paragraph = re.sub(
                    r'<w:r(?:\s[^>]*)?>.*?</w:r>',
                    add_color, paragraph, flags=re.DOTALL,
                )

            result.append(paragraph)
            pos = p_end

        return ''.join(result)

    doc_xml = style_heading_paragraphs(doc_xml)

    # 4. Sikkerhedsnet: samle konsekutive page-break-paragraffer til én.
    # Forhindrer tomme sider når flere kilder hver emit'er deres egen
    # sideskift (fx refleksions-boks afslutter med \clearpage og det næste
    # underkapitel begynder med \clearpage).
    pb_pattern = r'<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    while True:
        new_xml = re.sub(rf'({pb_pattern})\s*(?:{pb_pattern})+',
                         r'\1', doc_xml)
        if new_xml == doc_xml:
            break
        doc_xml = new_xml

    files['word/document.xml'] = doc_xml.encode('utf-8')

    # 4. Modificér styles.xml så Heading1-4 stilene selv har mørkeblå farve
    # (#2D3748). Default pandoc-styles bruger accent1-themeColor (#4F81BD =
    # lyseblå), som kan vinde over run-level color i nogle Word-rendering-
    # tilfælde. Ved at sætte stilens farve sikrer vi at det ikke sker.
    if 'word/styles.xml' in files:
        styles_xml = files['word/styles.xml'].decode('utf-8')

        def patch_heading_color(xml: str, heading_id: str) -> str:
            # Find <w:style ... w:styleId="HeadingN" ...>...</w:style>
            pattern = rf'(<w:style[^>]*"{heading_id}"[^>]*>)(.*?)(</w:style>)'
            m = re.search(pattern, xml, re.DOTALL)
            if not m:
                return xml
            style_block = m.group(2)
            # Erstat eksisterende <w:color w:themeColor="accent1" w:val="4F81BD" />
            new_block = re.sub(
                r'<w:color[^/]*/>',
                '<w:color w:val="2D3748"/>',
                style_block,
                count=1,
            )
            # Hvis der ikke var en w:color (usandsynligt for Heading-stile),
            # tilføj én lige efter <w:rPr>
            if new_block == style_block and '<w:rPr>' in new_block:
                new_block = new_block.replace(
                    '<w:rPr>', '<w:rPr><w:color w:val="2D3748"/>', 1
                )
            return xml[:m.start(2)] + new_block + xml[m.end(2):]

        for hid in ('Heading1', 'Heading2', 'Heading3', 'Heading4'):
            styles_xml = patch_heading_color(styles_xml, hid)

        files['word/styles.xml'] = styles_xml.encode('utf-8')

    # Skriv tilbage
    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Saml app-indhold til bog-manuskript")
    parser.add_argument("--md", action="store_true",
                        help="Kun markdown (skip pandoc)")
    parser.add_argument("--html", action="store_true",
                        help="Markdown + HTML (uden xelatex)")
    parser.add_argument("--docx", action="store_true",
                        help="Generer Word-dokument (manuskript.docx)")
    args = parser.parse_args()

    print("Bygger manuskript fra content/-filer …")
    manuskript = byg_manuskript()

    md_path = OUT / "manuskript.md"
    md_path.write_text(manuskript, encoding="utf-8")
    print(f"  ✓ {md_path} ({len(manuskript):,} tegn)")

    if args.md:
        return

    # DOCX-output (kan kombineres med PDF ved at køre uden flag også)
    if args.docx:
        docx_md = konverter_til_docx_md(manuskript)
        docx_md_path = OUT / "manuskript_docx.md"
        docx_md_path.write_text(docx_md, encoding="utf-8")
        docx_path = OUT / "manuskript.docx"
        if kor_pandoc(docx_md_path, "docx", docx_path):
            print(f"  ✓ {docx_path}")
        else:
            print("  × DOCX fejlede", file=sys.stderr)
            sys.exit(1)
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
