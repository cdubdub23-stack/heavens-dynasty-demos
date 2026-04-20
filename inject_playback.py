#!/usr/bin/env python3
"""
Inject prev/pause/next playback controls into ALL demos.
Universal — works with different scene navigation patterns.
"""

import os
import re
import glob

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
SKIP = ["index.html", "inject_playback.py", "BuildrsNation_Demo.html"]

# ── CSS to inject ─────────��────────────────────────────────
PLAYBACK_CSS = """
/* ── Playback Controls (prev, play/pause, next) ── */
#playback-ctrl {
    position: fixed; bottom: 1.5rem; left: 50%;
    transform: translateX(-50%);
    z-index: 9990;
    display: none;
    align-items: center;
    gap: 0.6rem;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(10px);
    padding: 0.4rem 1rem;
    border-radius: 50px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.pb-ctrl-btn {
    width: 38px; height: 38px;
    border-radius: 50%;
    border: none;
    background: transparent;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.2s, transform 0.2s;
}
.pb-ctrl-btn:hover { background: rgba(255,255,255,0.15); transform: scale(1.1); }
.pb-ctrl-btn.pp-main {
    width: 44px; height: 44px;
    background: rgba(255,255,255,0.2);
    font-size: 1.1rem;
}
.pb-ctrl-btn.pp-main:hover { background: rgba(255,255,255,0.3); }
.pb-scene-num {
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(255,255,255,0.7);
    min-width: 36px;
    text-align: center;
}
"""

# ── HTML to inject ───────────────��─────────────────────────
PLAYBACK_HTML = """
<!-- Playback Controls (injected) -->
<div id="playback-ctrl">
    <button class="pb-ctrl-btn" onclick="pbPrev()" title="Previous (Left)">&#x23EE;</button>
    <button class="pb-ctrl-btn pp-main" id="pb-pp-btn" onclick="pbToggle()" title="Play/Pause (Space)">&#x23F8;</button>
    <button class="pb-ctrl-btn" onclick="pbNext()" title="Next (Right)">&#x23ED;</button>
    <span class="pb-scene-num" id="pb-counter">1/8</span>
</div>
"""

# ── JS to inject ──────────────────────────────────────────
PLAYBACK_JS = """
// ── Playback Controls (injected) ──────────────────
(function(){
    var pbPaused = false;
    var pbTimer = null;
    var pbCurrentScene = 0;
    var pbTotalScenes = 0;
    var pbOrigAdvance = null;  // reference to original advance function

    // Detect scene count
    function pbDetectScenes() {
        var scenes = document.querySelectorAll('.scene, [class*="scene-"]');
        // Filter to direct scene containers (not sub-elements)
        var count = 0;
        scenes.forEach(function(s) {
            if (s.id && (s.id.startsWith('scene-') || s.id.match(/^scene\\d/)) ||
                s.className.match(/^scene$|^scene /)) {
                count++;
            }
        });
        if (count === 0) {
            // Try SCENES array
            if (window.SCENES && Array.isArray(window.SCENES)) count = window.SCENES.length;
            else if (window.scenes && Array.isArray(window.scenes)) count = window.scenes.length;
        }
        if (count === 0) count = document.querySelectorAll('[id^="scene"]').length;
        pbTotalScenes = count || 8;
    }

    // Show the playback bar
    window.pbShow = function() {
        document.getElementById('playback-ctrl').style.display = 'flex';
        pbDetectScenes();
        pbUpdateCounter();
    };

    function pbUpdateCounter() {
        var el = document.getElementById('pb-counter');
        if (el) el.textContent = (pbCurrentScene + 1) + '/' + pbTotalScenes;
    }

    // Hook into scene changes by watching for active class changes
    var pbObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            if (m.type === 'attributes' && m.attributeName === 'class') {
                var el = m.target;
                if (el.classList && el.classList.contains('active') &&
                    (el.classList.contains('scene') || el.id.startsWith('scene'))) {
                    // Figure out which scene index this is
                    var allScenes = document.querySelectorAll('.scene, [id^="scene-"]');
                    allScenes.forEach(function(s, i) {
                        if (s === el) pbCurrentScene = i;
                    });
                    pbUpdateCounter();
                }
            }
        });
    });

    // Start observing after a short delay (let demo initialize)
    setTimeout(function() {
        var scenes = document.querySelectorAll('.scene, [id^="scene-"]');
        scenes.forEach(function(s) {
            pbObserver.observe(s, { attributes: true });
        });
    }, 2000);

    // Also show playback bar when splash is hidden
    var splashCheck = setInterval(function() {
        var splash = document.getElementById('splash');
        if (!splash || splash.style.display === 'none' || splash.classList.contains('hidden') ||
            getComputedStyle(splash).opacity === '0' || getComputedStyle(splash).display === 'none') {
            pbShow();
            clearInterval(splashCheck);
        }
    }, 500);

    // Prev
    window.pbPrev = function() {
        pbCurrentScene = Math.max(0, pbCurrentScene - 1);
        pbGoTo(pbCurrentScene);
    };

    // Next
    window.pbNext = function() {
        pbCurrentScene = Math.min(pbTotalScenes - 1, pbCurrentScene + 1);
        pbGoTo(pbCurrentScene);
    };

    // Go to scene
    window.pbGoTo = function(idx) {
        // Try various known function names
        if (typeof goToScene === 'function') { goToScene(idx); return; }
        if (typeof goScene === 'function') { goScene(idx); return; }
        if (typeof showScene === 'function') { showScene(idx); return; }

        // Fallback: manually activate scene by index
        var scenes = document.querySelectorAll('.scene, [id^="scene-"]');
        scenes.forEach(function(s, i) {
            if (i === idx) s.classList.add('active');
            else s.classList.remove('active');
        });

        // Try to play corresponding audio
        var player = document.getElementById('player') || document.querySelector('audio');
        if (player && window.SCENES && window.SCENES[idx]) {
            var sceneId = window.SCENES[idx].id || window.SCENES[idx].key || window.SCENES[idx].name;
            if (sceneId) {
                if (window.__AUDIO_B64 && window.__AUDIO_B64[sceneId]) {
                    player.src = 'data:audio/mpeg;base64,' + window.__AUDIO_B64[sceneId];
                }
                if (!pbPaused) player.play().catch(function(){});
            }
        }
        pbUpdateCounter();
    };

    // Toggle play/pause
    window.pbToggle = function() {
        pbPaused = !pbPaused;
        var btn = document.getElementById('pb-pp-btn');
        var player = document.getElementById('player') || document.querySelector('audio');
        if (pbPaused) {
            btn.innerHTML = '&#x25B6;';
            if (player) player.pause();
        } else {
            btn.innerHTML = '&#x23F8;';
            if (player) player.play().catch(function(){});
        }
    };

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.key === 'ArrowLeft') { e.preventDefault(); pbPrev(); }
        if (e.key === 'ArrowRight') { e.preventDefault(); pbNext(); }
        if (e.key === ' ' && document.getElementById('playback-ctrl').style.display === 'flex') {
            e.preventDefault();
            pbToggle();
        }
    });
})();
"""


def inject_demo(filepath):
    """Inject playback controls into a single demo file."""
    with open(filepath, "r") as f:
        html = f.read()

    # Skip if already injected
    if "playback-ctrl" in html:
        return "SKIP (already has controls)"

    # Skip if too small (probably not a real demo)
    if len(html) < 5000:
        return "SKIP (too small)"

    modified = False

    # 1. Inject CSS before </style> or before </head>
    if "</style>" in html:
        html = html.replace("</style>", PLAYBACK_CSS + "\n</style>", 1)
        modified = True
    elif "</head>" in html:
        html = html.replace(
            "</head>", "<style>" + PLAYBACK_CSS + "</style>\n</head>", 1
        )
        modified = True

    # 2. Inject HTML before </body>
    if "</body>" in html:
        html = html.replace("</body>", PLAYBACK_HTML + "\n</body>", 1)
        modified = True

    # 3. Inject JS before </script> (last one) or before </body>
    if "</body>" in html:
        html = html.replace(
            "</body>", "<script>" + PLAYBACK_JS + "</script>\n</body>", 1
        )
        modified = True

    if modified:
        with open(filepath, "w") as f:
            f.write(html)
        return "DONE"
    return "SKIP (no injection point)"


def main():
    print("\n  .:*:. PLAYBACK CONTROLS INJECTION .:*:.\n")

    files = glob.glob(os.path.join(DEMO_DIR, "*.html"))
    results = {"DONE": 0, "SKIP": 0}

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        if filename in SKIP:
            continue

        status = inject_demo(filepath)
        prefix = "DONE" if "DONE" in status else "SKIP"
        results[prefix] = results.get(prefix, 0) + 1
        icon = "  [+]" if prefix == "DONE" else "  [-]"
        print(f"{icon} {filename}: {status}")

    print(f"\n  ✓ Injected: {results['DONE']} | Skipped: {results.get('SKIP', 0)}\n")


if __name__ == "__main__":
    main()
