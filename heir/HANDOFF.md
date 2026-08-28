# HEIR: King Of The North — build handoff

**Paste this whole file into Claude to get up to speed on the project.**

Artist: King Deazel · Album: *HEIR: King Of The North* · Label: IDMG
Built by: Curtis Stephens III · Status: **working draft, seven sections live**
Live: *(URL below)* · Source: `~/Desktop/HEIR_Site/`

---

## What this is

A custom-built public album site, per the *HEIR Site Build Spec* PDF. Platform
decision was **custom build** (not Bandzoogle). Single `index.html`, hand-written
CSS and vanilla JS, no framework and no CDN libraries — the spec's performance
targets (LCP under 2.5 s on 4G, under 2 MB above the fold) don't survive a
20-library stack. Whole page is **34 KB** before media.

## Design direction

Black ground `#050505`, gold accent `#d4a853`, Playfair Display for display type
and Inter for body — two families, `display=swap`, weight-subset, as specced.
Breakpoints 390 / 768 / 1280 / 1920. Body type never drops below 16 px.

## The seven sections

| # | Section | State |
|---|---------|-------|
| 01 | Hero | Live — **interim** backdrop, awaiting real photography |
| 02 | The Album | Live — cover + full 11-track list |
| 03 | Exclusive Access | Built, **checkout deliberately inert** |
| 04 | King Deazel | Layout live, **bio copy needed from Deazel** |
| 05 | Visuals | Grid live, 6 placeholders awaiting gallery |
| 06 | Videos | **Trailer live**, music-video slot open |
| 07 | BOATS Shop | Grid live, awaiting product photography |
| — | Footer | Email capture live, needs an ESP endpoint |

## Tracklist — CONFIRMED

Taken from IDMG's delivered master files (`idmgatl@gmail.com`, 2026-08-27):

1. Say My Name  2. I Been  3. Biggest  4. Repeat After Me
5. Party At The Palace  6. Vito  7. Hallelujah  8. Take A Break
9. Faded Out  10. Thing For You  11. Keep Rising

**Discrepancy to resolve:** the build spec said *Take A Break* sits at **7**.
The delivered files put it at **8**, with *Hallelujah* at 7. The files were
followed. Confirm which is right.

*Pray To Da Gods* is correctly absent — removed in the v2 re-sequence.
All tracks flag EXPLICIT; no clean versions exist.

Lives in `data/tracklist.json`. The page renders from it — edit the JSON, the
page updates. No HTML to touch.

## Media currently in the build

**Trailer** — `HEIR_King_of_the_North_x_Pray_To_Da_Gods_v2.MOV`, the 2:26 album
intro. Native 768 × 960 (4:5 vertical), HEVC source, re-encoded to H.264 with
`+faststart`, 38 MB, `preload="none"` behind a poster frame so it costs nothing
until played. **Framed vertical on purpose** — the only treatment that neither
stretches nor crops it.

**Cover art** — pulled as a still from that same trailer at 45.1 s. The trailer
is a motion version of the finished cover artwork, so the frame *is* the cover:
title treatment, lion chain, JBM banners, Parental Advisory badge, all present.

> ⚠️ **This is interim.** The still tops out at **768 px**. A finished
> **4000 × 4000** cover master exists per the spec but has not been supplied.
> Send it and the cover and OG card both get rebuilt at full sharpness.

**Hero backdrop** — also derived from the artwork: blurred, darkened, decorative
only. It is **not** the real hero. The spec forbids baked-in type on the hero
because headline type goes on in HTML to stay sharp and reflow on mobile — the
artwork carries its own title treatment, hence the blur.

## Still needed

**From Deazel**
- Hero photography — 3840 × 2160 landscape **and** 1440 × 2160 vertical crop of
  the same frame, sRGB, no baked-in text, dead space in the upper third
- Gallery, 6–10 frames at 2400 px long edge, a few black-and-white
- One portrait, 4:5
- Bio copy, 150–250 words: Chicago → BOATS → independent grind → acting and
  business → HEIR
- Product photography, 2000 px square, one consistent background and lighting
- The 4000 × 4000 cover master
- Music video(s), original camera files — not Instagram exports

**Business decisions**
- Price points for both tiers
- Payment processor (Stripe Checkout recommended)
- Secure download delivery — roughly **400 MB of WAV per customer**, needs
  expiring signed URLs and per-purchase download caps
- Licence terms on the paid download
- Which ESP for the mailing list

**Track durations** — the JSON has slots; total runtime is 33:12.5.
**45-second preview MP3s** — 192 kbps / 48 kHz. Add paths to `preview` in the
JSON and the play buttons activate themselves.

## Deliberately not done

Checkout buttons read **"Payment Not Wired"** and do nothing. That's intentional
— the page can be shown to anyone without implying a working store. Nothing
fake, no stock photography standing in for Deazel, no mock transactions.

## Already handled

Open Graph and Twitter cards, `MusicAlbum` structured data, `dataLayer`
analytics hook, skip link, visible focus rings, `prefers-reduced-motion`,
honeypot on the email form, lazy-loading below the fold, `<picture>` blocks with
full `srcset` pre-written for the hero so real assets drop straight in.

## Run it

```bash
cd ~/Desktop/HEIR_Site && python3 -m http.server 8080
# http://localhost:8080
```

`file://` will not work — the tracklist loads via `fetch()`.

## If you're Claude reading this

The build is a single self-contained `index.html` plus `data/tracklist.json` and
an `assets/` tree. Everything awaiting an asset renders as a labelled placeholder
that states the exact spec it needs, so the page doubles as a shot list. When
asked to update it: edit the JSON for tracklist changes, swap files in `assets/`
for media, and uncomment the prepared `<picture>` blocks in `index.html` when
real photography arrives. Don't add a framework and don't add CDN libraries —
the performance budget is the reason it's hand-written.
