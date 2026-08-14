# IAZZUS.com

The personal website of **Ian Vulovic** — one online identity covering IT
systems work and the consulting practice growing out of it, Men's Physique
training, military background, and the rest of life.

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
- [Video](#video)
- [The contact form](#the-contact-form)
- [Cloudflare Pages deployment](#cloudflare-pages-deployment)
- [Domain configuration](#domain-configuration)
- [Email on iazzus.com](#email-on-iazzuscom)
- [Taking payments](#taking-payments)
- [Security](#security)
- [Performance](#performance)
- [Future development](#future-development)

---

## Structure

```text
/
├── index.html              Homepage
├── work-with-me/           Services — IT consulting and training
├── technology/             Technical expertise, platforms, consulting
├── bodybuilding/           Men's Physique training, progress, gallery
│
├── garage/                 Hub: the two vehicles
│   ├── motorcycle/         2016 Kawasaki Ninja 650 ABS
│   └── tesla/              Tesla ownership notes
│
├── life/                   Hub: family, reptiles, garden
│   ├── family/             Photographs, no identifying detail
│   ├── reptiles/           Husbandry, records, gallery
│   └── garden/             Beds, approach, season log
│
├── about/                  Who Ian is and how the sides connect
│   └── military/           Service background
├── contact/                Contact form + direct email
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
├── tools/
│   ├── sync-nav.py         Writes the shared header/footer into every page
│   ├── partials/           Single source of truth for header + footer
│   └── dev-server.py       Local server that replays _headers
│
├── favicon.svg             IA monogram
├── robots.txt
├── sitemap.xml
├── _headers                Cloudflare Pages response headers (incl. CSP)
├── _redirects              www → apex, plus old-URL redirects
├── .editorconfig
├── .gitattributes
└── .gitignore
```

The stylesheets load in that order on every page and each one has a single
job. If you are looking for where something is defined, that order is the
map.

**Note on `/tools/`** — Cloudflare Pages publishes the whole repository
root, so those files are reachable at `iazzus.com/tools/…`. They hold no
secrets and nothing executes server-side, but they are not content, so they
are excluded from search engines by `Disallow: /tools/` in `robots.txt` and
an `X-Robots-Tag: noindex` header in `_headers`.

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

The header and footer are **not** hand-edited per page. Edit the single
source of truth and push it out:

1. Edit `tools/partials/header.html` or `tools/partials/footer.html`.
2. Run:

   ```bash
   python tools/sync-nav.py
   ```

That rewrites the region between `<!-- header:start -->` and
`<!-- header:end -->` (likewise for the footer) in all fifteen pages.

**Adding a page:** create the HTML file, then add it to the `PAGES` dict at
the top of `tools/sync-nav.py` with the nav key that should be highlighted.
Also add a `<url>` block to `sitemap.xml`.

This is not a build step — the committed HTML is complete and deployable on
its own. The tool exists only so fifteen copies of the same nav cannot drift
apart. Active state is driven by `aria-current="page"`, which the tool
applies from the nav key; there is no separate "active" class.

### Colours, spacing, type

Everything lives in [`assets/css/variables.css`](assets/css/variables.css).
Changing `--color-accent` re-themes the entire site: buttons, eyebrows,
underlines, focus rings, the hero wash and the status dots all derive from
it.

```css
--color-accent:   #45b8ac;   /* teal  — everyday accent */
--color-commerce: #e8785f;   /* coral — money moments only */
```

If you change either, keep the contrast against `--color-bg` at **4.5:1 or
better**. Current values measure 8.3:1 and 6.9:1.

Two colours are **not** in `variables.css` and must be changed by hand if
you re-theme: the stroke in `favicon.svg`, and the generated
`assets/images/og-default.png` and `assets/icons/apple-touch-icon.png`.

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
| `--color-accent`         | `#45B8AC` | Teal — the everyday accent |
| `--color-commerce`       | `#E8785F` | Coral — commercial moments |

**The two accents mean different things.** Teal is the everyday accent:
links, eyebrows, rules, focus rings, status dots. Coral is reserved for
moments where money or engagement is on the table — the Work With Me button,
service badges, pricing, the commerce CTA block. That is the entire value of
having it: a visitor learns within one page that coral means "this is the
one that costs something". Start using it decoratively and it stops being a
signal.

There is deliberately no dimmer text colour than `--color-muted`; the
obvious next step down fails WCAG AA at body size. Express hierarchy below
that point with size and weight instead.

### A note on the cascade

`global.css` loads before `components.css`, so a single-class utility in
`global.css` loses to a single-class component rule. Two places rely on
raised specificity rather than `!important` — `.placeholder-text` and
`.site-header__cta` — and both are commented where they are defined. If you
add a utility that must beat a component, do the same rather than reaching
for `!important`.

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

## Email on iazzus.com

Planned, not yet configured. The intended layout:

| Address                   | Role                                 |
| ------------------------- | ------------------------------------ |
| `ian@iazzus.com`          | Primary mailbox                      |
| `iazzus@iazzus.com`       | Alias → primary                      |
| `ian.vulovic@iazzus.com`  | Alias → primary (published on `/contact/`) |

One real mailbox, two aliases. That is the right shape: aliases cost
nothing, and you can retire one without migrating anything.

### Choosing a provider

You administer both of these for a living, so the honest summary is short.
**Google Workspace** or **Microsoft 365 Business Basic** — either is around
$6–7/user/month for one mailbox, both give you real deliverability and a
real admin console, and both let you send *as* an alias, which cheaper
options often do not. Pick whichever you would rather demo to a client,
since this mailbox is also a portfolio piece.

Cloudflare Email Routing is free and forwards `*@iazzus.com` to an existing
inbox, but it is **receive-only** — you cannot send as `ian@iazzus.com`.
Fine as a stopgap, wrong as the destination.

### DNS you will configure in Cloudflare

Do this yourself in the dashboard; nothing here changes DNS.

1. **MX records** as supplied by the provider. Remove any existing MX first
   — mixed MX records from two providers is the classic way to lose mail.
2. **SPF** — one TXT record at the apex, exactly one `v=spf1` record:
   `v=spf1 include:_spf.google.com ~all` (or
   `include:spf.protection.outlook.com`). Never publish two.
3. **DKIM** — generate the key in the provider's admin console, publish the
   CNAME or TXT records it gives you, then **enable signing**. Publishing
   the record without enabling signing is a common half-finished state.
4. **DMARC** — start at `v=DMARC1; p=none; rua=mailto:ian@iazzus.com`, watch
   the reports for a couple of weeks, then move to `p=quarantine` and
   finally `p=reject`. Do not start at `p=reject`.
5. **MTA-STS and TLS-RPT** are worth adding once the above is stable.
6. Set the MX and mail-related records to **DNS only** (grey cloud). Proxying
   them breaks mail.

Afterwards, verify with an external checker before trusting it, and send a
test message to a Gmail and an Outlook address.

### When email is live

Update the address in `contact/index.html` if it changes, and set the
`rua=` DMARC address to a mailbox you actually read.

---

## Taking payments

Planned, not yet built. `/work-with-me/` describes services and says plainly
that pricing is quoted per engagement — no invented figures, and no payment
flow that does not work.

The important constraint: **this site is static, and it must stay that way
to keep its CSP and performance.** So do not build a checkout into it.

Two approaches, in order of how much work they are:

**1. Hosted checkout links (recommended to start).** Create products in
Stripe, generate Payment Links, and make the button on `/work-with-me/` a
plain `<a href>` to that link. The visitor pays on Stripe's domain. No card
data touches your site, no PCI scope, no JavaScript, no CSP change, and you
can be taking money the same afternoon. Invoicing for consulting work is the
same idea — Stripe Invoicing sends a hosted payment page by email.

**2. Embedded checkout.** Only if you need the payment to happen without
leaving the site. This requires loading Stripe's JavaScript, which means
adding `js.stripe.com` to `script-src` and `frame-src` in `_headers`, and a
Pages Function to create sessions server-side. Meaningfully more surface
area for a marginal gain.

**Non-negotiables either way:**

- Your Stripe secret key goes in a **Cloudflare Pages environment
  variable**, read only inside a Pages Function. It must never appear in
  `main.js` or anywhere in this repository — anything shipped to the browser
  is public, and a leaked secret key can move money.
- Only the publishable key (`pk_live_…`) may appear client-side.
- Verify webhook signatures if you add webhooks.
- Never store card numbers. There is no version of this where you should.

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

**New pages** — copy an existing page, keep the `<head>` block and the
`<!-- header:start -->` / `<!-- footer:start -->` markers, change the
content. Then add it to `PAGES` in `tools/sync-nav.py`, run the tool, and
add a `<url>` block to `sitemap.xml`. Likely candidates: `/blog/`,
`/projects/`, `/life/travel/`.

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

**Email and payments** — see the two sections above.

**When to reconsider the no-build-step decision:** `tools/sync-nav.py`
handles the header and footer, which was the first real duplication
problem. The next signal would be needing repeated content *inside* pages —
a blog index, a shared card list. At that point reach for the smallest
thing that fixes it, a static site generator that still emits plain HTML,
rather than a front-end framework.

---

© Ian Vulovic. Content and images are not licensed for reuse.
