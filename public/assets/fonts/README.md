# Fonts

This folder is intentionally empty.

The site currently uses **system font stacks** (see `--font-display`,
`--font-body` and `--font-mono` in `assets/css/variables.css`). That means
zero font requests, zero layout shift, and nothing to license.

## If you want a self-hosted display face

1. Get a `.woff2` file you are licensed to host. Variable fonts are ideal —
   one file covers every weight.
2. Put it here, e.g. `assets/fonts/iazzus-display.woff2`.
3. Uncomment the `@font-face` block at the bottom of
   `assets/css/variables.css` and adjust the family name and path.
4. Prepend the family to `--font-display`:

   ```css
   --font-display: "IAZZUS Display", "Inter", -apple-system, …;
   ```

5. Preload it in the `<head>` of each page, above the stylesheets:

   ```html
   <link rel="preload" href="/assets/fonts/iazzus-display.woff2"
         as="font" type="font/woff2" crossorigin>
   ```

`font-display: swap` is already in the commented block, so text stays
visible while the font loads.

## Do not use a font CDN

The Content-Security-Policy in `_headers` sets `font-src 'self'`. Loading
fonts from Google Fonts or another CDN would require loosening that policy
and would add a third-party dependency and an extra DNS lookup. Self-host
instead — and add the font's own path to the long-cache rule already present
in `_headers` for `/assets/fonts/*`.
