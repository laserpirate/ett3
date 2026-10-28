# ett3 site · A3 Ground Truth share page · v01
# python _build/build_a3_v01.py [--release] [--check-live] [--shots]
#   copies the newest packet from the lane (00_share/packet) into a3-groundtruth/: sheet PNGs (Pillow, metadata
#   stripped), WebP thumbnails, PDFs (pymupdf, metadata cleared); converts Public Sans to woff2; writes the course
#   landing, the share page, site.css, a3.js, robots.txt. --release uploads the zip to a GitHub Release (skipped if
#   the tag exists). --check-live crawls the live site. --shots saves headless screenshots into the lane.
#   No password, no lock, no encryption: noindex meta and robots disallow only. The gate below fails the build.
import datetime, glob, html, io, json, os, re, shutil, subprocess, sys, urllib.request
import pymupdf
from PIL import Image
from fontTools.ttLib import TTFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANE = r"Z:\_F26_Fall-2026\2_ett3-26\Assignments-ett3\assignment-3_ground-truth"
PACKET = os.path.join(LANE, "00_share", "packet")
MASTHEAD = os.path.join(LANE, "00_share", "site", "ett3-A3_masthead_gsplat-preview_v01.png")  # swap here for the hi-res splat render
MASTHEAD_CROP = (48, 125)  # px off the right (Polycam UI buttons) and the bottom (Windows activation watermark)
MASTHEAD_W = 2400
OWNER, REPO = "laserpirate", "ett3"
BASE = "https://%s.github.io/%s/" % (OWNER, REPO)
# newest first; the page button points to [0], older ones are listed underneath
RELEASES = [("a3-groundtruth-packet-v01", "A3 Ground Truth packet v01")]
PAGE = os.path.join(SITE, "a3-groundtruth")
SHEETS = ["00_cover", "01_D1-patch-delineation", "02_D2-patch-map", "03_D3-plot-transect-plants",
          "04_D3b-plant-drawings", "05_D3c-field-drawings", "06_S1-scan-atlas", "07_data"]
FULL_W, FULL_W_SMALL, FULL_MAX_MB, THUMB_W = 5100, 3400, 8.0, 1200
PAL = json.load(open(os.path.join(LANE, "01_src", "ett3-A3_palette_v01.json")))
ROBOTS_META = '<meta name="robots" content="noindex, nofollow, noai, noimageai">'


def vnum(p):
    return int(re.search(r"_v(\d+)\.\w+$", p).group(1))


def newest(pat):
    c = glob.glob(os.path.join(PACKET, pat))
    return max(c, key=vnum) if c else None


def clean_pdf(src, dst):
    d = pymupdf.open(src)
    d.set_metadata({})
    d.del_xml_metadata()
    d.save(dst, garbage=3, deflate=True)
    d.close()


def sheets(pdf):
    os.makedirs(os.path.join(PAGE, "sheets"), exist_ok=True)
    pv = "v%02d" % vnum(pdf)
    out, d = [], pymupdf.open(pdf)
    for i, key in enumerate(SHEETS):
        name = "ett3-A3_packet-%s_%s" % (pv, key)
        pg = d[i]
        for w in (FULL_W, FULL_W_SMALL):
            pix = pg.get_pixmap(matrix=pymupdf.Matrix(w / pg.rect.width, w / pg.rect.width), alpha=False)
            im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")  # fresh image: no metadata carried
            full = os.path.join(PAGE, "sheets", name + ".png")
            im.save(full, optimize=True)
            if os.path.getsize(full) / 1e6 <= FULL_MAX_MB:
                break
        th = im.resize((THUMB_W, round(im.height * THUMB_W / im.width)), Image.LANCZOS)
        th.save(os.path.join(PAGE, "sheets", name + ".webp"), quality=84, method=6)
        out.append(dict(name=name, w=im.width, h=im.height, mb=os.path.getsize(full) / 1e6))
    return out


def masthead():
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    im = Image.open(MASTHEAD).convert("RGB")
    im = im.crop((0, 0, im.width - MASTHEAD_CROP[0], im.height - MASTHEAD_CROP[1]))
    im = Image.frombytes("RGB", im.size, im.tobytes()).resize((MASTHEAD_W, round(im.height * MASTHEAD_W / im.width)), Image.LANCZOS)  # no metadata
    im.save(os.path.join(PAGE, "masthead.webp"), quality=86, method=6)
    im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS).save(os.path.join(SITE, "assets", "a3-card.webp"), quality=84, method=6)
    return im.size


def fonts():
    d = os.path.join(SITE, "assets", "fonts")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(PACKET, "indd", "Document fonts", "PublicSans-*.otf")):
        t = TTFont(f)
        t.flavor = "woff2"
        t.save(os.path.join(d, os.path.basename(f)[:-4] + ".woff2"))


def status():
    t = open(newest("README_group_v*.md"), encoding="utf-8").read()
    m = re.search(r"\|\s*total\s*\|\s*(\d+) slots\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", t)
    n, field, data, confirm, p = m.groups()
    return dict(n=n, field=field, data=data, confirm=confirm, p=p)


def rel_url(tag, f):
    return "https://github.com/%s/%s/releases/download/%s/%s" % (OWNER, REPO, tag, os.path.basename(f))


CSS = """@font-face{font-family:'Public Sans';font-weight:400;font-style:normal;font-display:swap;src:url(fonts/PublicSans-Regular.woff2) format('woff2')}
@font-face{font-family:'Public Sans';font-weight:600;font-style:normal;font-display:swap;src:url(fonts/PublicSans-SemiBold.woff2) format('woff2')}
@font-face{font-family:'Public Sans';font-weight:400;font-style:italic;font-display:swap;src:url(fonts/PublicSans-Italic.woff2) format('woff2')}
:root{--ink:%(ink)s;--water:%(water)s;--accent:%(accent)s;--contour:%(contour)s;--proxy:%(proxy)s;--paper:%(paper)s;--ground:%(t_upland)s;--rule:#d9d4cf}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 'Public Sans',sans-serif}
a{color:var(--water)}
.wrap{max-width:1280px;margin:0 auto;padding:0 24px}
h1{font-size:30px;font-weight:600;margin:24px 0 4px;line-height:1.2}
h2{font-size:20px;font-weight:600;margin:32px 0 12px;border-bottom:1px solid var(--rule);padding-bottom:6px}
.sub{margin:0;color:var(--contour)}
.status{margin:12px 0 0;font-size:15px}.status .p{color:var(--proxy);font-style:italic}
.mast{display:block;width:100%%;height:clamp(200px,34vw,520px);object-fit:cover;object-position:45%% 55%%;background:var(--ink)}
.row{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0 4px}
.btn{display:inline-block;padding:9px 16px;border:1px solid var(--ink);border-radius:0;color:var(--ink);text-decoration:none;font-weight:600;font-size:15px}
.btn:hover,.btn:focus{background:var(--ink);color:var(--paper)}
.btn.main{background:var(--ink);color:var(--paper)}.btn.main:hover{background:var(--water);border-color:var(--water)}
.older{font-size:13px;color:var(--proxy);margin:6px 0 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%%),1fr));gap:18px}
.card{margin:0;border:1px solid var(--rule);background:var(--ground)}
.card button{display:block;width:100%%;padding:0;border:0;background:var(--paper);cursor:zoom-in}
.card img{display:block;width:100%%;height:auto;aspect-ratio:17/11}
.card figcaption{padding:8px 10px;font-size:13px;word-break:break-all}
footer{margin:48px 0 32px;padding-top:12px;border-top:1px solid var(--rule);font-size:13px;color:var(--contour)}
#lb{position:fixed;inset:0;background:rgba(5,7,12,.94);display:none;flex-direction:column;z-index:20}
#lb.on{display:flex}#lb .bar{display:flex;gap:10px;align-items:center;padding:10px 16px;color:var(--paper);font-size:14px}
#lb .bar span{flex:1;word-break:break-all}#lb .bar a,#lb .bar button{color:var(--paper);border:1px solid var(--paper);background:none;border-radius:0;padding:6px 12px;font:600 14px 'Public Sans',sans-serif;text-decoration:none;cursor:pointer}
#lb .fig{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;padding:0 16px 16px}
#lb img{max-width:100%%;max-height:100%%;background:var(--paper)}
.list{list-style:none;padding:0;margin:0}.list li{display:flex;gap:16px;align-items:center;border:1px solid var(--rule);padding:10px;margin-bottom:12px}
.list img{width:240px;max-width:40vw;height:auto;display:block}
@media (max-width:600px){.wrap{padding:0 16px}h1{font-size:24px}.grid{grid-template-columns:1fr}.btn{flex:1 1 100%%;text-align:center}}
"""

JS = """(function(){var c=[].slice.call(document.querySelectorAll('.card button')),lb=document.getElementById('lb'),im=lb.querySelector('img'),
nm=lb.querySelector('.bar span'),fu=lb.querySelector('.full'),i=0;
function show(k){i=(k+c.length)%c.length;var b=c[i];im.src=b.dataset.full;im.alt=b.dataset.name;nm.textContent=b.dataset.name+'  ('+(i+1)+' of '+c.length+')';fu.href=b.dataset.full;lb.classList.add('on');}
function hide(){lb.classList.remove('on');im.removeAttribute('src');c[i].focus();}
c.forEach(function(b,k){b.addEventListener('click',function(){show(k);});});
lb.querySelector('.x').addEventListener('click',hide);lb.querySelector('.pv').addEventListener('click',function(){show(i-1);});
lb.querySelector('.nx').addEventListener('click',function(){show(i+1);});
lb.addEventListener('click',function(e){if(e.target===lb||e.target.classList.contains('fig'))hide();});
document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;if(e.key==='Escape')hide();
else if(e.key==='ArrowRight')show(i+1);else if(e.key==='ArrowLeft')show(i-1);});})();
"""


def head(title, desc, css, og_img):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            + ROBOTS_META + '<title>%s</title><meta name="description" content="%s"><meta property="og:title" content="%s">'
            '<meta property="og:description" content="%s"><meta property="og:image" content="%s"><meta property="og:type" content="website">'
            '<link rel="icon" href="data:,"><link rel="stylesheet" href="%s"></head><body>') % (title, desc, title, desc, og_img, css)


def page(sh, files, st, pv, built):
    tag, _ = RELEASES[0]
    alt = "Gaussian splat preview of the transect, Alewife Brook"
    e = html.escape
    o = [head("ett3 A3 Ground Truth", "Group packet for Assignment 3, Ground Truth, Alewife Brook Conservation Area. Pin-up Fri Oct 30, 12 pm.",
              "../assets/site.css", BASE + "a3-groundtruth/masthead.webp")]
    o.append('<img class="mast" src="masthead.webp" alt="%s" width="%d" height="%d">' % (alt, *files["mast"]))
    o.append('<div class="wrap"><header><h1>Assignment 3 · Ground Truth</h1><p class="sub">Alewife Brook Conservation Area</p>'
             '<p class="sub">Pin-up Fri Oct 30, 12 pm · group: [FIELD: names]</p>')
    o.append('<p class="status">Packet %s · values measured from the Polycam scan, field values pending are marked <span class="p">P</span> (proxy) · '
             '%s open slots: FIELD %s, DATA %s, CONFIRM %s, P %s</p></header>' % (pv, st["n"], st["field"], st["data"], st["confirm"], st["p"]))
    o.append('<div class="row">'
             '<a class="btn main" href="%s">Packet zip (%.1f MB)</a>' % (rel_url(tag, files["zip"]), files["zip_mb"])
             + '<a class="btn" href="files/%s">Packet PDF (%.1f MB)</a>' % (files["pdf"], files["pdf_mb"])
             + '<a class="btn" href="files/%s">Review PDF (slots marked, %.1f MB)</a>' % (files["review"], files["review_mb"])
             + '<a class="btn" href="files/%s">README for the group</a></div>' % files["readme"])
    if len(RELEASES) > 1:
        o.append('<p class="older">Older packets: ' + ", ".join('<a href="https://github.com/%s/%s/releases/tag/%s">%s</a>' % (OWNER, REPO, t, e(n))
                                                            for t, n in RELEASES[1:]) + "</p>")
    o.append('<h2>Sheets</h2><div class="grid">')
    for s in sh:
        o.append('<figure class="card"><button type="button" data-full="sheets/%s.png" data-name="%s">'
                 '<img src="sheets/%s.webp" alt="%s" loading="lazy" width="1200" height="776"></button>'
                 '<figcaption>%s</figcaption></figure>' % (s["name"], s["name"], s["name"], s["name"], s["name"]))
    o.append('</div><footer>Built %s · packet %s · <a href="https://github.com/%s/%s">repo</a><br>'
             'Scan: Polycam. Drawings: Python, Blender, Illustrator, InDesign, Claude.</footer></div>' % (built, pv, OWNER, REPO))
    o.append('<div id="lb" role="dialog" aria-label="Sheet viewer"><div class="bar"><span></span>'
             '<button type="button" class="pv" aria-label="Previous">Prev</button><button type="button" class="nx" aria-label="Next">Next</button>'
             '<a class="full" href="#">full size</a><button type="button" class="x" aria-label="Close">Close</button></div>'
             '<div class="fig"><img alt=""></div></div><script src="a3.js"></script></body></html>')
    return "\n".join(o)


def landing(built):
    return "\n".join([head("ett3", "ett3 course pages.", "assets/site.css", BASE + "assets/a3-card.webp"),
                      '<div class="wrap"><h1>ett3</h1><p class="sub">Assignment pages</p><h2>Assignments</h2><ul class="list">',
                      '<li><a href="a3-groundtruth/"><img src="assets/a3-card.webp" alt="Gaussian splat preview of the transect, Alewife Brook"></a>'
                      '<div><a href="a3-groundtruth/"><strong>A3 · Ground Truth</strong></a><br>Alewife Brook Conservation Area · pin-up Fri Oct 30</div></li>',
                      '</ul><footer>Built %s · <a href="https://github.com/%s/%s">repo</a></footer></div></body></html>' % (built, OWNER, REPO)])


def gate():
    bad = []
    lock = re.compile(r"type=[\"']?password|\b(passwords?|passphrase|unlock|locked|encrypt\w*|decrypt\w*|staticrypt|crypto)\b", re.I)
    for root, dirs, fs in os.walk(SITE):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in fs:
            p = os.path.join(root, f)
            rp = os.path.relpath(p, SITE)
            if os.path.getsize(p) > 50e6:
                bad.append("over 50 MB: " + rp)
            if f.endswith((".html", ".js", ".css")):
                t = open(p, encoding="utf-8").read()
                if lock.search(t):
                    bad.append("lock word: %s (%s)" % (rp, lock.search(t).group(0)))
                if f.endswith(".html"):
                    if ROBOTS_META not in t:
                        bad.append("no noindex meta: " + rp)
                    if re.search("[\u2013\u2014]", re.sub(r"<[^>]+>", "", t)):
                        bad.append("em or en dash: " + rp)
    if bad:
        sys.exit("GATE FAIL\n" + "\n".join(bad))
    print("gate ok")


def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True)


def release(files):
    tag, title = RELEASES[0]
    if gh("release", "view", tag, "-R", "%s/%s" % (OWNER, REPO)).returncode == 0:
        print("release exists, skipped:", tag)
        return
    notes = ("Contents: 8 sheets (PDF, PNG, SVG), one .ai per sheet plus an 8-artboard .ai, InDesign .indd + .idml with Links and fonts, README.\n"
             "Proxy status: values measured from the Polycam scan; field values still pending are marked P (proxy), open slots listed in the review PDF.\n"
             "How to contribute: see README_group (in the zip and on the page). Field values go in the CSV, layout edits on layer group-edit.\n"
             "Share page: %sa3-groundtruth/\n"
             "Pin-up Fri Oct 30 2026, 12 pm, 11x17." % BASE)
    r = gh("release", "create", tag, files["zip_src"], "-R", "%s/%s" % (OWNER, REPO), "--title", title, "--notes", notes)
    print(r.stdout, r.stderr)


def check_live(files):
    tag, _ = RELEASES[0]
    urls = [BASE, BASE + "a3-groundtruth/", BASE + "robots.txt", rel_url(tag, files["zip"])]
    for root, _, fs in os.walk(SITE):
        if ".git" in root or "_build" in root:
            continue
        for f in fs:
            rp = os.path.relpath(os.path.join(root, f), SITE).replace("\\", "/")
            if rp.startswith(".") or rp in ("README.md", "robots.txt") or rp.endswith("index.html"):
                continue
            urls.append(BASE + rp)
    ok, n = 0, 0
    for u in urls:
        n += 1
        try:
            req = urllib.request.Request(u, method="GET" if u.endswith(("/", ".txt")) or "releases/download" in u else "HEAD", headers={"User-Agent": "ett3-check"})
            with urllib.request.urlopen(req, timeout=60) as r:
                code = r.status
                body = r.read(200000) if u.endswith(("/", ".txt")) else b""
        except Exception as ex:
            code, body = getattr(ex, "code", str(ex)), b""
        good = code == 200
        if u.endswith("robots.txt"):
            good = good and b"Disallow: /" in body
        if u.endswith("/"):
            good = good and ROBOTS_META.encode() in body and not re.search(rb"type=[\"']?password", body, re.I)
        ok += good
        if not good:
            print("FAIL", code, u)
    print("crawl %d/%d" % (ok, n))
    return ok, n


def shots():
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    stamp = datetime.date.today().strftime("%Y%m%d")
    for w, h, tag in ((1440, 3400, "desktop-1440"), (390, 9000, "phone-390")):
        out = os.path.join(LANE, "00_share", "site", "ett3-A3_share-page_%s_%s_v01.png" % (tag, stamp))
        n = 1
        while os.path.exists(out):  # never overwrite
            n += 1
            out = re.sub(r"_v\d+\.png$", "_v%02d.png" % n, out)
        # headless Chrome clamps windows to about 500 px, so the page is framed at exactly w px and the shot cropped to it
        frame = os.path.join(os.environ.get("TEMP", "."), "ett3_shot_%d.html" % w)
        open(frame, "w").write('<!doctype html><body style="margin:0"><iframe src="%sa3-groundtruth/" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>' % (BASE, w, h))
        subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=%d,%d" % (max(w, 800), h), "--virtual-time-budget=15000",
                        "--screenshot=" + out, "file:///" + frame.replace("\\", "/")], capture_output=True, timeout=120)
        if os.path.exists(out):
            Image.open(out).crop((0, 0, w, h)).save(out)
        print("shot", out, os.path.exists(out))


def main():
    pdf, review = newest("ett3-A3_packet_v*.pdf"), newest("ett3-A3_packet_review_v*.pdf")
    readme, zp = newest("README_group_v*.pdf"), newest("ett3-A3_packet_v*.zip")
    pv = "v%02d" % vnum(pdf)
    os.makedirs(os.path.join(PAGE, "files"), exist_ok=True)
    files = dict(zip=os.path.basename(zp), zip_src=zp, zip_mb=os.path.getsize(zp) / 1e6)
    if "--check-live" in sys.argv or "--shots" in sys.argv:
        if "--check-live" in sys.argv:
            check_live(files)
        if "--shots" in sys.argv:
            shots()
        return
    for k, src in (("pdf", pdf), ("review", review), ("readme", readme)):
        dst = os.path.join(PAGE, "files", os.path.basename(src))
        clean_pdf(src, dst)
        files[k], files[k + "_mb"] = os.path.basename(src), os.path.getsize(dst) / 1e6
    shutil.copy(newest("README_group_v*.md"), os.path.join(PAGE, "files"))
    files["mast"] = masthead()
    fonts()
    sh = sheets(pdf)
    st = status()
    built = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    css = CSS % {k: v["hex"] for k, v in PAL.items()}
    for p, t in ((os.path.join(SITE, "assets", "site.css"), css), (os.path.join(PAGE, "a3.js"), JS),
                 (os.path.join(PAGE, "index.html"), page(sh, files, st, pv, built)), (os.path.join(SITE, "index.html"), landing(built)),
                 (os.path.join(SITE, "robots.txt"), "User-agent: *\nDisallow: /\n"), (os.path.join(SITE, ".nojekyll"), "")):
        open(p, "w", encoding="utf-8", newline="\n").write(t)
    for s in sh:
        print("%-55s %dx%d %.1f MB" % (s["name"], s["w"], s["h"], s["mb"]))
    print({k: v for k, v in files.items() if k != "zip_src"})
    gate()
    if "--release" in sys.argv:
        release(files)


if __name__ == "__main__":
    main()
