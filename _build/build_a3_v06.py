# ett3 site · A3 · build v06 · Animations page (splat orbit tests) + masthead video loop (ink); build_a3_v05 kept and reused
# python _build/build_a3_v06.py --manifest <path.json> [--check-live] [--shots] [--video-check]
#   Masthead: <video autoplay muted loop playsinline> on the share page and the landing card, still poster under prefers-reduced-motion.
#   The old still masthead.webp stays in the repo (og:image still points at it). 4K masters ride on Release ANIM_RELEASE, not in the repo.
import html, importlib.util, os, shutil, subprocess, sys
from PIL import Image

_s = importlib.util.spec_from_file_location("v5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v05.py"))
v5 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v5)
v4 = v5.v4; b3, b1 = v4.b3, v4.b1
SITE, LANE, PAGE, BASE, OWNER, REPO = b1.SITE, b1.LANE, b1.PAGE, b1.BASE, b1.OWNER, b1.REPO
ANIM = os.path.join(LANE, "00_share", "gsplat", "anim")
ANIM_RELEASE = "a3-orbits-v01"
NAV = v4.NAV[:-1] + [("animations/", "Animations"), v4.NAV[-1]]
v4.NAV[:] = NAV; b3.NAV = NAV

MAST = dict(mp4="ett3-A3_masthead-loop_v01.mp4", webm="ett3-A3_masthead-loop_v01.webm", poster="ett3-A3_masthead-loop_poster_v01.webp",
            card="ett3-A3_masthead-loop_card_v01.webp", w=1600, h=624)
MAST_ALT = "Gaussian splat of the fallen log at Alewife Brook, eye-level orbit on a dark ground"
# (key, title, caption, web mp4 in anim/web_v01, PNG master frames dir, strip PNG)
REEL = ("reel", "Reel v01", "Shots 1 to 3 on white, 0.5 s dissolves, 2 s hold on the last frame · 37 s", "reel", None, None)
CARDS = [
    [("wide-reveal", "1 · Wide reveal", "r 6 m · 2.6 to 2.0 m above ground · arc 122 to 218 deg · 24 mm · 14 s", "wide-reveal", "wide-reveal", "wide-reveal")],
    [("eye-level", "2 · Eye level", "r 3.5 to 3.0 m · 1.65 m above ground · arc 5 to 85 deg · 35 mm · 12 s", "eye-level", "eye-level", "eye-level"),
     ("eye-level-ink", "2 · Eye level, ink", "Same camera, near-black ground", "eye-level-ink", "eye-level-ink", None)],
    [("low-close", "3 · Low close", "r 1.8 m around the root end · 0.9 to 1.5 m above ground · arc 85 deg · 28 mm · 10 s", "low-close", "low-close", "low-close"),
     ("low-close-ink", "3 · Low close, ink", "Same camera, near-black ground", "low-close-ink", "low-close-ink", "low-close-ink")],
]
INTRO = ("Orbit tests of the Gaussian splat around the fallen log, rendered with the gsplat rasterizer at 3840 x 2160, 24 fps. "
         "Arcs stay inside the sides the iPhone capture covered (120 to 220 deg and 330 to 70 deg around the log). Web copies are 1920 px.")
EXTRA_CSS = """.mastv{position:relative}video.mast{object-position:50% 72%}.mast-still{display:none}
@media (prefers-reduced-motion:reduce){video.mast{display:none}.mast-still{display:block}}
.list video{display:block;width:100%;height:auto;background:#05070C}
.vcard{margin:0;border:1px solid var(--rule);background:var(--ground)}
.vcard video{display:block;width:100%;height:auto;aspect-ratio:16/9;background:#05070C}
.vcard figcaption{padding:8px 10px;font-size:14px}.vcard .strip{display:block;width:100%;height:auto;border-top:1px solid var(--rule)}
.anim h2{margin-top:34px}.anim .g2{margin-top:14px}
"""
RM_JS = ("<script>(function(){if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches){"
         "[].forEach.call(document.querySelectorAll('video[autoplay]'),function(v){v.removeAttribute('autoplay');v.pause();});}})();</script>")


def mast_html(up, cls="mast"):
    return ('<div class="mastv"><video class="%s" autoplay muted loop playsinline preload="metadata" poster="%s%s" width="%d" height="%d" aria-label="%s">'
            '<source src="%s%s" type="video/mp4"><source src="%s%s" type="video/webm"></video>'
            '<img class="%s mast-still" src="%s%s" alt="%s" width="%d" height="%d"></div>'
            % (cls, up, MAST["poster"], MAST["w"], MAST["h"], MAST_ALT, up, MAST["mp4"], up, MAST["webm"],
               cls, up, MAST["poster"], MAST_ALT, MAST["w"], MAST["h"]))


def copy_masthead():
    for k in ("mp4", "webm", "poster", "card"):
        shutil.copy2(os.path.join(ANIM, MAST[k]), os.path.join(PAGE, MAST[k]))


def anim_assets(reel, cards, webdir="web_v01"):
    d = os.path.join(PAGE, "animations"); os.makedirs(d, exist_ok=True)
    out = {}
    for c in [reel] + [x for row in cards for x in row]:
        key, _, _, web, frames, strip = c
        mp4 = "ett3-A3_orbit_%s_1920_%s.mp4" % (web, webdir.split("_")[-1])
        src = os.path.join(ANIM, webdir, mp4)
        assert os.path.getsize(src) < 45e6, "web encode over 45 MB: " + mp4
        shutil.copy2(src, os.path.join(d, mp4))
        poster = "ett3-A3_orbit_%s_poster.webp" % key
        if not os.path.exists(os.path.join(d, poster)):
            if frames:
                fs = sorted(f for f in os.listdir(os.path.join(ANIM, "frames_%s_v01" % frames)) if f.endswith(".png"))
                im = Image.open(os.path.join(ANIM, "frames_%s_v01" % frames, fs[len(fs) // 2])).convert("RGB")
            else:  # reel: middle frame of the web encode
                tmp = os.path.join(os.environ.get("TEMP", "."), "ett3_reel_mid.png")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "18", "-i", src, "-frames:v", "1", tmp], check=True)
                im = Image.open(tmp).convert("RGB")
            im = Image.frombytes("RGB", im.size, im.tobytes()).resize((1920, 1080), Image.LANCZOS)
            im.save(os.path.join(d, poster), quality=82, method=6)
        st = None
        if strip:
            st = "ett3-A3_orbit_%s_strip.webp" % key
            if not os.path.exists(os.path.join(d, st)):
                im = Image.open(os.path.join(ANIM, "ett3-A3_orbit_%s_strip_v01.png" % strip)).convert("RGB")
                im = Image.frombytes("RGB", im.size, im.tobytes())
                im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS).save(os.path.join(d, st), quality=82, method=6)
        out[key] = dict(mp4=mp4, poster=poster, strip=st)
    return out


def vcard(c, a):
    e = html.escape
    key, title, cap = c[0], c[1], c[2]
    s = ('<figure class="vcard"><video controls muted playsinline preload="none" poster="%s" width="1920" height="1080">'
         '<source src="%s" type="video/mp4"></video><figcaption><b>%s</b><br>%s</figcaption>' % (a[key]["poster"], a[key]["mp4"], e(title), e(cap)))
    if a[key]["strip"]:
        s += '<img class="strip" src="%s" alt="%s: start, middle and end frames" loading="lazy" width="2400" height="452">' % (a[key]["strip"], e(title))
    return s + "</figure>"


def animations_page(a, built, reel=REEL, cards=CARDS, release=ANIM_RELEASE, extra_sections=()):
    e = html.escape
    o = [b1.head("Animations", "Orbit test animations of the Gaussian splat around the fallen log, A3 transect, Alewife Brook.",
                 "../../assets/site.css", BASE + "a3-groundtruth/animations/%s" % a[reel[0]]["poster"])]
    o.append('<div class="wrap anim"><header><h1>Animations</h1><p class="sub">Alewife Brook Conservation Area · fallen log · Gaussian splat</p>'
             '<p class="status">%s</p><p><a class="btn main" href="https://github.com/%s/%s/releases/tag/%s">4K masters</a></p></header>'
             % (e(INTRO), OWNER, REPO, release))
    o.append(b3.nav("animations/", "../"))
    for sec in extra_sections:
        o.append(sec)
    o.append('<h2>%s</h2><div class="g2" style="grid-template-columns:1fr">%s</div>' % (e(reel[1]), vcard(reel, a)))
    o.append("<h2>Shots</h2>")
    for row in cards:
        o.append('<div class="g2">%s</div>' % "".join(vcard(c, a) for c in row) if len(row) > 1 else '<div class="g2" style="grid-template-columns:1fr">%s</div>' % vcard(row[0], a))
    o.append('<footer>Built %s · <a href="https://github.com/%s/%s">repo</a></footer></div></body></html>' % (built, OWNER, REPO))
    return "\n".join(o)


_share = v4.share_page
_landing = b1.landing


def share_page(*a, **k):
    t = _share(*a, **k)
    old = t[t.index('<img class="mast"'):t.index(">", t.index('<img class="mast"')) + 1]
    t = t.replace(old, mast_html(""))
    return t.replace("</body>", RM_JS + "</body>")


def landing(built):
    t = _landing(built)
    old = t[t.index('<img src="assets/a3-card.webp"'):t.index(">", t.index('<img src="assets/a3-card.webp"')) + 1]
    vid = ('<video autoplay muted loop playsinline preload="metadata" poster="a3-groundtruth/%s" width="800" height="312" aria-label="%s">'
           '<source src="a3-groundtruth/%s" type="video/mp4"></video>' % (MAST["card"], MAST_ALT, MAST["mp4"]))
    t = t.replace(old, vid)
    return t.replace("</body>", RM_JS + "</body>")


v4.share_page = share_page
b1.landing = landing
v4.EXTRA_CSS = v4.EXTRA_CSS + EXTRA_CSS
_check = v4.check_live
_shots = v4.shots


def check_live(files):
    pages_extra = ["a3-groundtruth/animations/"]
    _check(files)
    ok = n = 0
    seen = set()
    for p in pages_extra:
        u = BASE + p
        code, body = b3.fetch(u); n += 1; ok += code == 200 and b1.ROBOTS_META.encode() in body
        import re
        for r_ in set(re.findall(r'(?:src|href|poster)="([^"#]+)"', body.decode("utf-8", "replace"))):
            au = r_ if r_.startswith("http") else b3.urllib.request.urljoin(u, r_)
            if au in seen: continue
            seen.add(au); c2, _ = b3.fetch(au, 1); n += 1; ok += c2 == 200
            if c2 != 200: print("FAIL", c2, au)
    for f in (MAST["mp4"], MAST["webm"], MAST["poster"], MAST["card"]):
        c2, _ = b3.fetch(BASE + "a3-groundtruth/" + f, 1); n += 1; ok += c2 == 200
        if c2 != 200: print("FAIL", c2, f)
    print("crawl animations + masthead %d/%d" % (ok, n))


def video_check(base=None):
    """headless Chrome via vcheck_v01.mjs: the masthead / card videos must be playing (readyState >= 2, paused false)"""
    base = base or BASE
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "vcheck_v01.mjs"), base + "a3-groundtruth/", base],
                       capture_output=True, text=True, timeout=180)
    print(r.stdout.strip(), r.stderr.strip()[-400:])
    return r.returncode == 0


def shots(base=None):
    _shots(base)
    import datetime, re
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    base = base or BASE
    stamp = datetime.date.today().strftime("%Y%m%d")
    outdir = os.path.join(LANE, "00_share", "site") if base == BASE else os.environ.get("ETT3_SHOT_DIR", os.environ.get("TEMP", "."))
    for w, h, tag in ((1440, 5200, "desktop-1440"), (390, 12000, "phone-390")):
        out = os.path.join(outdir, "ett3-A3_animations_%s_%s_v01.png" % (tag, stamp))
        k = 1
        while os.path.exists(out):
            k += 1; out = re.sub(r"_v\d+\.png$", "_v%02d.png" % k, out)
        frame = os.path.join(os.environ.get("TEMP", "."), "ett3_shot_anim_%d.html" % w)
        open(frame, "w").write('<!doctype html><body style="margin:0"><iframe src="%sa3-groundtruth/animations/" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>' % (base, w, h))
        subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=%d,%d" % (max(w, 800), h), "--virtual-time-budget=25000",
                        "--screenshot=" + out, "file:///" + frame.replace("\\", "/")], capture_output=True, timeout=240)
        if os.path.exists(out):
            Image.open(out).crop((0, 0, w, h)).save(out)
        print("shot", out, os.path.exists(out))


def main():
    if "--video-check" in sys.argv:
        sys.exit(0 if video_check(os.environ.get("ETT3_SHOT_BASE")) else 1)
    if not ("--check-live" in sys.argv or "--shots" in sys.argv):
        copy_masthead()
    v4.check_live = check_live
    v4.shots = shots
    v4.main()
    if "--check-live" in sys.argv or "--shots" in sys.argv:
        return
    css_p = os.path.join(SITE, "assets", "site.css")
    css = open(css_p, encoding="utf-8").read()
    if ".mastv" not in css:
        open(css_p, "a", encoding="utf-8", newline="\n").write(EXTRA_CSS)
    a = anim_assets(REEL, CARDS)
    built = __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    p = os.path.join(PAGE, "animations", "index.html")
    open(p, "w", encoding="utf-8", newline="\n").write(animations_page(a, built))
    b1.gate()


if __name__ == "__main__":
    main()
