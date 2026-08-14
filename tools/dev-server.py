#!/usr/bin/env python3
"""Local development server for iazzus.com.

Optional. `python -m http.server` is enough for day-to-day editing; this
script exists so local behaviour matches Cloudflare Pages more closely:

  * response headers are replayed from the repository's `_headers` file,
    so the Content-Security-Policy can be tested before deploying;
  * unknown paths render `404.html` with a real 404 status.

Usage:
    python tools/dev-server.py [port]

Then open http://localhost:8000
"""

from __future__ import annotations

import http.server
import os
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "public"
DEFAULT_PORT = 8000


def load_headers(path: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    """Parse a Cloudflare Pages `_headers` file into (pattern, headers)."""
    rules: list[tuple[str, list[tuple[str, str]]]] = []
    if not path.is_file():
        return rules

    pattern: str | None = None
    headers: list[tuple[str, str]] = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0].isspace():
            if pattern and ":" in raw:
                name, _, value = raw.strip().partition(":")
                headers.append((name.strip(), value.strip()))
        else:
            if pattern:
                rules.append((pattern, headers))
            pattern = raw.strip()
            headers = []

    if pattern:
        rules.append((pattern, headers))
    return rules


HEADER_RULES = load_headers(ROOT / "_headers")


def headers_for(path: str) -> list[tuple[str, str]]:
    """Collect every rule matching `path`, later rules winning."""
    matched: dict[str, str] = {}
    for pattern, headers in HEADER_RULES:
        if pattern.endswith("*"):
            if not path.startswith(pattern[:-1]):
                continue
        elif pattern != path:
            continue
        for name, value in headers:
            matched[name] = value
    return list(matched.items())


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".webmanifest": "application/manifest+json",
        ".webp": "image/webp",
        ".woff2": "font/woff2",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        for name, value in headers_for(self.path.split("?", 1)[0]):
            # Production caching would hide edits behind a stale copy.
            if name.lower() == "cache-control":
                continue
            self.send_header(name, value)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        page = ROOT / "404.html"
        if code == 404 and page.is_file():
            body = page.read_bytes()
            self.send_response(404, message)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    os.chdir(ROOT)

    with Server(("127.0.0.1", port), Handler) as httpd:
        print(f"iazzus.com -> http://localhost:{port}")
        print(f"serving     {ROOT}")
        print(f"headers     {len(HEADER_RULES)} rule(s) from _headers")
        print("ctrl-c to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
