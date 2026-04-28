#!/usr/bin/env python3
"""Migrer alle HTML-filer til den fælles 5-tab bottom-nav.

For hver HTML-fil:
1. Erstat inline <nav class="bottom-nav">...</nav> med placeholder
   <nav class="bottom-nav" data-active="X"></nav>
2. Fjern <button class="theme-toggle">...</button>
3. Tilføj <script src="js/bottom-nav.js"></script> før </body>

Kører idempotent — springer over hvis allerede migreret.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mapping fra filnavn til hvilken tab der er aktiv
ACTIVE_MAP = {
    "modellen.html": "modellen",
    "begreber.html": "modellen",
    "behandleren.html": "behandleren",
    "zoner.html": "behandleren",
    "rejsen.html": "rejsen",
    "stadier.html": "rejsen",
    "inspiration.html": "inspiration",
    # Dynamiske sider sætter active fra JS — placeholder er bare tom her
    "kapitel.html": "",
    "begreb.html": "modellen",
    "zone.html": "behandleren",
    "stadie.html": "rejsen",
    "index.html": "",  # Forsiden har ingen aktiv tab
    "info.html": "info",  # Allerede sat
}

# Regex: <nav class="bottom-nav">...indhold...</nav>
NAV_BLOCK = re.compile(r'<nav class="bottom-nav">.*?</nav>', re.DOTALL)

# Regex: <button class="theme-toggle"...>...</button>
THEME_TOGGLE = re.compile(r'\s*<!--[^>]*[Dd]ark mode toggle[^>]*-->\s*\n?\s*<button class="theme-toggle"[^>]*></button>\s*\n?')

# Regex: hele bottom-nav i template-literal i JS (`<nav class="bottom-nav">...`)
JS_NAV_BLOCK = re.compile(
    r'<nav class="bottom-nav">.*?</nav>',
    re.DOTALL,
)

count_html = 0
count_js_nav = 0
count_theme_removed = 0
count_script_added = 0

for html_path in sorted(ROOT.glob("*.html")):
    name = html_path.name
    if name == "info.html":
        # Info har allerede placeholder + script
        continue

    text = html_path.read_text()
    original = text
    active = ACTIVE_MAP.get(name, "")

    # 1. Erstat statiske <nav class="bottom-nav">...</nav> blocks med placeholder
    placeholder = f'<nav class="bottom-nav" data-active="{active}"></nav>'
    new_text, n = NAV_BLOCK.subn(placeholder, text)
    if n > 0:
        text = new_text
        count_html += n

    # 2. Fjern theme-toggle button
    new_text, n = THEME_TOGGLE.subn("\n", text)
    if n > 0:
        text = new_text
        count_theme_removed += n

    # 3. Tilføj <script src="js/bottom-nav.js"></script> før </body> hvis ikke allerede der
    if 'bottom-nav.js' not in text:
        text = text.replace(
            "</body>",
            '  <script src="js/bottom-nav.js"></script>\n</body>',
            1,
        )
        count_script_added += 1

    if text != original:
        html_path.write_text(text)
        print(f"  opdateret: {name}")

print(f"\n{count_html} bottom-nav blocks erstattet")
print(f"{count_theme_removed} theme-toggle buttons fjernet")
print(f"{count_script_added} bottom-nav.js scripts tilføjet")
