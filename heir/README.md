# HEIR: King Of The North — site build

Custom build. All seven sections from the spec, house visual language
(Playfair Display + Inter, gold on black), no CDN dependencies.

Run locally — `fetch()` needs a server, `file://` will not work:

    cd ~/Desktop/HEIR_Site && python3 -m http.server 8080
    # http://localhost:8080

---

## Drop assets in here

    assets/img/
      hero-1280.avif   hero-1920.avif   hero-2560.avif      (+ .webp, + hero-1920.jpg)
      hero-vert-800.avif  hero-vert-1440.avif               (+ .webp)
      cover-600.webp   cover-1200.webp  cover-1200.jpg
      og-cover.jpg     1200 × 630, for link previews
      portrait.jpg     4:5
      gallery-01…06    2400 px long edge
    assets/video/
      trailer.mp4  trailer-poster.jpg
      motion.mp4   motion-poster.jpg
    assets/audio/
      preview-01.mp3 … preview-11.mp3    192 kbps / 48 kHz, 45 s
    assets/merch/
      tee.jpg  hoodie.jpg  hat.jpg  chain.jpg    2000 px square

Every placeholder in the page states the spec it's waiting on. Commented-out
`<picture>` blocks with full `srcset` sit directly above the hero and cover
placeholders — uncomment, delete the placeholder `<div class="ph">`, done.

Also uncomment the two `<link rel="preload">` lines in `<head>` once the hero
exists. That's the LCP element; without the preload the 2.5 s target is at risk.

### Encoding

    # web video
    ffmpeg -i in.mov -c:v libx264 -profile:v high -crf 18 -preset slow \
      -vf "scale=1920:-2" -pix_fmt yuv420p -movflags +faststart \
      -c:a aac -b:a 192k trailer.mp4

    # silent hero loop
    ffmpeg -i in.mov -c:v libx264 -crf 23 -preset slow \
      -vf "scale=1920:-2" -pix_fmt yuv420p -movflags +faststart -an loop.mp4

---

## Tracklist

`data/tracklist.json` drives section 02. Fill in titles and durations, set
`"confirmed": true`, and the SEQUENCE PENDING banner removes itself. Nothing
else needs touching.

---

## Still to wire

| Item | Where | Needs |
|---|---|---|
| Checkout | `[data-buy]` buttons | Stripe Checkout + price points |
| Download delivery | — | Expiring signed URLs, per-purchase caps (~400 MB WAV each) |
| Mailing list | `ENDPOINT` const in `index.html` | ESP POST endpoint |
| Analytics | `track()` in `index.html` | Pushes to `dataLayer`; point at your provider |
| Social links | footer `<nav class="social">` | Real URLs |
| Canonical URL | `og:url` | Real domain |

Buy buttons are **deliberately inert** and read "Payment Not Wired" so the page
can be shown to anyone without implying a working store.

---

## Open decisions still blocking

1. **Tracklist sign-off** — blocks section 02 only.
2. **Which motion video, and the 4:5 frame** — laid out vertical for now, the
   only option that loses no picture.
3. **Preview length** — built to 45 s, change `previewSeconds` in the JSON.
4. ~~Platform~~ — settled: custom.
