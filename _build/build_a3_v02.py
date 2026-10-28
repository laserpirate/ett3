# ett3 site · A3 Ground Truth share page + splat gallery · v02
# python _build/build_a3_v02.py [--release] [--check-live] [--shots]
#   v01 is kept and imported for its helpers (sheets, fonts, masthead, head, gate, CSS, JS). New here:
#   packet v03 (9 sheets, adds 08 S2 splat atlas), a "Splat gallery" button, packet buttons on the v03 Release,
#   the gallery page a3-groundtruth/gsplat/ (contact sheet + 23 shots, WebP on paper), crawl and shots of both pages.
#   The 4000 px splat PNGs are not copied: WebP 3000 px full size, 1000 px thumbnails.
import datetime, html, importlib.util, os, re, shutil, subprocess, sys, urllib.request
from PIL import Image

_spec = importlib.util.spec_from_file_location("b1", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v01.py"))
b1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(b1)
SITE, LANE, PAGE, BASE, OWNER, REPO = b1.SITE, b1.LANE, b1.PAGE, b1.BASE, b1.OWNER, b1.REPO
GS_SRC = os.path.join(LANE, "00_share", "gsplat")
GS = os.path.join(PAGE, "gsplat")
CONTACT = "ett3-A3_gsplat-shots_v01"
GS_FULL_W, GS_THUMB_W, CONTACT_W = 3000, 1000, 2000
b1.SHEETS = b1.SHEETS + ["08_S2-splat-atlas"]
RELEASES = [("a3-groundtruth-packet-v03", "A3 Ground Truth packet v03"), ("a3-groundtruth-packet-v01", "A3 Ground Truth packet v01 (8 sheets)")]
b1.RELEASES = RELEASES
GROUPS = [("Candidate cameras", "CAM_persp_[A-D]", ""), ("Ortho", "CAM_(top|side)", ""), ("Orbit", "ORBIT_\\d+", ""),
          ("Log zooms", "ZOOM_log_", ""), ("Bank zooms", "ZOOM_bank_", ""),
          ("Wetland zooms", "ZOOM_wetland_", "Weak reconstruction, few views of open water.")]
ZOOM_ORDER = {"wide": 0, "mid": 1, "close": 2}
EXTRA_CSS = """.contact{display:block;border:1px solid var(--rule);background:var(--paper);cursor:zoom-in}.contact img{display:block;width:100%;height:auto}
.shots .card img{aspect-ratio:3/2;object-fit:contain;background:var(--ground)}
.note{margin:-4px 0 12px;font-size:15px;color:var(--proxy);font-style:italic}
"""


def paper_hex():
    return b1.PAL["t_upland"]["hex"]  # the site's --ground tone, light paper


def flatten(src, w):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, paper_hex())
    im = Image.alpha_composite(bg, im).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    return Image.frombytes("RGB", im.size, im.tobytes())  # no metadata


def shot_key(n):
    m = re.search(r"ZOOM_\w+?_(wide|mid|close)", n)
    return (ZOOM_ORDER[m.group(1)] if m else 0, n)


def gallery_assets():
    os.makedirs(GS, exist_ok=True)
    pngs = sorted(p for p in os.listdir(GS_SRC) if p.startswith("ett3-A3_gsplat_") and p.endswith(".png") and "overlay" not in p)
    groups = []
    for title, pat, note in GROUPS:
        names = sorted([p[:-4] for p in pngs if re.search("_" + pat, p)], key=shot_key)
        items = []
        for n in names:
            full, th = os.path.join(GS, n + ".webp"), os.path.join(GS, n + "_thumb.webp")
            im = flatten(os.path.join(GS_SRC, n + ".png"), GS_FULL_W)
            if not os.path.exists(full):
                im.save(full, quality=86, method=6)
            t = im.resize((GS_THUMB_W, round(im.height * GS_THUMB_W / im.width)), Image.LANCZOS)
            if not os.path.exists(th):
                t.save(th, quality=84, method=6)
            items.append(dict(name=n, w=t.width, h=t.height))
        groups.append((title, note, items))
    n_used = sum(len(g[2]) for g in groups)
    assert n_used == 23 == len(pngs), (n_used, len(pngs))
    c = Image.open(os.path.join(GS_SRC, CONTACT + ".png")).convert("RGB")
    c = Image.frombytes("RGB", c.size, c.tobytes())
    if not os.path.exists(os.path.join(GS, CONTACT + ".webp")):
        c.save(os.path.join(GS, CONTACT + ".webp"), quality=88, method=6)  # full size, native 4044 px
        c.resize((CONTACT_W, round(c.height * CONTACT_W / c.width)), Image.LANCZOS).save(os.path.join(GS, CONTACT + "_view.webp"), quality=86, method=6)
    cv = Image.open(os.path.join(GS, CONTACT + "_view.webp"))
    return groups, dict(w=cv.width, h=cv.height)


def gallery_page(groups, cs, built):
    e = html.escape
    o = [b1.head("ett3 A3 splat gallery", "Gaussian splat shots of the A3 transect, Alewife Brook. Trained from 544 iPhone keyframes, aligned to the LiDAR scan.",
                 "../../assets/site.css", BASE + "a3-groundtruth/gsplat/%s_view.webp" % CONTACT)]
    o.append('<img class="mast" src="../masthead.webp" alt="Gaussian splat preview of the transect, Alewife Brook" width="2400" height="855">')
    o.append('<div class="wrap"><header><h1>A3 · Splat gallery</h1><p class="sub">Alewife Brook Conservation Area · transect s 0 to 8.6 m</p>'
             '<p class="status">Gaussian splat trained from 544 keyframes (COLMAP + Brush), aligned to the LiDAR scan. '
             'Wetland shots weak: few views of open water.</p></header>')
    o.append('<div class="row"><a class="btn" href="../">Back to the A3 page</a></div>')
    o.append('<h2>Contact sheet</h2><a class="contact" href="%s.webp" title="Open full size"><img src="%s_view.webp" alt="Contact sheet of all splat shots" width="%d" height="%d"></a>'
             % (CONTACT, CONTACT, cs["w"], cs["h"]))
    for title, note, items in groups:
        o.append('<h2>%s</h2>' % e(title))
        if note:
            o.append('<p class="note">%s</p>' % e(note))
        o.append('<div class="grid shots">')
        for it in items:
            o.append('<figure class="card"><button type="button" data-full="%s.webp" data-name="%s"><img src="%s_thumb.webp" alt="%s" loading="lazy" width="%d" height="%d"></button>'
                     '<figcaption>%s</figcaption></figure>' % (it["name"], it["name"], it["name"], it["name"], it["w"], it["h"], it["name"]))
        o.append('</div>')
    o.append('<footer>Built %s · splat v01 · <a href="https://github.com/%s/%s">repo</a><br>'
             'Splat: COLMAP 4.2.1, Brush 0.3.0, gsplat rasterizer. Keyframes: iPhone, Polycam export.</footer></div>' % (built, OWNER, REPO))
    o.append('<div id="lb" role="dialog" aria-label="Image viewer"><div class="bar"><span></span>'
             '<button type="button" class="pv" aria-label="Previous">Prev</button><button type="button" class="nx" aria-label="Next">Next</button>'
             '<a class="full" href="#">full size</a><button type="button" class="x" aria-label="Close">Close</button></div>'
             '<div class="fig"><img alt=""></div></div><script src="../a3.js"></script></body></html>')
    return "\n".join(o)


def share_page(sh, files, st, pv, built):
    t = b1.page(sh, files, st, pv, built)
    tag = RELEASES[0][0]
    # packet buttons on the v03 Release; gallery button after the zip
    t = t.replace('href="files/%s">Packet PDF' % files["pdf"], 'href="%s">Packet PDF' % b1.rel_url(tag, files["pdf"]))
    t = t.replace('href="files/%s">Review PDF' % files["review"], 'href="%s">Review PDF' % b1.rel_url(tag, files["review"]))
    t = t.replace('<a class="btn" href="files/%s">README' % files["readme"],
                  '<a class="btn" href="gsplat/">Splat gallery</a><a class="btn" href="files/%s">README' % files["readme"])
    assert 'href="gsplat/"' in t and tag in t
    return t


def release(files):
    tag, title = RELEASES[0]
    if b1.gh("release", "view", tag, "-R", "%s/%s" % (OWNER, REPO)).returncode == 0:
        print("release exists, skipped:", tag)
        return
    notes = ("Contents: 9 sheets (new: 08 S2 Splat atlas), packet PDF and review PDF, one .ai per sheet plus a 9-artboard .ai, "
             "InDesign .indd + .idml with Links and fonts, README.\n"
             "Proxy status: values measured from the Polycam scan; field values still pending are marked P (proxy), open slots listed in the review PDF.\n"
             "How to contribute: see README_group (in the zip and on the page). Field values go in the CSV, layout edits on layer group-edit.\n"
             "Share page: %sa3-groundtruth/ · Splat gallery: %sa3-groundtruth/gsplat/\n"
             "Pin-up Fri Oct 30 2026, 12 pm, 11x17." % (BASE, BASE))
    r = b1.gh("release", "create", tag, files["zip_src"], files["pdf_src"], files["review_src"], "-R", "%s/%s" % (OWNER, REPO),
              "--title", title, "--notes", notes, "--latest")
    print(r.stdout, r.stderr)


def check_live(files):
    tag = RELEASES[0][0]
    extra = [BASE + "a3-groundtruth/gsplat/", b1.rel_url(tag, files["pdf"]), b1.rel_url(tag, files["review"])]
    for t, _ in RELEASES[1:]:
        extra.append("https://github.com/%s/%s/releases/tag/%s" % (OWNER, REPO, t))
    ok, n = b1.check_live(files)
    ok2, n2 = 0, 0
    for u in extra:
        n2 += 1
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ett3-check"}), timeout=120) as r:
                code, body = r.status, r.read(400000) if u.endswith("/") else b""
        except Exception as ex:
            code, body = getattr(ex, "code", str(ex)), b""
        good = code == 200 and (not u.endswith("/") or b1.ROBOTS_META.encode() in body)
        ok2 += good
        if not good:
            print("FAIL", code, u)
    print("crawl total %d/%d" % (ok + ok2, n + n2))


def shots():
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    stamp = datetime.date.today().strftime("%Y%m%d")
    for path, name in (("a3-groundtruth/", "share-page"), ("a3-groundtruth/gsplat/", "gsplat-gallery")):
        for w, h, tag in ((1440, 4200, "desktop-1440"), (390, 12000, "phone-390")):
            out = os.path.join(LANE, "00_share", "site", "ett3-A3_%s_%s_%s_v01.png" % (name, tag, stamp))
            k = 1
            while os.path.exists(out):  # never overwrite
                k += 1
                out = re.sub(r"_v\d+\.png$", "_v%02d.png" % k, out)
            frame = os.path.join(os.environ.get("TEMP", "."), "ett3_shot_%s_%d.html" % (name, w))
            open(frame, "w").write('<!doctype html><body style="margin:0"><iframe src="%s%s" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>' % (BASE, path, w, h))
            subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=%d,%d" % (max(w, 800), h), "--virtual-time-budget=20000",
                            "--screenshot=" + out, "file:///" + frame.replace("\\", "/")], capture_output=True, timeout=180)
            if os.path.exists(out):
                Image.open(out).crop((0, 0, w, h)).save(out)
            print("shot", out, os.path.exists(out))


def main():
    pdf, review = b1.newest("ett3-A3_packet_v*.pdf"), b1.newest("ett3-A3_packet_review_v*.pdf")
    readme, zp = b1.newest("README_group_v*.pdf"), b1.newest("ett3-A3_packet_v*.zip")
    pv = "v%02d" % b1.vnum(pdf)
    assert pv == "v03" and b1.vnum(zp) == 3, (pdf, zp)
    files = dict(zip=os.path.basename(zp), zip_src=zp, zip_mb=os.path.getsize(zp) / 1e6, pdf=os.path.basename(pdf), pdf_src=pdf,
                 pdf_mb=os.path.getsize(pdf) / 1e6, review=os.path.basename(review), review_src=review, review_mb=os.path.getsize(review) / 1e6)
    if "--check-live" in sys.argv or "--shots" in sys.argv:
        if "--check-live" in sys.argv:
            check_live(files)
        if "--shots" in sys.argv:
            shots()
        return
    # PDFs ride on the Release (buttons point there); only the README goes into files/
    for src in (readme,):
        b1.clean_pdf(src, os.path.join(PAGE, "files", os.path.basename(src)))
    files["readme"] = os.path.basename(readme)
    shutil.copy(b1.newest("README_group_v*.md"), os.path.join(PAGE, "files"))
    files["mast"] = b1.masthead()
    sh = b1.sheets(pdf)
    st = b1.status()
    groups, cs = gallery_assets()
    built = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    css = b1.CSS % {k: v["hex"] for k, v in b1.PAL.items()} + EXTRA_CSS
    for p, t in ((os.path.join(SITE, "assets", "site.css"), css), (os.path.join(PAGE, "a3.js"), b1.JS),
                 (os.path.join(PAGE, "index.html"), share_page(sh, files, st, pv, built)),
                 (os.path.join(GS, "index.html"), gallery_page(groups, cs, built)),
                 (os.path.join(SITE, "index.html"), b1.landing(built))):
        open(p, "w", encoding="utf-8", newline="\n").write(t)
    for s in sh:
        print("%-55s %dx%d %.1f MB" % (s["name"], s["w"], s["h"], s["mb"]))
    print({k: v for k, v in files.items() if not k.endswith("_src")})
    print("gallery", [(g[0], len(g[2])) for g in groups])
    b1.gate()
    if "--release" in sys.argv:
        release(files)


if __name__ == "__main__":
    main()
