#!/usr/bin/env python3
"""
inject_mobile.py — Add a reversible mobile-responsive layer to Heaven's Dynasty demos.

Injects a single <style id="hd-mobile-fix"> block right before </head>.
It is guarded by @media (max-width:640px) so DESKTOP RENDERING IS UNTOUCHED.
Re-running is safe: it removes any prior hd-mobile-fix block first (idempotent).

Usage:
    python3 inject_mobile.py CHAINLINK_Demo.html      # one file (pilot)
    python3 inject_mobile.py --all                    # every *_Demo.html + named pages
    python3 inject_mobile.py --all --dry-run          # show what would change
"""

import sys, re, glob, os

MARKER_START = "<!-- hd-mobile-fix:start -->"
MARKER_END = "<!-- hd-mobile-fix:end -->"

MOBILE_CSS = f"""{MARKER_START}
<style id="hd-mobile-fix">
/* Heaven's Dynasty universal mobile layer — activates only <=640px, desktop untouched */
@media (max-width: 640px) {{
  /* 1. Kill horizontal overflow at the root */
  html, body {{ overflow-x: hidden !important; max-width: 100vw !important; }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  /* 2. Cap every element to its container — neutralizes fixed px widths (760px/800px/860px) */
  body * {{ max-width: 100% !important; }}
  /* 3. Media never overflows — and photos are capped vertically so they don't
        dominate the screen (fit-to-slide requirement). */
  img, video, svg, canvas, iframe {{ height: auto !important; }}
  img, video {{ max-height: 46vh !important; object-fit: contain; }}
  /* 3b. Compaction — shrink type + spacing so scenes fit vertically */
  body {{ font-size: 0.94rem; }}
  h1 {{ font-size: clamp(1.5rem, 7vw, 2.1rem) !important; line-height: 1.15 !important; }}
  h2 {{ font-size: clamp(1.25rem, 5.5vw, 1.7rem) !important; line-height: 1.18 !important; }}
  h3 {{ font-size: clamp(1.05rem, 4.5vw, 1.35rem) !important; }}
  p, li {{ font-size: 0.9rem; line-height: 1.4; }}
  [class*="scene"], [class*="slide"] {{ gap: 0.6rem !important; }}
  /* 4. Collapse multi-column grids to a single column */
  [class*="grid"], [class*="cols"], [class*="row"], [class*="feed"],
  .cols-2, .cols-3, .cols-4, .splash-grid, .outcome-grid {{
    grid-template-columns: 1fr !important;
  }}
  /* 5. Tables SHRINK TO FIT — every column stays visible, text wraps, NO sideways
        scroll and nothing clipped off-screen. */
  table {{ width: 100% !important; table-layout: fixed !important;
           border-collapse: collapse; font-size: 0.7rem !important; }}
  th, td {{ white-space: normal !important; word-break: break-word;
            overflow-wrap: anywhere; padding: 4px 5px !important; max-width: 100% !important; }}
  /* mono numbers / pills / tags often force nowrap and push past the edge — let them wrap */
  [class*="mono"], [class*="pill"], [class*="tag"], [class*="badge"], [class*="chip"] {{
    white-space: normal !important; word-break: break-word; overflow-wrap: anywhere;
  }}
  /* any element explicitly set to nowrap may overflow — relax it on phones */
  [style*="nowrap"] {{ white-space: normal !important; }}
  /* 6. Status rails / toolbars wrap instead of running off-screen */
  [class*="rail"], [class*="toolbar"], [class*="status"], [class*="nav"] {{
    flex-wrap: wrap !important;
  }}
  /* 7. Comfortable scene padding + breathing room above the playback bar */
  [class*="scene"], [class*="slide"], [class*="stage"] {{
    padding-left: 1rem !important; padding-right: 1rem !important;
  }}
  /* 8. Floating caption/commentary overlays cover the screen on phones — hide
        on mobile. Audio narration is unaffected. NOTE: targets the FLOATING bars
        only (subtitle and narrator ids/classes). The in-scene dot-narration text
        block is real content and is deliberately NOT matched. */
  #subtitles, #subtitles.visible, #subtitle-bar, #subtitle-text, [id*="subtitle"],
  [class*="subtitle"], #narrator, #narrator-text, [id*="narrator"], [class*="narrator"],
  #captions, [id*="caption"]:not([class*="card"]) {{
    display: none !important;
  }}
}}
</style>
<script id="hd-mobile-fit">
/* Auto-fit: scale each visible scene so it fits the phone screen (both axes).
   Mobile only (<=640px). Never scales up. Re-runs on resize + scene change. */
(function(){{
  var MAX_W = 640, BAR = 64; // headroom for the playback bar
  function activeScenes(){{
    return [].slice.call(document.querySelectorAll(
      '[class*="scene"],[class*="slide"]'
    )).filter(function(s){{
      var cs = getComputedStyle(s);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      if (parseFloat(cs.opacity) === 0) return false;
      return s.offsetParent !== null || cs.position === 'fixed';
    }});
  }}
  function fit(){{
    var wrap = document.querySelectorAll('[data-hdfit]');
    if (window.innerWidth > MAX_W){{ // desktop: undo everything
      [].forEach.call(wrap, function(el){{ el.style.transform=''; el.style.transformOrigin='';
        el.removeAttribute('data-hdfit'); }});
      return;
    }}
    activeScenes().forEach(function(s){{
      s.style.transform = 'none';                 // measure natural size
      s.style.transformOrigin = 'top center';
      var w = s.scrollWidth, h = s.scrollHeight;
      if (!w || !h) return;
      var scale = Math.min(1, window.innerWidth / w, (window.innerHeight - BAR) / h);
      if (scale < 0.992){{
        s.style.transform = 'scale(' + scale.toFixed(4) + ')';
        s.setAttribute('data-hdfit','1');
      }} else {{
        s.style.transform = '';
        s.removeAttribute('data-hdfit');
      }}
    }});
  }}
  var t; function deb(){{ clearTimeout(t); t = setTimeout(fit, 100); }}
  window.addEventListener('resize', deb);
  window.addEventListener('orientationchange', deb);
  window.addEventListener('load', deb);
  if (document.readyState !== 'loading') deb();
  else document.addEventListener('DOMContentLoaded', deb);
  try {{
    new MutationObserver(deb).observe(document.documentElement,
      {{ attributes:true, subtree:true, attributeFilter:['class','style'] }});
  }} catch(e){{}}
  setInterval(fit, 700); // safety re-fit for JS-driven scene changes
}})();
</script>
{MARKER_END}
"""


def patch(html: str) -> str:
    # Remove any prior injection (idempotent re-runs)
    html = re.sub(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        "",
        html,
        flags=re.DOTALL,
    )
    # Insert before the first </head>
    idx = html.lower().find("</head>")
    if idx == -1:
        return None  # no head — skip
    return html[:idx] + MOBILE_CSS + "\n" + html[idx:]


def targets(all_mode: bool, args):
    if all_mode:
        files = sorted(
            set(glob.glob("*.html") + glob.glob("*/index.html") + glob.glob("*/*.html"))
        )
        return [f for f in files if "inject" not in f.lower()]
    return args


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    all_mode = "--all" in argv
    files = targets(all_mode, [a for a in argv if not a.startswith("-")])
    if not files:
        print("No files. Use a filename or --all.")
        return
    done = skipped = 0
    for f in files:
        if not os.path.exists(f):
            print(f"  ✗ missing: {f}")
            continue
        src = open(f, encoding="utf-8").read()
        out = patch(src)
        if out is None:
            print(f"  ○ no </head>, skipped: {f}")
            skipped += 1
            continue
        if dry:
            print(f"  ▸ would patch: {f}")
            continue
        open(f, "w", encoding="utf-8").write(out)
        print(f"  ✓ patched: {f}")
        done += 1
    if not dry:
        print(f"\nDone. {done} patched, {skipped} skipped.")


if __name__ == "__main__":
    main()
