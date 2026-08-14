# Video

Self-hosted video only. Nothing on this site embeds a third-party player,
which is why the Content-Security-Policy can stay closed (`media-src 'self'`
in `_headers`). Adding a YouTube or Vimeo iframe would require opening
`frame-src` to that host — possible, but it is a real tradeoff, not a
formality.

## Filenames

The placeholders on `/motorcycle/` reference these:

| Filename                     | Aspect | Resolution  |
| ---------------------------- | ------ | ----------- |
| `ninja-650-ride.mp4`         | 16:9   | 1920 × 1080 |
| `ninja-650-walkaround.mp4`   | 16:9   | 1920 × 1080 |

Each clip also wants a poster image in `assets/images/`, named to match:
`ninja-650-ride-poster.jpg`, 1920 × 1080, under ~200 KB.

## Encoding

H.264 in an MP4 container plays everywhere without a fallback file. If you
have ffmpeg:

```bash
ffmpeg -i input.mov -c:v libx264 -preset slow -crf 23 -vf scale=1920:-2 -c:a aac -b:a 128k -movflags +faststart ninja-650-ride.mp4
```

- `-crf 23` is a good default. Lower is better quality and a bigger file;
  18 is close to visually lossless, 28 is noticeably soft.
- `-movflags +faststart` moves the index to the front of the file so
  playback can begin before the whole thing downloads. Do not skip it.
- **Keep clips under ~20 MB.** Cloudflare Pages has a 25 MB per-file limit,
  and a large video is the fastest way to ruin an otherwise quick site.
  Trim hard before you re-encode.

Extract a poster frame from the video itself so it matches exactly:

```bash
ffmpeg -i ninja-650-ride.mp4 -ss 00:00:03 -vframes 1 -q:v 3 ninja-650-ride-poster.jpg
```

## Markup

Replace the `.media__placeholder` div, keeping the wrapping `.media` element
so the aspect ratio stays reserved:

```html
<div class="media media--wide">
  <video controls preload="none" playsinline
         poster="/assets/images/ninja-650-ride-poster.jpg"
         width="1920" height="1080">
    <source src="/assets/video/ninja-650-ride.mp4" type="video/mp4">
    <track kind="captions" src="/assets/video/ninja-650-ride.vtt"
           srclang="en" label="English">
    Your browser cannot play this video.
  </video>
</div>
```

- `preload="none"` means nothing downloads until the visitor presses play.
  This matters more than any other setting on this page.
- `playsinline` stops iOS from hijacking into fullscreen.
- Never use `autoplay`. If you ever do, it must also be `muted` and `loop`,
  and it should not be the main content of a page.
- Add a `.vtt` captions track for anything with speech. If a clip is silent
  engine noise, omit the `<track>` rather than shipping an empty one.
