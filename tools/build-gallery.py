#!/usr/bin/env python3
"""Generate gallery markup from whatever files are in a folder.

Drop photos and videos into their folder, run this, done. No hand-editing
HTML per file, and no chance of a typo'd filename pointing at nothing.

    python tools/build-gallery.py

Image dimensions are read straight from the file headers, so every <img>
gets correct width/height attributes and the page never shifts as photos
load. No dependencies - PNG, JPEG and WebP headers are parsed here.

It rewrites whatever sits between the marker comments in each page:

    <!-- gallery:start --> ... <!-- gallery:end -->
    <!-- videos:start -->  ... <!-- videos:end -->

Everything outside the markers is left alone, so hand-written captions
elsewhere on the page survive. Files are sorted by name, so prefix them
01-, 02-… if you care about order.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "public"

IMAGE_TYPES = (".webp", ".jpg", ".jpeg", ".png", ".avif")
VIDEO_TYPES = (".mp4", ".webm", ".mov")

# page -> where its media lives, and how the photos should be cropped.
# shape is the .media--* modifier: portrait (4:5), landscape (3:2),
# square (1:1) or wide (16:9).
GALLERIES: dict[str, dict] = {
    "frida/index.html": {
        "images": "assets/images/frida",
        "masonry": True,
        # No "videos" key on purpose: the clips section is not rendered on
        # that page right now, so there is nothing to write into and an
        # empty placeholder would be worse than nothing. Video support is
        # untouched and still used by other pages. To bring it back, add
        # "videos": "assets/video/frida" here and put videos:start/end
        # markers back on the page.
    },
    "life/reptiles/index.html": {
        "images": "assets/images/reptiles",
        "shape": "landscape",
    },
    "life/garden/index.html": {
        "images": "assets/images/garden",
        "shape": "landscape",
    },
    "life/family/index.html": {
        "images": "assets/images/family",
        "shape": "landscape",
    },
    "garage/motorcycle/index.html": {
        "images": "assets/images/motorcycle",
        "videos": "assets/video/motorcycle",
        "shape": "landscape",
    },
    "garage/tesla/index.html": {
        "images": "assets/images/tesla",
        "shape": "landscape",
    },
    "about/military/index.html": {
        "images": "assets/images/military",
        "shape": "landscape",
    },
    # bodybuilding/index.html is deliberately absent. Physique photographs
    # are published as dated check-ins (front / side / rear grouped with the
    # phase and notes), which a flat auto-generated grid cannot express, and
    # until the first one exists the page renders no gallery at all rather
    # than an empty placeholder. The markup template lives in a comment in
    # the "Documented, not remembered" section of that page. To switch to a
    # plain generated grid instead, add:
    #     "bodybuilding/index.html": {
    #         "images": "assets/images/physique",
    #         "shape": "portrait",
    #     },
    # and put gallery:start / gallery:end markers back on the page.
}


# ---------------------------------------------------------------- sizing

def png_size(data: bytes) -> tuple[int, int] | None:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # Standalone markers carry no length.
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        # Any SOF frame header holds the real dimensions.
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6,
                      0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + seg_len
    return None


def webp_size(data: bytes) -> tuple[int, int] | None:
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        w = int.from_bytes(data[24:27], "little") + 1
        h = int.from_bytes(data[27:30], "little") + 1
        return w, h
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 ":
        w, h = struct.unpack("<HH", data[26:30])
        return w & 0x3FFF, h & 0x3FFF
    return None


def dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()[:65536]
    except OSError:
        return None
    for reader in (png_size, jpeg_size, webp_size):
        try:
            size = reader(data)
        except (struct.error, IndexError):
            size = None
        if size and all(size):
            return size
    return None


# ---------------------------------------------------------------- markup

def figure(src: str, shape: str, size: tuple[int, int] | None) -> str:
    dims = f' width="{size[0]}" height="{size[1]}"' if size else ""
    return (
        '        <figure class="gallery__item">\n'
        f'          <div class="media media--{shape}">\n'
        f'            <img src="{src}" alt=""{dims} loading="lazy" decoding="async">\n'
        "          </div>\n"
        "        </figure>"
    )


def video_figure(src: str, poster: str | None) -> str:
    poster_attr = f'\n                 poster="{poster}"' if poster else ""
    return (
        '        <figure class="gallery__item">\n'
        '          <div class="media media--wide">\n'
        f'            <video controls preload="none" playsinline{poster_attr}>\n'
        f'              <source src="{src}" type="video/mp4">\n'
        "            </video>\n"
        "          </div>\n"
        "        </figure>"
    )


def placeholder(kind: str, folder: str) -> str:
    """Empty state for a gallery with no files yet.

    Visitor-facing copy only. The instructions for whoever maintains the
    site go in an HTML comment beside it, so they are visible in the source
    but never rendered - a page should not explain its own build process to
    the person reading it.
    """
    return (
        f"        <!-- Empty: add files to public/{folder}/ then run\n"
        "             python tools/build-gallery.py -->\n"
        '        <div class="empty-state">\n'
        f'          <h3 class="empty-state__title">No {kind} yet</h3>\n'
        '          <p class="empty-state__body">Coming soon.</p>\n'
        "        </div>"
    )


def collect(folder: Path, suffixes: tuple[str, ...]) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        (p for p in folder.iterdir()
         if p.is_file() and p.suffix.lower() in suffixes),
        key=lambda p: p.name.lower(),
    )


def replace_block(text: str, name: str, body: str) -> tuple[str, bool]:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        return text, False
    return pattern.sub(lambda _: f"{start}\n{body}\n      {end}", text, count=1), True


def main() -> int:
    total_images = total_videos = 0

    for page, cfg in GALLERIES.items():
        path = SITE / page
        if not path.is_file():
            continue

        text = original = path.read_text(encoding="utf-8")
        shape = cfg.get("shape", "landscape")

        img_folder = cfg.get("images")
        if img_folder:
            files = collect(SITE / img_folder, IMAGE_TYPES)
            # Masonry galleries let every photo keep its own proportions, so
            # nothing is cropped. Otherwise everything is forced to one shape.
            masonry = cfg.get("masonry", False)
            item_shape = "natural" if masonry else shape
            blocks = [
                figure(f"/{img_folder}/{f.name}", item_shape, dimensions(f))
                for f in files
            ]
            if blocks:
                css = "gallery gallery--masonry" if masonry else "gallery"
                body = (f'      <div class="{css}" data-reveal>\n'
                        + "\n".join(blocks)
                        + "\n      </div>")
            else:
                body = placeholder("photos", img_folder)
            text, found = replace_block(text, "gallery", body)
            if found and files:
                total_images += len(files)
                print(f"  {page}: {len(files)} photo(s)")
            elif not found:
                print(f"  !! {page}: no gallery markers", file=sys.stderr)

        vid_folder = cfg.get("videos")
        if vid_folder:
            files = collect(SITE / vid_folder, VIDEO_TYPES)
            blocks = []
            for f in files:
                stem = f.with_suffix("").name
                poster = None
                for ext in (".jpg", ".jpeg", ".webp", ".png"):
                    if img_folder and (SITE / img_folder / f"{stem}-poster{ext}").is_file():
                        poster = f"/{img_folder}/{stem}-poster{ext}"
                        break
                blocks.append(video_figure(f"/{vid_folder}/{f.name}", poster))
            if blocks:
                body = ('      <div class="grid grid--2" data-reveal>\n'
                        + "\n".join(blocks)
                        + "\n      </div>")
            else:
                body = placeholder("video", vid_folder)
            text, found = replace_block(text, "videos", body)
            if found and files:
                total_videos += len(files)
                print(f"  {page}: {len(files)} video(s)")
            elif not found:
                print(f"  !! {page}: no videos markers", file=sys.stderr)

        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")

    print(f"\n{total_images} photo(s), {total_videos} video(s) written")
    if total_images == 0 and total_videos == 0:
        print("Nothing found - check the folders listed in GALLERIES.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
