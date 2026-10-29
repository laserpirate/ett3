# ett3 site · A3 · build v07 · Animations page with the ink passes (reel v02 first, v14 tests under "Earlier tests"); build_a3_v06 kept and reused
# python _build/build_a3_v07.py --manifest <path.json> [--check-live] [--shots] [--video-check]
import html, importlib.util, os, sys

_s = importlib.util.spec_from_file_location("v6", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v06.py"))
v6 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v6)
b1, b3, PAGE, BASE, OWNER, REPO = v6.b1, v6.b3, v6.PAGE, v6.BASE, v6.OWNER, v6.REPO
ANIM_RELEASE2 = "a3-orbits-v02"
REEL2 = ("reel-v02", "Reel v02, ink", "Wide reveal, high orbit B, eye level, low close, walk-through, high orbit A, 360; 0.5 s dissolves, 2 s hold · 108 s",
         "reel", None, None)
CARDS2 = [
    [("orbit-360-ink", "360 orbit", "r 4 m · 2.4 m above ground · about 22 deg down · full turn at constant speed, loops · 24 mm · 20 s",
      "orbit-360-ink", "orbit-360-ink", "orbit-360-ink"),
     ("walk-through-ink", "Walk-through", "The opening walk of the iPhone capture path along the log, smoothed, 3.3 m · 1.4 m eye height · 28 mm · 25 s",
      "walk-through-ink", "walk-through-ink", "walk-through-ink")],
    [("high-orbit-A-ink", "High orbit A", "r 4.5 m · 3.5 m above ground · about 31 deg down · arc 100 to 240 deg · 28 mm · 14 s",
      "high-orbit-A-ink", "high-orbit-A-ink", "high-orbit-A-ink"),
     ("high-orbit-B-ink", "High orbit B", "r 5.5 m · 5.0 m above ground · about 38 deg down · arc 100 to 240 deg · 24 mm · 14 s",
      "high-orbit-B-ink", "high-orbit-B-ink", "high-orbit-B-ink")],
    [("wide-reveal-ink", "Wide reveal, ink", "r 6 m · 2.6 to 2.0 m above ground · arc 122 to 218 deg · 24 mm · 14 s",
      "wide-reveal-ink", "wide-reveal-ink", "wide-reveal-ink"),
     ("eye-level-ink-2", "Eye level, ink", "r 3.5 to 3.0 m · 1.65 m above ground · arc 5 to 85 deg · 35 mm · 12 s",
      "eye-level-ink", "eye-level-ink", "eye-level-ink")],
]
INTRO2 = ("Orbit tests of the Gaussian splat around the fallen log, rendered with the gsplat rasterizer at 3840 x 2160, 24 fps, on the near-black ground. "
          "The 360 and the high orbits run past the sides the iPhone capture covered, so thin edges and loose blobs show there. Web copies are 1920 px.")


def page(a1, a2, built):
    e = html.escape
    o = [b1.head("Animations", "Orbit test animations of the Gaussian splat around the fallen log, A3 transect, Alewife Brook.",
                 "../../assets/site.css", BASE + "a3-groundtruth/animations/%s" % a2[REEL2[0]]["poster"])]
    o.append('<div class="wrap anim"><header><h1>Animations</h1><p class="sub">Alewife Brook Conservation Area · fallen log · Gaussian splat</p>'
             '<p class="status">%s</p><p><a class="btn main" href="https://github.com/%s/%s/releases/tag/%s">4K masters (ink)</a> '
             '<a class="btn" href="https://github.com/%s/%s/releases/tag/%s">4K masters (earlier tests)</a></p></header>'
             % (e(INTRO2), OWNER, REPO, ANIM_RELEASE2, OWNER, REPO, v6.ANIM_RELEASE))
    o.append(b3.nav("animations/", "../"))
    o.append('<h2>%s</h2><div class="g2" style="grid-template-columns:1fr">%s</div>' % (e(REEL2[1]), v6.vcard(REEL2, a2)))
    o.append("<h2>Ink shots</h2>")
    for row in CARDS2:
        o.append('<div class="g2">%s</div>' % "".join(v6.vcard(c, a2) for c in row))
    o.append('<h2>Earlier tests</h2><p class="status">%s</p>' % e(v6.INTRO))
    o.append('<div class="g2" style="grid-template-columns:1fr">%s</div>' % v6.vcard(v6.REEL, a1))
    for row in v6.CARDS:
        o.append('<div class="g2">%s</div>' % "".join(v6.vcard(c, a1) for c in row) if len(row) > 1 else
                 '<div class="g2" style="grid-template-columns:1fr">%s</div>' % v6.vcard(row[0], a1))
    o.append('<footer>Built %s · <a href="https://github.com/%s/%s">repo</a></footer></div></body></html>' % (built, OWNER, REPO))
    return "\n".join(o)


def main():
    if "--video-check" in sys.argv or "--check-live" in sys.argv or "--shots" in sys.argv:
        return v6.main()
    v6.main()  # v06 pages, masthead, v01 animations assets + page (overwritten below)
    a1 = v6.anim_assets(v6.REEL, v6.CARDS)
    a2 = v6.anim_assets(REEL2, CARDS2, webdir="web_v02")
    built = __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    open(os.path.join(PAGE, "animations", "index.html"), "w", encoding="utf-8", newline="\n").write(page(a1, a2, built))
    b1.gate()


if __name__ == "__main__":
    main()
