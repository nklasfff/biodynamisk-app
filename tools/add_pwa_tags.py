#!/usr/bin/env python3
"""Tilføj PWA / iOS standalone meta-tags til alle HTML-filer i projektets rod.
Kører idempotent — springer filer over der allerede har manifest-linket."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PWA_BLOCK = """
  <!-- PWA / iOS standalone-mode -->
  <link rel="manifest" href="manifest.json">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Biodynamisk">
  <meta name="theme-color" content="#1d2731">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">"""

VIEWPORT_RE = re.compile(r'(<meta name="viewport"[^>]*>)')

count_updated = 0
count_skipped = 0
for html_path in sorted(ROOT.glob("*.html")):
    text = html_path.read_text()
    if 'rel="manifest"' in text:
        print(f"  springer over: {html_path.name} (allerede sat op)")
        count_skipped += 1
        continue
    new_text, n = VIEWPORT_RE.subn(r"\1" + PWA_BLOCK, text, count=1)
    if n == 0:
        print(f"  ADVARSEL: ingen viewport-tag i {html_path.name}")
        continue
    html_path.write_text(new_text)
    print(f"  opdateret: {html_path.name}")
    count_updated += 1

print(f"\n{count_updated} filer opdateret, {count_skipped} sprunget over")
