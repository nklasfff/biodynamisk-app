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
    ("fil", "ordliste"),
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
    Konvertér '## Til refleksion'-sektioner til pandoc fenced div så de
    kan styles som kasse i PDF'en.
    """
    pattern = re.compile(
        r"^(#{2,6})\s*Til [Rr]efleksion\s*\n(.*?)(?=^#{1,6}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def replace(m):
        body = m.group(2).rstrip()
        return f'\n::: refleksion\n**Til refleksion**\n\n{body}\n:::\n\n'

    return pattern.sub(replace, content)


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

    return header + "\n" + hero + body.strip() + "\n"


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


def render_mit_spejl_arbejdshaefte() -> str:
    """Ekstraher Mit Spejl-spørgsmålene fra js/mit-spejl.js og lav et arbejdshæfte."""
    js = (ROOT / "js" / "mit-spejl.js").read_text(encoding="utf-8")

    # Find QUESTIONS_KORT og QUESTIONS_DYB
    def find_arr(name):
        m = re.search(rf"const\s+{name}\s*=\s*\[(.*?)\n\s*\];", js, re.DOTALL)
        if not m:
            return []
        # Tekst-felter med både titel og tekst
        body = m.group(1)
        items = re.findall(
            r"titel:\s*['\"](.*?)['\"]\s*,[^}]*?tekst:\s*['\"](.*?)['\"]",
            body,
            re.DOTALL,
        )
        return items

    kort = find_arr("QUESTIONS_KORT")
    dyb = find_arr("QUESTIONS_DYB")

    out = []
    out.append("\n# Appendiks A — Mit Spejl\n")
    out.append("*Et arbejdshæfte til selvspejling*\n")
    out.append(dedent("""
        Mit Spejl er et fortællende spejl — ikke en test eller analyse, men
        en serie korte invitationer til åben, nysgerrig opmærksomhed på din
        egen rejse, som den opleves netop nu.

        Brug spørgsmålene som åbninger. Der findes ingen rigtige eller forkerte
        svar. For hvert spørgsmål markerer du på skalaen 1–7 hvor det møder
        dig lige nu — 1 = mærkes næsten ikke, 7 = mærkes som klart til stede.
        Lad svarene komme uden at forsøge at vurdere dem.

        Spørgsmålene findes i to udgaver: den korte (et hurtigt spejl) og
        den dybe (en grundigere lytning). Begge føres her — vælg den der
        passer til hvor du er.
    """).strip() + "\n")

    if kort:
        out.append("\n## Den korte spejling\n")
        for i, (titel, tekst) in enumerate(kort, 1):
            out.append(f"\n**{i}. {titel}** — {tekst}")
            out.append("\n1   2   3   4   5   6   7")
        out.append("")

    if dyb:
        out.append("\n## Den dybe spejling\n")
        for i, (titel, tekst) in enumerate(dyb, 1):
            out.append(f"\n**{i}. {titel}** — {tekst}")
            out.append("\n1   2   3   4   5   6   7")
        out.append("")

    if not kort and not dyb:
        out.append("\n*(spørgsmålene kunne ikke ekstraheres automatisk — se appen for den fulde liste)*\n")

    out.append(dedent("""
        \n## Find dit tyngdepunkt

        Hvert spørgsmål peger til ét af de fem stadier på modenhedsspiralen.
        Når du har besvaret alle, kan du finde dit tyngdepunkt ved at lægge
        mærke til hvilket stadie der gennemgående får højest score.

        Tyngdepunktet er ikke en placering du skal nå hen til — det er en
        fortælling om hvor du står lige nu. Spiralens karakter er at vi
        vender tilbage til det vi troede vi havde forladt.
    """).strip() + "\n")

    return "\n".join(out)


def render_invitationer() -> str:
    """Læs mikrotekster.json og lav appendiks med alle 120 invitationer."""
    path = ROOT / "content" / "daglig-draw" / "mikrotekster.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    teksters = data.get("mikrotekster", [])

    # Gruppér efter kategori_label
    grupper = {}
    for t in teksters:
        label = t.get("kategori_label", "Andet")
        grupper.setdefault(label, []).append(t)

    out = ["\n# Appendiks B — Daglige Invitationer\n"]
    out.append(
        "*120 mikrotekster — én pr. dag, eller blot en at hvile ved når der er behov.*\n"
    )

    for label, teksters in grupper.items():
        out.append(f"\n## {label.title()}\n")
        for t in teksters:
            navn = t.get("navn", "")
            evokation = t.get("evokation", "")
            invitation = t.get("invitation", "")
            out.append(f"\n### {navn}\n")
            if evokation:
                out.append(f"\n{evokation}\n")
            if invitation:
                out.append(f"\n*{invitation}*\n")

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

    # Appendikser
    out.append(render_mit_spejl_arbejdshaefte())
    out.append(render_invitationer())

    return "\n\n".join(out)


# ============================================================================
# PANDOC
# ============================================================================

def latex_header_med_graphicspath() -> str:
    """Bygges dynamisk så graphicspath peger til den faktiske figures-mappe."""
    figures_path = str(FIGURES_DIR.resolve()).replace("\\", "/")
    # graphicspath kræver INGEN mellemrum mellem inder-{} og indhold
    graphicspath = "\\graphicspath{{" + figures_path + "/}}"
    return dedent(rf"""
        \usepackage{{xcolor}}
        \usepackage{{tcolorbox}}
        \tcbuselibrary{{breakable, skins}}
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
