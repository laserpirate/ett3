# ett3 site · A3 Ground Truth · v03 · Site Views, Site Photos, Nest Habitat Adaptation pages + nav + packet v04
# python _build/build_a3_v03.py [--release] [--check-live] [--shots]
#   v02 (and through it v01) is kept and imported for its helpers. New here:
#   views/  3 x 3 splat views, contoured (set B 0.25 ft / 1 ft index), set A (1 ft) linked beside each contoured view
#   photos/ 3 x 3 plants + 2 x 3 patch conditions from the keyframes (no field photos found), WebP 2400 px + thumbs, EXIF / GPS stripped
#   nest/   empty slots (no nest photos found), hero + 2 x 2
#   nav on every A3 page: Packet / Site Views / Site Photos / Splat Gallery / Nest Habitat Adaptation
#   packet buttons on Release a3-groundtruth-packet-v04; crawl of every page and every asset it references.
import datetime, html, importlib.util, json, os, re, subprocess, sys, urllib.request
from PIL import Image, ImageOps

_spec = importlib.util.spec_from_file_location("b2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v02.py"))
b2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(b2)
b1 = b2.b1
SITE, LANE, PAGE, BASE, OWNER, REPO = b1.SITE, b1.LANE, b1.PAGE, b1.BASE, b1.OWNER, b1.REPO
CONT_SRC = os.path.join(LANE, "00_share", "gsplat", "contoured")
GS_SRC = b2.GS_SRC
KF = r"Z:\_F26_Fall-2026\2_ett3-26\_assets-ett3\poly_alewife\Alewife-imgs-keyframes\images_jpg_q85"
RELEASES = [("a3-groundtruth-packet-v04", "A3 Ground Truth packet v04"), ("a3-groundtruth-packet-v03", "A3 Ground Truth packet v03 (9 sheets)"),
            ("a3-groundtruth-packet-v01", "A3 Ground Truth packet v01 (8 sheets)")]
b1.RELEASES = b2.RELEASES = RELEASES
NAV = [("", "Packet"), ("views/", "Site Views"), ("photos/", "Site Photos"), ("gsplat/", "Splat Gallery"), ("nest/", "Nest Habitat Adaptation")]
EXTRA_CSS = b2.EXTRA_CSS + """.nav{display:flex;flex-wrap:wrap;gap:0;margin:18px 0 0;border:1px solid var(--ink)}
.nav a{flex:1 1 auto;padding:8px 14px;text-align:center;color:var(--ink);text-decoration:none;font-weight:600;font-size:15px;border-right:1px solid var(--ink)}
.nav a:last-child{border-right:0}.nav a:hover,.nav a:focus{background:var(--ink);color:var(--paper)}.nav a[aria-current]{background:var(--ink);color:var(--paper)}
.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.g3 .card img{aspect-ratio:auto;object-fit:contain;background:var(--ground)}
.g3.ph .card img{aspect-ratio:3/4;object-fit:cover}
.card figcaption{word-break:normal}.card figcaption b{font-weight:600}.card figcaption .t{color:var(--accent);font-weight:600}
.card figcaption a{font-size:12px}
.slot{display:flex;align-items:center;justify-content:center;border:2px dashed var(--proxy);background:var(--ground);color:var(--proxy);
 font-size:14px;text-align:center;padding:16px;min-height:220px}.slot.hero{min-height:clamp(240px,40vw,560px)}
.g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px}
@media (max-width:800px){.g3{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.g3,.g2{grid-template-columns:1fr}.nav a{flex:1 1 100%;border-right:0;border-bottom:1px solid var(--ink)}.nav a:last-child{border-bottom:0}}
"""

# ---------- views ----------
VIEWS = [  # (row, stem, contoured, caption: view, scale or lens, contours, one factual line)
    (1, "CAM_persp_A", True, "perspective, 22 mm lens (36 mm sensor), no scale", "contours 0.25 ft, index 1 ft",
     "Fallen log across the interior; ground falls about 2 ft from the interior (left) to the wetland end (right)."),
    (1, "CAM_top", True, "plan, ortho, frame 9.11 m wide", "contours 0.25 ft, index 1 ft",
     "Scan footprint in plan; the log runs diagonally across the transect, 6.1 m long."),
    (1, "CAM_side", True, "side, ortho, frame 9.11 m wide, looking across the transect", "ground section line, ft scale ticks every 0.25 ft",
     "Ground along the transect axis: 2.5 ft at the interior, 0.4 ft at the wetland end; bank drop 0.43 m (1.4 ft) at s 5.5 to 6.75 m."),
    (2, "ZOOM_wetland_wide", True, "wetland, wide, 24 mm lens", "contours 0.25 ft, index 1 ft",
     "Weak reconstruction, open water. Wet patch past the bank, near s 7.2 m."),
    (2, "ZOOM_log_wide", False, "log, wide, 24 mm lens", "no contours",
     "Fallen log, 6.1 m long, 2 deg slope, seen from the side."),
    (2, "ZOOM_log_close", False, "log, close, 100 mm lens", "no contours",
     "Same eye as log wide: bark and moss on the log surface."),
    (3, "ZOOM_bank_mid", False, "bank, mid, 50 mm lens", "no contours",
     "Bank between s 5.5 and 6.75 m, where the ground drops 0.43 m to the wet end."),
    (3, "ORBIT_090", False, "orbit 090 deg, 24 mm lens, 3 m above the centre ground, 25 deg down", "no contours",
     "Whole transect crop from the side of the axis."),
    (3, "CAM_persp_D", False, "axonometric, ortho 9.5 m, plan turned 30 deg, 35 deg down", "no contours",
     "Whole transect crop: log, bank and the wet end in one frame."),
]

# ---------- photos (keyframes; IDs tentative) ----------
# file, kind, title, latin, stratum / patch, location or what is visible, measured value
PHOTOS = [
    ("plant", "glossy buckthorn", "Frangula alnus", "understory shrub", "interior"),
    ("plant", "oriental bittersweet", "Celastrus orbiculatus", "ground layer, vine", "interior"),
    ("plant", "black cherry", "Prunus serotina", "midstory tree (trunk)", "wetland side"),
    ("plant", "goldenrod", "Solidago sp.", "ground layer, herb", "edge"),
    ("plant", "Virginia creeper", "Parthenocissus quinquefolia", "ground layer, vine", "interior"),
    ("plant", "ash seedling", "Fraxinus sp.", "ground layer, seedling", "interior"),
    ("plant", "dogwood", "Cornus sp.", "understory shrub", "interior, toward the water"),
    ("plant", "moss on the fallen log", "Bryophyta", "ground layer, on wood", "interior"),
    ("plant", "common buckthorn", "Rhamnus cathartica", "understory shrub, multi-stem", "interior"),
    ("cond", "Interior litter", "", "leaf litter over the whole ground layer, herbs sparse", "interior ground 0.39 to 0.70 m over s 1 to 5.5 m (scan)"),
    ("cond", "Edge", "", "woody stems thin out, herbs and vines on the slope", "edge band s 5.5 to 6.75 m, 1.25 m wide (scan)"),
    ("cond", "Bank drop", "", "slope down to standing water below the woody ground", "bank drop 0.43 m (1.4 ft) across the edge (scan)"),
    ("cond", "Wetland", "", "open water with fallen branches; weak in the splat", "ground 0.03 m at the wet end, veg under 0.3 m (scan)"),
    ("cond", "Disturbance", "", "old timber posts with bolts standing in the interior", "[FIELD: what the posts were, when]"),
    ("cond", "Log habitat", "", "fallen log with moss, branches and litter around it", "log 6.1 m long, 2 deg slope (scan)"),
]
PHOTO_FILES = None  # filled from the lane pick (01_src/ett3-A3_photo-pick_v01.json + photo list)


def nav(cur, up):
    return '<nav class="nav" aria-label="A3 pages">' + "".join(
        '<a href="%s%s"%s>%s</a>' % (up, href or "./", ' aria-current="page"' if href == cur else "", lab) for href, lab in NAV) + "</nav>"


def lb(js):
    return ('<div id="lb" role="dialog" aria-label="Image viewer"><div class="bar"><span></span>'
            '<button type="button" class="pv" aria-label="Previous">Prev</button><button type="button" class="nx" aria-label="Next">Next</button>'
            '<a class="full" href="#">full size</a><button type="button" class="x" aria-label="Close">Close</button></div>'
            '<div class="fig"><img alt=""></div></div><script src="%s"></script></body></html>' % js)


def web(src_img, out_full, out_thumb, full_w, thumb_w, flatten=True):
    """WebP full + thumb, new pixel buffer (no EXIF / GPS / ICC carried over)"""
    if flatten:
        im = b2.flatten(src_img, full_w)
    else:
        im = ImageOps.exif_transpose(Image.open(src_img)).convert("RGB")
        if max(im.size) > full_w:
            im.thumbnail((full_w, full_w), Image.LANCZOS)
        im = Image.frombytes("RGB", im.size, im.tobytes())
    if not os.path.exists(out_full):
        im.save(out_full, quality=84, method=6)
    t = im.copy(); t.thumbnail((thumb_w, thumb_w * 2), Image.LANCZOS)
    if not os.path.exists(out_thumb):
        t.save(out_thumb, quality=82, method=6)
    return t.size


def views_assets():
    d = os.path.join(PAGE, "views"); os.makedirs(d, exist_ok=True)
    out = []
    for row, stem, cont, lens, ci, line in VIEWS:
        name = "ett3-A3_gsplat_%s_%s_v01" % (stem, "contour") if cont else "ett3-A3_gsplat_%s_v01" % stem
        src = os.path.join(CONT_SRC if cont else GS_SRC, name + ".png")
        w, h = web(src, os.path.join(d, name + ".webp"), os.path.join(d, name + "_thumb.webp"), 3000, 1000)
        alt = None
        if cont:
            an = "ett3-A3_gsplat_%s_contour-1ft_v01" % stem
            web(os.path.join(CONT_SRC, an + ".png"), os.path.join(d, an + ".webp"), os.path.join(d, an + "_thumb.webp"), 3000, 1000)
            alt = an
        out.append(dict(row=row, stem=stem, name=name, alt=alt, w=w, h=h, lens=lens, ci=ci, line=line))
    return out


def views_page(items, built):
    e = html.escape
    o = [b1.head("Site Views", "Gaussian splat views of the A3 transect at Alewife Brook, with ground contours in feet.", "../../assets/site.css",
                 BASE + "a3-groundtruth/views/%s_thumb.webp" % items[0]["name"])]
    o.append('<div class="wrap"><header><h1>Site Views</h1><p class="sub">Alewife Brook Conservation Area · transect s 0 to 8.6 m</p>'
             '<p class="status">Splat renders with ground contours from the scan ground grid (not the splat). Default set: 0.25 ft, index 1 ft. '
             'Ground relief in the scan is 0.1 to 2.8 ft, so the 1 ft / 5 ft set has 5 lines and no 5 ft line; it is linked under each contoured view.</p></header>')
    o.append(nav("views/", "../"))
    for r in (1, 2, 3):
        o.append('<div class="g3" style="margin-top:22px">')
        for it in [i for i in items if i["row"] == r]:
            cap = "%s · %s · %s · %s" % (it["stem"], it["lens"], it["ci"], it["line"])
            o.append('<figure class="card"><button type="button" data-full="%s.webp" data-name="%s"><img src="%s_thumb.webp" alt="%s" loading="lazy" width="%d" height="%d"></button>'
                     '<figcaption><b>%s</b> · %s · %s<br>%s%s</figcaption></figure>'
                     % (it["name"], e(cap), it["name"], e(it["stem"] + ", " + it["line"]), it["w"], it["h"], e(it["stem"]), e(it["lens"]), e(it["ci"]), e(it["line"]),
                        '<br><a href="%s.webp">1 ft / 5 ft set</a>' % it["alt"] if it["alt"] else ""))
        o.append('</div>')
    o.append('<footer>Built %s · splat v01, contours v02 · <a href="https://github.com/%s/%s">repo</a></footer></div>' % (built, OWNER, REPO))
    o.append(lb("../a3.js"))
    return "\n".join(o)


def photos_assets():
    d = os.path.join(PAGE, "photos"); os.makedirs(d, exist_ok=True)
    pick = json.load(open(os.path.join(LANE, "01_src", "ett3-A3_photo-pick_v02.json")))["photos"]
    out = []
    for k, (p, meta) in enumerate(zip(pick, PHOTOS), 1):
        name = "ett3-A3_photo_%02d_v01" % k
        w, h = web(os.path.join(KF, p["file"]), os.path.join(d, name + ".webp"), os.path.join(d, name + "_thumb.webp"), 2400, 800, flatten=False)
        out.append(dict(name=name, w=w, h=h, file=p["file"], meta=meta))
    return out


def photos_page(items, built):
    e = html.escape
    o = [b1.head("Site Photos", "Plants and patch conditions along the A3 transect at Alewife Brook. Plant IDs tentative.", "../../assets/site.css",
                 BASE + "a3-groundtruth/photos/%s_thumb.webp" % items[0]["name"])]
    o.append('<div class="wrap"><header><h1>Site Photos</h1><p class="sub">Alewife Brook Conservation Area · transect s 0 to 8.6 m</p>'
             '<p class="status">Frames from the Polycam scan walk, iPhone, Oct 23 2026 (no separate field photos found). '
             'Every plant ID is tentative until the group confirms it. Location from the frame\'s camera pose, approximate.</p></header>')
    o.append(nav("photos/", "../"))
    o.append('<h2>Plants</h2><div class="g3 ph">')
    for it in items[:9]:
        kind, cn, la, stratum, loc = it["meta"]
        cap = "%s, %s · %s · %s · ID tentative" % (cn, la, stratum, loc)
        o.append('<figure class="card"><button type="button" data-full="%s.webp" data-name="%s"><img src="%s_thumb.webp" alt="%s" loading="lazy" width="%d" height="%d"></button>'
                 '<figcaption><b>%s</b>, <i>%s</i> · %s · %s · <span class="t">ID tentative</span></figcaption></figure>'
                 % (it["name"], e(cap), it["name"], e(cn + ", ID tentative"), it["w"], it["h"], e(cn), e(la), e(stratum), e(loc)))
    o.append('</div><h2>Patch conditions</h2><div class="g3 ph">')
    for it in items[9:]:
        kind, patch, _, vis, val = it["meta"]
        cap = "%s · %s · %s" % (patch, vis, val)
        o.append('<figure class="card"><button type="button" data-full="%s.webp" data-name="%s"><img src="%s_thumb.webp" alt="%s" loading="lazy" width="%d" height="%d"></button>'
                 '<figcaption><b>%s</b> · %s · %s</figcaption></figure>' % (it["name"], e(cap), it["name"], e(patch + ": " + vis), it["w"], it["h"], e(patch), e(vis), e(val)))
    o.append('</div><footer>Built %s · keyframes q85, WebP 2400 px, metadata stripped · ID terms: Woody Plants readings (Trowbridge and Bassuk; Beck 2013 p.72) · '
             '<a href="https://github.com/%s/%s">repo</a></footer></div>' % (built, OWNER, REPO))
    o.append(lb("../a3.js"))
    return "\n".join(o)


def nest_page(built):
    slot = '[DROP PHOTOS: _assets-ett3\\nest\\]'
    o = [b1.head("Nest Habitat Adaptation", "A found abandoned nest from Alewife Brook, turned into a readymade sculpture.", "../../assets/site.css",
                 BASE + "a3-groundtruth/masthead.webp")]
    o.append('<div class="wrap"><header><h1>Nest Habitat Adaptation</h1>'
             '<p class="status">A found abandoned nest, Alewife Brook Conservation Area, found [CONFIRM: date], turned into a readymade sculpture.</p>'
             '<p class="sub">Group: [FIELD]</p></header>')
    o.append(nav("nest/", "../"))
    o.append('<div class="slot hero" style="margin-top:22px">Photo slot 1 (hero) · %s</div><div class="g2">' % slot)
    for k in range(2, 6):
        o.append('<div class="slot">Photo slot %d · %s</div>' % (k, slot))
    o.append('</div><footer>Built %s · no nest photos found yet · <a href="https://github.com/%s/%s">repo</a></footer></div></body></html>' % (built, OWNER, REPO))
    return "\n".join(o)


def add_nav(t, cur, up):
    i = t.index("</header>") + len("</header>")
    return t[:i] + nav(cur, up) + t[i:]


def share_page(sh, files, st, pv, built):
    t = b2.share_page(sh, files, st, pv, built)
    return add_nav(t, "", "")


def release(files):
    tag, title = RELEASES[0]
    if b1.gh("release", "view", tag, "-R", "%s/%s" % (OWNER, REPO)).returncode == 0:
        print("release exists, skipped:", tag); return
    notes = ("Contents: 9 sheets; D2 v04 option A (site plan on the splat, 1:40) in the default packet, option B (detail at the log, 1:10) "
             "as the alternate packet ett3-A3_packet_v04_altB.pdf; D3 v04 (section on the splat side view, plant table per zone). "
             "Packet PDF and review PDF, one .ai per sheet plus a 9-artboard .ai, InDesign .indd + .idml with Links and fonts, README.\n"
             "Proxy status: values measured from the Polycam scan; field values still pending are marked P (proxy), open slots listed in the review PDF.\n"
             "Pages: %sa3-groundtruth/ · views/ · photos/ · gsplat/ · nest/\nPin-up Fri Oct 30 2026, 12 pm, 11x17." % BASE)
    r = b1.gh("release", "create", tag, files["zip_src"], files["pdf_src"], files["review_src"], files["alt_src"], "-R", "%s/%s" % (OWNER, REPO),
              "--title", title, "--notes", notes, "--latest")
    print(r.stdout, r.stderr)


def fetch(u, n=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ett3-check"}), timeout=180) as r:
            return r.status, (r.read() if n is None else r.read(n))
    except Exception as ex:
        return getattr(ex, "code", str(ex)), b""


def check_live(files):
    pages = ["", "a3-groundtruth/", "a3-groundtruth/views/", "a3-groundtruth/photos/", "a3-groundtruth/gsplat/", "a3-groundtruth/nest/"]
    seen, ok, n = set(), 0, 0
    for p in pages:
        u = BASE + p
        code, body = fetch(u); n += 1
        t = body.decode("utf-8", "replace")
        good = code == 200 and b1.ROBOTS_META in t
        ok += good
        if not good: print("FAIL page", code, u)
        refs = set(re.findall(r'(?:src|href|data-full)="([^"#]+)"', t))
        for r_ in refs:
            if r_.startswith("http") and "github.io" not in r_:
                au = r_
            elif r_.startswith("http"):
                au = r_
            else:
                au = urllib.request.urljoin(u, r_)
            if au in seen or au.startswith("mailto"):
                continue
            seen.add(au)
            code2, _ = fetch(au, 1); n += 1
            ok += code2 == 200
            if code2 != 200: print("FAIL", code2, au)
        css = urllib.request.urljoin(u, "../../assets/site.css") if p.count("/") == 2 else None
    for f in ("fonts/PublicSans-Regular.woff2", "fonts/PublicSans-SemiBold.woff2", "fonts/PublicSans-Italic.woff2", "site.css"):
        au = BASE + "assets/" + f
        if au not in seen:
            code2, _ = fetch(au, 1); n += 1; ok += code2 == 200
            if code2 != 200: print("FAIL", code2, au)
    for t_, _ in RELEASES:
        au = "https://github.com/%s/%s/releases/tag/%s" % (OWNER, REPO, t_)
        code2, _ = fetch(au, 1); n += 1; ok += code2 == 200
        if code2 != 200: print("FAIL", code2, au)
    au = b1.rel_url(RELEASES[0][0], files["alt"]); code2, _ = fetch(au, 1); n += 1; ok += code2 == 200
    print("crawl %d/%d" % (ok, n))


def shots():
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    stamp = datetime.date.today().strftime("%Y%m%d")
    for path, name in (("a3-groundtruth/", "share-page"), ("a3-groundtruth/views/", "site-views"), ("a3-groundtruth/photos/", "site-photos"),
                       ("a3-groundtruth/nest/", "nest")):
        for w, h, tag in ((1440, 4200, "desktop-1440"), (390, 9000, "phone-390")):
            out = os.path.join(LANE, "00_share", "site", "ett3-A3_%s_%s_%s_v01.png" % (name, tag, stamp))
            k = 1
            while os.path.exists(out):
                k += 1; out = re.sub(r"_v\d+\.png$", "_v%02d.png" % k, out)
            frame = os.path.join(os.environ.get("TEMP", "."), "ett3_shot_%s_%d.html" % (name, w))
            open(frame, "w").write('<!doctype html><body style="margin:0"><iframe src="%s%s" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>' % (BASE, path, w, h))
            subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=%d,%d" % (max(w, 800), h), "--virtual-time-budget=25000",
                            "--screenshot=" + out, "file:///" + frame.replace("\\", "/")], capture_output=True, timeout=240)
            if os.path.exists(out):
                Image.open(out).crop((0, 0, w, h)).save(out)
            print("shot", out, os.path.exists(out))


def main():
    _new = b1.newest
    b1.newest = lambda pat: _new(pat) if "packet_v" not in pat else max(
        [q for q in __import__("glob").glob(os.path.join(b1.PACKET, pat)) if "_alt" not in q], key=b1.vnum)  # skip the _altB alternate
    pdf, review = b1.newest("ett3-A3_packet_v*.pdf"), b1.newest("ett3-A3_packet_review_v*.pdf")
    readme, zp = b1.newest("README_group_v*.pdf"), b1.newest("ett3-A3_packet_v*.zip")
    alt = os.path.join(b1.PACKET, "ett3-A3_packet_v04_altB.pdf")
    pv = "v%02d" % b1.vnum(pdf)
    assert pv == "v04" and b1.vnum(zp) == 4 and os.path.exists(alt), (pdf, zp)
    files = dict(zip=os.path.basename(zp), zip_src=zp, zip_mb=os.path.getsize(zp) / 1e6, pdf=os.path.basename(pdf), pdf_src=pdf,
                 pdf_mb=os.path.getsize(pdf) / 1e6, review=os.path.basename(review), review_src=review, review_mb=os.path.getsize(review) / 1e6,
                 alt=os.path.basename(alt), alt_src=alt)
    if "--check-live" in sys.argv or "--shots" in sys.argv:
        if "--check-live" in sys.argv: check_live(files)
        if "--shots" in sys.argv: shots()
        return
    b1.clean_pdf(readme, os.path.join(PAGE, "files", os.path.basename(readme)))
    files["readme"] = os.path.basename(readme)
    import shutil
    shutil.copy(b1.newest("README_group_v*.md"), os.path.join(PAGE, "files"))
    files["mast"] = b1.masthead()
    sh = b1.sheets(pdf)
    st = b1.status()
    groups, cs = b2.gallery_assets()
    va, pa = views_assets(), photos_assets()
    built = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    css = b1.CSS % {k: v["hex"] for k, v in b1.PAL.items()} + EXTRA_CSS
    for p, t in ((os.path.join(SITE, "assets", "site.css"), css), (os.path.join(PAGE, "a3.js"), b1.JS),
                 (os.path.join(PAGE, "index.html"), share_page(sh, files, st, pv, built)),
                 (os.path.join(PAGE, "gsplat", "index.html"), add_nav(b2.gallery_page(groups, cs, built), "gsplat/", "../")),
                 (os.path.join(PAGE, "views", "index.html"), views_page(va, built)),
                 (os.path.join(PAGE, "photos", "index.html"), photos_page(pa, built)),
                 (os.path.join(PAGE, "nest", "index.html"), nest_page(built)),
                 (os.path.join(SITE, "index.html"), b1.landing(built))):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(t)
    print({k: v for k, v in files.items() if not k.endswith("_src")}, "views", len(va), "photos", len(pa))
    b1.gate()
    if "--release" in sys.argv:
        release(files)


if __name__ == "__main__":
    main()
