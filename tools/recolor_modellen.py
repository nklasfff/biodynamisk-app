#!/usr/bin/env python3
"""
Erstatter den varme/gyldne palet med en ren grå/hvid palet i alle
illustrationer der hører under MODELLEN-sektionen.

Den mørke navy-baggrund (#1f2a35 / #131a22 / #0c1218) bevares —
den er identisk med dagens-invitation-stilen og udgør den fælles
visuelle grund. Tekst-toner i koldt blågrå (#d4dfeb, #95aac4, #6a7e9c)
bevares også — de er i forvejen neutrale.

Mappingen er bygget så luminans (perceptuel lyshed) bevares, sådan
at gradienter og dybde stadig læser rigtigt visuelt. Nuancer der ligger
tæt på dagens-invitation-paletten (#ffffff, #e8e8e8, #a8a8a8, #787878,
#d8d8d8, #888888, #666666, #f0f0f0, #b0b0b0, #808080, #c8c8c8) er
prioriteret.

Kør: python3 tools/recolor_modellen.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Varm → grå mapping. Alle hex-værdier er lowercase. Filerne kan
# indeholde både upper- og lowercase, så substitueringen er case-
# insensitive (se replace-løkken nedenfor).
COLOR_MAP = {
    # Højlys, hvide cremer → rene hvider
    "#faf4e8": "#f8f8f8",
    "#fdf8ec": "#fafafa",
    "#fdf6e8": "#f8f8f8",
    "#fcf2dc": "#f4f4f4",
    "#fbf2e0": "#f4f4f4",
    "#faf0d8": "#f0f0f0",
    "#f8eed8": "#eeeeee",
    "#f4ecd8": "#ececec",
    "#f4e6c8": "#e8e8e8",
    "#f0e2c8": "#e0e0e0",
    "#f0d8c0": "#d8d8d8",
    "#ecdcb8": "#d8d8d8",
    "#ecd8b0": "#d4d4d4",
    "#e8dfcf": "#dcdcdc",
    "#e8d4a8": "#cccccc",
    # Mid-toner — gyldne tan → mid-grå
    "#dcc498": "#bcbcbc",
    "#d4b98f": "#b0b0b0",
    "#d4b888": "#b0b0b0",
    "#c9b8a0": "#b0b0b0",
    "#c8a878": "#a4a4a4",
    "#c8a070": "#9c9c9c",
    "#c89e80": "#a0a0a0",
    "#c4b090": "#aaaaaa",
    "#c4a070": "#9c9c9c",
    "#c0a474": "#9c9c9c",
    # Mørkere varme — brunlige → mørkere grå
    "#a89880": "#909090",
    "#a8806a": "#808080",
    "#9c7c50": "#787878",
    "#806848": "#646464",
    "#806448": "#646464",
    "#7c6448": "#626262",
    "#604838": "#4a4a4a",
    "#503820": "#383838",
}

# Filer der skal recolores
TARGETS = [
    "hero-motiver/00-begreber-oversigt.svg",
    "hero-motiver/01-dynamisk-stilhed.svg",
    "hero-motiver/02-breath-of-life.svg",
    "hero-motiver/03-primary-respiration.svg",
    "hero-motiver/04-midtlinjen.svg",
    "hero-motiver/05-the-health.svg",
    "hero-motiver/06-motion-present.svg",
    "hero-motiver/07-fulcrum.svg",
    "hero-motiver/08-stillpoints.svg",
    "hero-motiver/09-transmutation.svg",
    "hero-motiver/10-the-neutral.svg",
    "hero-motiver/11-automatic-shifting.svg",
    "hero-motiver/12-den-iboende-behandlingsplan.svg",
    "hero-motiver/13-fluid-body.svg",
    "hero-motiver/14-the-lesion-field.svg",
    "hero-motiver/15-potency.svg",
    "hero-motiver/16-ignition.svg",
    "hero-motiver/17-axial-fluctuations.svg",
    "hero-motiver/18-wholeness.svg",
    "hero-motiver/24-modellen-oversigt.svg",
    "hero-motiver/28-blechschmidt.svg",
    "hero-motiver/38-ordliste.svg",
    "hero-motiver/helhed-1-balance.svg",
    "hero-motiver/helhed-2-forste-forskydning.svg",
    "hero-motiver/helhed-3-ubalancen-breder-sig.svg",
    "hero-motiver/helhed-4-kronisk-monster.svg",
    "modellen.html",
    "begreber.html",
    "js/det-levende-hierarki.js",
]


def recolor(text: str) -> tuple[str, int]:
    """Returner (ny tekst, antal substitutioner)."""
    total = 0
    for old, new in COLOR_MAP.items():
        # Case-insensitive match på hele hex-koden — kun præcise 6-cifrede matches
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        new_text, n = pattern.subn(new, text)
        if n:
            text = new_text
            total += n
    return text, total


def main() -> int:
    grand_total = 0
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"SPRING OVER (mangler): {rel}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        new_text, n = recolor(original)
        if n == 0:
            print(f"  uændret: {rel}")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"  {n:3d} substitutioner: {rel}")
        grand_total += n
    print(f"\nFærdig — {grand_total} substitutioner i {len(TARGETS)} filer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
