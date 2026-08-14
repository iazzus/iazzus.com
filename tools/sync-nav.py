#!/usr/bin/env python3
"""Write the shared header and footer into every page.

This is NOT a build step. The HTML files in this repository stay complete
and deployable on their own - this tool just stops the header and footer
from drifting apart across fifteen pages when you add a nav link.

Edit tools/partials/header.html or tools/partials/footer.html, then:

    python tools/sync-nav.py

Add a new page by creating the HTML file and adding it to PAGES below.
The key decides which nav link gets aria-current="page"; use None for
pages that are not in the nav (404).

The tool rewrites whatever sits between the marker comments:

    <!-- header:start --> ... <!-- header:end -->
    <!-- footer:start --> ... <!-- footer:end -->

If a file has no markers yet it falls back to replacing the first
<header class="site-header"> / <footer class="site-footer"> block and
leaves markers behind for next time.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "public"          # deployable site lives here
PARTIALS = ROOT / "tools" / "partials"

# page path (relative to repo root) -> active nav key
PAGES: dict[str, str | None] = {
    "index.html": "home",
    "technology/index.html": "technology",
    "bodybuilding/index.html": "physique",
    "garage/index.html": "garage",
    "garage/motorcycle/index.html": "garage",
    "garage/tesla/index.html": "garage",
    "life/index.html": "life",
    "life/family/index.html": "life",
    "life/reptiles/index.html": "life",
    "life/garden/index.html": "life",
    "about/index.html": "about",
    "about/military/index.html": "about",
    "work-with-me/index.html": "work",
    "contact/index.html": "contact",
    "404.html": None,
    # Unlisted. Gets the shared header/footer like any other page, but is
    # not in the nav, not in sitemap.xml, and noindexed via _headers.
    "frida/index.html": None,
}

MARKERS = {
    "header": ("<!-- header:start -->", "<!-- header:end -->"),
    "footer": ("<!-- footer:start -->", "<!-- footer:end -->"),
}

LEGACY = {
    "header": re.compile(r'<header class="site-header".*?</header>', re.S),
    "footer": re.compile(r'<footer class="site-footer".*?</footer>', re.S),
}


def render(partial: str, active: str | None) -> str:
    """Swap data-nav-key attributes for aria-current on the active link."""
    def sub(match: re.Match[str]) -> str:
        key = match.group(1)
        return ' aria-current="page"' if key == active else ""

    return re.sub(r'\s+data-nav-key="([a-z-]+)"', sub, partial)


def apply(text: str, name: str, block: str) -> tuple[str, bool]:
    start, end = MARKERS[name]
    wrapped = f"{start}\n{block.strip()}\n{end}"

    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(lambda _: wrapped, text, count=1), True

    if LEGACY[name].search(text):
        return LEGACY[name].sub(lambda _: wrapped, text, count=1), True

    return text, False


def main() -> int:
    header = (PARTIALS / "header.html").read_text(encoding="utf-8")
    footer = (PARTIALS / "footer.html").read_text(encoding="utf-8")

    updated, skipped, missing = [], [], []

    for rel, key in PAGES.items():
        path = SITE / rel
        if not path.is_file():
            missing.append(rel)
            continue

        text = original = path.read_text(encoding="utf-8")
        ok = True
        for name, partial in (("header", header), ("footer", footer)):
            text, found = apply(text, name, render(partial, key))
            if not found:
                print(f"  !! no {name} region in {rel}", file=sys.stderr)
                ok = False

        if text != original and ok:
            path.write_text(text, encoding="utf-8", newline="\n")
            updated.append(rel)
        elif ok:
            skipped.append(rel)

    print(f"synced {len(updated)}, already current {len(skipped)}")
    for rel in updated:
        print("  updated", rel)
    if missing:
        print("\nlisted in PAGES but not on disk:", file=sys.stderr)
        for rel in missing:
            print("  ", rel, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
