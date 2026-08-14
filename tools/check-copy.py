#!/usr/bin/env python3
"""Fail if banned characters have crept back into the source.

    python tools/check-copy.py

Exits non-zero and prints file:line:column for every hit, so it works both
as a git pre-commit hook (.githooks/pre-commit) and as a manual check.

The dash rule is a house style decision, not a technical one: em and en
dashes are not used anywhere on this site, in visitor-facing copy or in
source comments. Write a plain hyphen, a comma, or a colon instead.

The banned characters are written as codepoints rather than literals on
purpose. A checker that contains the very characters it bans would flag
itself, and excluding this file by name would leave a hole in the check.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# codepoint -> what to write instead
BANNED = {
    0x2014: "em dash, use a hyphen -",
    0x2013: "en dash, use a hyphen -",
    0x2015: "horizontal bar, use a hyphen -",
    0x2012: "figure dash, use a hyphen -",
}

# Anything not listed here is skipped: binaries, images, fonts, media.
TEXT_SUFFIXES = {
    ".html", ".css", ".js", ".json", ".md", ".py", ".ps1", ".toml",
    ".txt", ".svg", ".yml", ".yaml", "",
}

SKIP_DIRS = {".git", "node_modules", ".wrangler"}


def text_files() -> list[Path]:
    out = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            out.append(path)
    return sorted(out)


def main() -> int:
    # The offending line gets echoed back, so stdout has to survive
    # characters the Windows console encoding cannot represent.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    failures = 0

    for path in text_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(lines, 1):
            for codepoint, advice in BANNED.items():
                char = chr(codepoint)
                if char not in line:
                    continue
                failures += line.count(char)
                column = line.index(char) + 1
                print(f"{rel}:{number}:{column}: {advice}")
                print(f"    {line.strip()[:110]}")

    if failures:
        print(f"\n{failures} banned character(s). Nothing was committed.")
        return 1

    print("check-copy: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
