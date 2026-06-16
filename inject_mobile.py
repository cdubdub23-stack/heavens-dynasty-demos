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
  /* 3. Media never overflows */
  img, video, svg, canvas, iframe {{ height: auto !important; }}
  /* 4. Collapse multi-column grids to a single column */
  [class*="grid"], [class*="cols"], [class*="row"], [class*="feed"],
  .cols-2, .cols-3, .cols-4, .splash-grid, .outcome-grid {{
    grid-template-columns: 1fr !important;
  }}
  /* 5. Wide tables scroll horizontally instead of clipping */
  table {{ display: block; width: 100% !important; overflow-x: auto;
           -webkit-overflow-scrolling: touch; }}
  /* 6. Status rails / toolbars wrap instead of running off-screen */
  [class*="rail"], [class*="toolbar"], [class*="status"], [class*="nav"] {{
    flex-wrap: wrap !important;
  }}
  /* 7. Comfortable scene padding + breathing room above the playback bar */
  [class*="scene"], [class*="slide"], [class*="stage"] {{
    padding-left: 1rem !important; padding-right: 1rem !important;
  }}
  /* 8. Narration caption overlay (#subtitles) covers the screen on phones —
        hide it on mobile. Audio narration is unaffected. */
  #subtitles, #subtitles.visible, [id*="subtitle"], [class*="subtitle"],
  #captions, [id*="caption"]:not([class*="card"]) {{
    display: none !important;
  }}
}}
</style>
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
