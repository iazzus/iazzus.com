#!/usr/bin/env python3
"""Local development server for iazzus.com.

Optional. `python -m http.server` is enough for day-to-day editing; this
script exists so local behavior matches Cloudflare Pages more closely:

  * response headers are replayed from the repository's `_headers` file,
    so the Content-Security-Policy can be tested before deploying;
  * `_redirects` rules are replayed too, so a section move can be checked
    locally instead of being discovered by a broken link in production;
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


def load_redirects(path: Path) -> list[tuple[str, str, int]]:
    """Parse `_redirects` into (source, destination, status).

    Same shape Cloudflare uses: whitespace-separated, optional trailing
    status code, first match wins. Only the `*` / `:splat` form is
    supported, which is all this site uses.
    """
    rules: list[tuple[str, str, int]] = []
    if not path.is_file():
        return rules

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        status = 301
        if len(parts) >= 3 and parts[2].isdigit():
            status = int(parts[2])
        rules.append((parts[0], parts[1], status))
    return rules


REDIRECT_RULES = load_redirects(ROOT / "_redirects")


def redirect_for(path: str) -> tuple[str, int] | None:
    """First matching rule wins, exactly as Cloudflare evaluates them."""
    for source, destination, status in REDIRECT_RULES:
        if source.endswith("*"):
            prefix = source[:-1]
            if path.startswith(prefix):
                return destination.replace(":splat", path[len(prefix):]), status
        elif source == path:
            return destination, status
    return None


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

    def send_head(self):
        # Redirects are evaluated before the file system, the same order
        # Cloudflare uses. Without this a moved path would still resolve
        # locally from a stale folder and the rule would never be exercised.
        path, _, query = self.path.partition("?")
        hit = redirect_for(path)
        if hit:
            target, status = hit
            if query:
                target += "?" + query
            self.send_response(status)
            self.send_header("Location", target)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        return super().send_head()

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
        print(f"redirects   {len(REDIRECT_RULES)} rule(s) from _redirects")
        print("ctrl-c to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
