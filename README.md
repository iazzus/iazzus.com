# IAZZUS.com

The personal website of **Ian Vulovic** — a single online identity covering
two things: IT systems work (and the consulting practice growing out of it),
and Men's Physique bodybuilding.

Hand-written HTML, CSS and vanilla JavaScript. **No framework, no build
step, no dependencies.** Every file in this repository is the file that gets
served. Open any of them and what you read is what runs.

Built to deploy on **Cloudflare Pages** at `https://iazzus.com`.

---

## Contents

- [Structure](#structure)
- [Local development](#local-development)
- [Editing the site](#editing-the-site)
- [Design system](#design-system)
- [Images](#images)
- [The contact form](#the-contact-form)
- [Cloudflare Pages deployment](#cloudflare-pages-deployment)
- [Domain configuration](#domain-configuration)
- [Security](#security)
- [Performance](#performance)
- [Future development](#future-development)

---

## Structure

```text
/
├── index.html              Homepage
├── technology/index.html   Technical expertise, platforms, consulting
├── bodybuilding/index.html Men's Physique training, progress, gallery
├── motorcycle/index.html   2016 Kawasaki Ninja 650 ABS — specs, service log
├── about/index.html        Who Ian is and how the two sides connect
├── contact/index.html      Contact form + direct email
├── 404.html                Custom not-found page
│
├── assets/
│   ├── css/
│   │   ├── reset.css       Normalisation only, no design decisions
│   │   ├── variables.css   ← every colour, size, space and duration
│   │   ├── global.css      Base elements, layout primitives, utilities
│   │   ├── components.css  Buttons, nav, cards, forms, footer…
│   │   ├── responsive.css  Breakpoints, reduced motion, print
│   │   └── noscript.css    Loaded only when JavaScript is disabled
│   ├── js/main.js          Nav, header, reveals, footer year, form
│   ├── images/             Photography + Open Graph image (has its own README)
│   ├── video/              Self-hosted clips (has its own README)
│   ├── icons/              apple-touch-icon.png
│   └── fonts/              Empty by design (has its own README)
│
├── favicon.svg             IA monogram
├── robots.txt
├── sitemap.xml
├── _headers                Cloudflare Pages response headers (incl. CSP)
├── _redirects              Cloudflare Pages redirects (www → apex)
├── tools/dev-server.py     Optional local server that replays _headers
├── .editorconfig
└── .gitignore
```

The stylesheets load in that order on every page and each one has a single
job. If you are looking for where something is defined, that order is the
map.

---

## Local development

There is **no build step and nothing to install**. You can double-click
`index.html`, but relative links like `/technology/` will not resolve from
`file://`, so use a local server.

**Simplest — Python's built-in server:**

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>.

**Recommended — the included dev server**, which also replays the headers
from `_headers` (so you can verify the Content-Security-Policy locally) and
serves `404.html` with a real 404 status:

```bash
python tools/dev-server.py
```

It disables caching so edits show up on refresh. Pass a port as the first
argument to use something other than 8000.

**Any other static server works too**, for example `npx serve` or the VS
Code "Live Server" extension.

### After editing

- Hard-refresh (Ctrl+F5) if a CSS change does not appear.
- Check the browser console — the site should produce **zero** console
  output.
- Test at a narrow width (375 px) and a wide one. The navigation switches to
  the mobile panel below 900 px.

---

## Editing the site

### Navigation

Navigation markup is repeated in the `<header>` of each of the seven HTML
files (there is no templating — that is the cost of having no build step).
To add or rename a link, update it in all seven, and in the footer's "Site"
list.

Mark the current page with `aria-current="page"`:

```html
<li><a class="nav__link" href="/technology/" aria-current="page">Technology</a></li>
```

That attribute drives both the highlight and the accent underline — there is
no separate "active" class to keep in sync.

### Colours, spacing, type

Everything lives in [`assets/css/variables.css`](assets/css/variables.css).
Changing `--color-accent` re-themes the entire site: buttons, eyebrows,
underlines, focus rings, the hero wash and the status dots all derive from
it.

```css
--color-accent: #c9954a;   /* brass */
```

If you change it, keep the contrast against `--color-bg` at **4.5:1 or
better**. The current value measures 7.5:1.

### Text

Copy is written directly in the HTML — no CMS, no data files. Search for the
phrase you want to change and edit it.

Two conventions are used to mark provisional content:

- `class="placeholder-text"` renders in italic muted grey and marks a value
  that is deliberately not published yet.
- `<!-- EDIT: … -->` comments mark spots where you are expected to add real
  detail. Search the repository for `EDIT:` to find all of them.

### Contact details

`contact/index.html` publishes **one** channel: `ian.vulovic@iazzus.com`.

**No phone number appears anywhere on this site, by deliberate choice.** A
number published in HTML is scraped within days and cannot be recalled once
it is in a broker's dataset — and unlike an email address, you cannot filter
your way out of it. If you ever decide to add one, understand that is a
one-way door.

Profile links (LinkedIn, GitHub) can be added as extra `.def-list__row`
entries in the "Direct contact" panel; there is an `EDIT:` comment marking
the spot.

### Copyright year

The footer year is set by `main.js` from the system clock. The `2026` in the
markup is only a fallback for visitors with JavaScript disabled; update it
whenever you happen to notice it.

---

## Design system

**Palette** — a dark neutral base with one restrained accent.

| Token                    | Value     | Use                        |
| ------------------------ | --------- | -------------------------- |
| `--color-bg`             | `#08090A` | Page background            |
| `--color-bg-elevated`    | `#101214` | Alternating section bands  |
| `--color-surface`        | `#151719` | Cards and panels           |
| `--color-text`           | `#F4F4F5` | Headings, primary text     |
| `--color-text-secondary` | `#A1A1AA` | Body copy                  |
| `--color-muted`          | `#8B8B94` | Metadata, captions, labels |
| `--color-accent`         | `#C9954A` | Brass — the only accent    |

There is deliberately no dimmer text colour than `--color-muted`; the
obvious next step down fails WCAG AA at body size. Express hierarchy below
that point with size and weight instead.

**Typography** — system font stacks, so there are zero font requests and no
layout shift. Headings and display type use a grotesque stack; eyebrows,
labels, metadata and stat captions use a **monospace** stack, which is what
gives the site its technical register without any graphics. Sizes are fluid
via `clamp()`.

**Components** — buttons, nav, cards, disciplines, tags, badges, stats,
entries, platform groups, media containers, CTA blocks, notices, forms,
tables, empty states and the footer. All in `components.css`, all built on
tokens, named `.block__element--modifier`.

**Motion** — short transitions on hover and focus, plus a one-time fade-and-
rise as sections enter the viewport (`data-reveal`). Nothing loops, nothing
parallaxes. `prefers-reduced-motion: reduce` disables all of it, and the
design is intended to look finished that way.

---

## Images

There are no photographs in the repository yet. Every image slot is a
labelled placeholder that reserves the correct aspect ratio, so dropping in
a real photo will not shift the layout.

Filenames, dimensions, formats and the exact markup to swap in are
documented in [`assets/images/README.md`](assets/images/README.md).

Summary: **WebP, 4:5 portrait for physique shots, 3:2 landscape for the
motorcycle, under ~250 KB**, with real `alt` text, explicit `width`/`height`
and `loading="lazy"`.

## Video

`/motorcycle/` has two video slots. Video is **self-hosted only** — no
YouTube or Vimeo embeds — which is what keeps `media-src 'self'` in the CSP
and avoids a third-party dependency. Encoding commands, size limits and the
markup to swap in are in [`assets/video/README.md`](assets/video/README.md).

The two rules that matter: `preload="none"` so nothing downloads until
someone presses play, and **keep each file under ~20 MB** (Cloudflare Pages
caps individual files at 25 MB).

---

## The contact form

The form **validates but does not send**. `CONTACT_ENDPOINT` at the top of
`assets/js/main.js` is an empty string, and while it is empty the form
reports plainly that no backend is connected rather than faking a success
message. This is deliberate — nothing on the site pretends to work.

To connect it:

1. Build an endpoint that accepts a JSON `POST` — a Cloudflare Pages
   Function at `functions/api/contact.js` is the path of least resistance,
   since it deploys with the same project and needs no extra service.
2. Set the constant:

   ```js
   var CONTACT_ENDPOINT = "/api/contact";
   ```

3. Keep the endpoint same-origin. The CSP sets `connect-src 'self'`, so
   posting to a third-party host would require loosening the policy.
4. Validate again server-side. Front-end validation is a convenience, not a
   control.
5. The form includes a hidden honeypot field named `company`. Reject any
   submission where it is non-empty.

Never put an API key or webhook secret in `main.js` — it ships to every
visitor. Use a Pages Function with an environment variable.

---

## Cloudflare Pages deployment

### Option A — Git integration (recommended)

1. Push this repository to GitHub or GitLab.
2. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**, then pick the repository.
3. Build settings:

   | Field                  | Value             |
   | ---------------------- | ----------------- |
   | Framework preset       | **None**          |
   | Build command          | *(leave empty)*   |
   | Build output directory | `/` *(the root)*  |

4. **Save and Deploy.** It will be live on
   `your-project.pages.dev` in under a minute.

Every push to the production branch deploys automatically; pull requests get
their own preview URLs.

### Option B — Direct upload

**Workers & Pages** → **Create** → **Pages** → **Upload assets**, then drag
the project folder in. Fine for a one-off, but you lose deploy history and
rollback.

`_headers` and `_redirects` are read from the output directory on every
deploy — no configuration needed.

---

## Domain configuration

You own `iazzus.com` in Cloudflare, so this is short. **Do these steps
yourself in the dashboard** — nothing here changes DNS automatically.

1. **Attach the apex domain.** Pages project → **Custom domains** → **Set up
   a custom domain** → `iazzus.com`. Cloudflare creates the required DNS
   record and issues the certificate.
2. **Attach `www`** the same way. Adding it is what makes the `www → apex`
   rule in `_redirects` take effect.
3. **Preferred: redirect www at the zone level instead.** It is faster
   (handled at the edge before Pages is reached) and works on the free plan:

   **iazzus.com** → **Rules** → **Redirect Rules** → **Create rule**

   - When: `Hostname` `equals` `www.iazzus.com`
   - Then: **Dynamic** redirect, **301**
   - Expression: `concat("https://iazzus.com", http.request.uri.path)`
   - Preserve query string: **on**

4. **SSL/TLS** → set encryption mode to **Full (strict)**.
5. **SSL/TLS → Edge Certificates** → enable **Always Use HTTPS** and
   **Automatic HTTPS Rewrites**.
6. Verify: `https://www.iazzus.com/technology/` should land on
   `https://iazzus.com/technology/` with a single 301.

Canonical URLs in the HTML, `sitemap.xml` and `robots.txt` all point at the
apex domain, so keep the apex as the canonical host.

---

## Security

A static site has a small attack surface, but the defaults are still worth
setting. All headers are in [`_headers`](_headers).

| Header                      | Value                                          | Why                                                            |
| --------------------------- | ---------------------------------------------- | -------------------------------------------------------------- |
| `Content-Security-Policy`   | `default-src 'self'` + directives below         | Blocks injected or third-party scripts, styles and frames       |
| `X-Content-Type-Options`    | `nosniff`                                       | Stops MIME-type guessing                                        |
| `X-Frame-Options`           | `DENY`                                          | Clickjacking (legacy companion to `frame-ancestors`)            |
| `Referrer-Policy`           | `strict-origin-when-cross-origin`               | Does not leak full paths to other sites                         |
| `Permissions-Policy`        | camera, mic, geolocation… all denied            | The site needs none of them                                     |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains`           | HTTPS only, for a year, including future subdomains             |
| `Cross-Origin-Opener-Policy`| `same-origin`                                   | Isolates the browsing context                                   |

**The CSP is strict on purpose.** It contains no `'unsafe-inline'` and no
nonces because the site has **zero inline styles and zero executable inline
scripts**. The only inline `<script>` blocks are `type="application/ld+json"`
structured data, which browsers never execute and therefore do not evaluate
against `script-src`.

If you add something the policy blocks, the fix is almost always to move it
into a file rather than to loosen the policy:

- inline `style="…"` → a class in `components.css`
- inline `onclick="…"` → an event listener in `main.js`
- a third-party script → reconsider, then add its exact origin to
  `script-src`, not `'unsafe-inline'`

Test before deploying with `python tools/dev-server.py`, which sends the same
headers locally. Violations appear in the browser console.

`includeSubDomains` on HSTS means any future `msp.iazzus.com` or
`lab.iazzus.com` must be served over HTTPS. Everything behind Cloudflare is,
so this is safe — but be aware of it before pointing a subdomain at
something else. `preload` is deliberately **not** set; it is very hard to
undo.

### Other precautions

- **No secrets in this repository.** Nothing here needs a key. If a future
  feature does, it belongs in a Pages Function environment variable, never in
  `main.js`.
- **No third-party requests at all** — no fonts, no CDNs, no analytics, no
  trackers. Everything is same-origin, which is also why the CSP can stay
  this tight.
- The `.gitignore` blocks `.env`, `*.pem` and `*.key` as a backstop.

---

## Performance

About 49 KB of CSS and 11 KB of JavaScript across the whole site,
uncompressed, before Cloudflare's Brotli — a large share of both is
comments. No fonts, no libraries, no
render-blocking JavaScript (`main.js` is deferred), and no image requests
until real photographs are added.

Things worth preserving:

- Keep JavaScript optional. Everything on the site is readable and navigable
  without it.
- Give every image explicit `width` and `height` so nothing shifts on load.
- If you ever add a font, self-host it and preload it — see
  [`assets/fonts/README.md`](assets/fonts/README.md).

Caching in `_headers` is intentionally short for CSS and JS. Because there
is no build step, filenames are not content-hashed, so a long `max-age`
would strand visitors on a stale stylesheet. If you later add hashed
filenames, switch those rules to `max-age=31536000, immutable`.

---

## Future development

The structure is designed so these are additive rather than rewrites.

**New top-level sections** — copy an existing page directory, keep the
`<head>` block and header/footer markup, change the content. Then add the
nav link (six files), a `<url>` entry in `sitemap.xml`, and a footer link.
Likely candidates: `/blog/`, `/projects/`, `/services/`, `/training/`,
`/gallery/`.

**Real project write-ups** — the `.entry` component on
`/technology/` already handles a title, badge, body and tag list. Replace
the category descriptions with concrete engagements as they become
publishable.

**Progress logging** — `/bodybuilding/` has a real `<table>` with an empty
state. Add one `<tr>` per check-in and delete the empty row.

**Contact backend** — see [the contact form](#the-contact-form). A Pages
Function is the smallest step.

**Subdomains** (`msp.`, `lab.`, `status.`) — separate Pages projects or
Workers, attached as custom domains in the same zone. Nothing in this
repository needs to change.

**When to reconsider the no-build-step decision:** if the header and footer
markup duplicated across pages starts causing drift, that is the signal.
Reach for the smallest thing that fixes it — a static site generator that
still emits plain HTML — rather than a front-end framework.

---

© Ian Vulovic. Content and images are not licensed for reuse.
