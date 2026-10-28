# ett3 site · A3 Ground Truth · v04 · packet v05 (14 sheets), Site Plans (D2 A / B / C), Plant Species, nest callout
# python _build/build_a3_v04.py --manifest <path.json> [--release] [--check-live] [--shots]
#   v03 (and through it v02, v01) is kept and imported for its helpers. Default run builds locally and runs the gate only.
#   The manifest names the lane files, so the build does not guess versions:
#   {"pv": "v05",
#    "packet_pdf": path, "review_pdf": path, "zip": path, "readme_pdf": path, "readme_md": path,   (readme optional: newest in the lane)
#    "pages": [{"no": "00", "title": "Cover", "png": path}, ...],                                  (14 sheets, packet order)
#    "d2": {"A": png, "B": png, "C": png},
#    "nest_marker": {"A": [x, y], "B": [x, y], "C": [x, y]},   optional: nest symbol position as a fraction of the image (0..1, from top left)
#    "species_csv": path, "pole_html": "<p>...</p>" (optional),
#    "status": {"n": .., "field": .., "data": .., "confirm": .., "p": ..} (optional: read from the README md slot table otherwise)}
#   New pages: plans/ (D2 option A / B / C side by side, nest callout), species/ (sortable table from the species CSV).
#   Nest page: portrait slot left, landscape slots right. Photos page: each figure gets an anchor (#photo-NN) for the species links.
import csv, datetime, html, importlib.util, io, json, os, re, shutil, subprocess, sys
from PIL import Image

_spec = importlib.util.spec_from_file_location("b3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v03.py"))
b3 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(b3)
b2, b1 = b3.b2, b3.b1
SITE, LANE, PAGE, BASE, OWNER, REPO = b1.SITE, b1.LANE, b1.PAGE, b1.BASE, b1.OWNER, b1.REPO
RELEASES = [("a3-groundtruth-packet-v05", "A3 Ground Truth packet v05 (14 sheets)"), ("a3-groundtruth-packet-v04", "A3 Ground Truth packet v04"),
            ("a3-groundtruth-packet-v03", "A3 Ground Truth packet v03 (9 sheets)"), ("a3-groundtruth-packet-v01", "A3 Ground Truth packet v01 (8 sheets)")]
b1.RELEASES = b2.RELEASES = b3.RELEASES = RELEASES
NAV = [("", "Packet"), ("plans/", "Site Plans"), ("views/", "Site Views"), ("photos/", "Site Photos"), ("species/", "Plant Species"),
       ("gsplat/", "Splat Gallery"), ("nest/", "Nest Habitat Adaptation")]
b3.NAV = NAV
D2_CAP = {"A": ("Option A · texture", "Contours over the Polycam texture top view."),
          "B": ("Option B · contours only", "Contours on white, the fallen logs outlined from the scan with their lengths."),
          "C": ("Option C · mesh", "Contours over the mesh wireframe top view, lightened.")}
NEST_TXT = "Bird nest (abandoned), in shrub, ~6 ft / 1.8 m above ground, s 4.5 m [CONFIRM position]"
EXTRA_CSS = b3.EXTRA_CSS + """.pin{position:relative}
.nestpin{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border:2px solid var(--accent);border-radius:50%;background:rgba(255,255,255,.35);z-index:2}
.nestpin:hover,.nestpin:focus{background:var(--accent)}
.callout{margin:18px 0 0;padding:12px 14px;border:1px solid var(--accent);font-size:15px}.callout a{font-weight:600}
.nestgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:18px;margin-top:22px;align-items:start}
.nestgrid .slot{min-height:0}.nestgrid .slot.portrait{aspect-ratio:3/4}
.nestgrid .land{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.nestgrid .land .slot{aspect-ratio:3/2}
.tw{overflow-x:auto;margin-top:18px;border:1px solid var(--rule)}
table.sp{border-collapse:collapse;font-size:14px;min-width:1100px;width:100%}
table.sp th,table.sp td{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
table.sp th{background:var(--ground);font-weight:600;position:sticky;top:0}
table.sp th button{font:inherit;font-weight:600;background:none;border:0;padding:0;cursor:pointer;color:var(--ink);text-align:left}
table.sp th button::after{content:" \\2195";color:var(--proxy)}
table.sp tr.tp td{color:var(--proxy);font-style:italic}
table.sp .tag{display:inline-block;margin-left:4px;padding:0 4px;border:1px solid var(--proxy);font-size:11px;font-style:normal}
.pole{margin-top:28px;font-size:15px}
@media (max-width:600px){.nestgrid,.nestgrid .land{grid-template-columns:1fr}}
"""
SORT_JS = """<script>(function(){var t=document.querySelector('table.sp');if(!t)return;var b=t.tBodies[0];
[].forEach.call(t.tHead.rows[0].cells,function(th,i){var k=th.querySelector('button');if(!k)return;var asc=true;
k.addEventListener('click',function(){var r=[].slice.call(b.rows);r.sort(function(x,y){var a=x.cells[i].textContent.trim(),c=y.cells[i].textContent.trim(),
na=parseFloat(a),nc=parseFloat(c);var v=(!isNaN(na)&&!isNaN(nc))?na-nc:a.localeCompare(c);return asc?v:-v;});asc=!asc;r.forEach(function(e){b.appendChild(e);});});});})();</script>"""


def load_manifest():
    if "--manifest" not in sys.argv:
        sys.exit("need --manifest <path.json>")
    m = json.load(open(sys.argv[sys.argv.index("--manifest") + 1], encoding="utf-8"))
    for k in ("packet_pdf", "review_pdf", "zip", "pages", "d2"):
        assert k in m, "manifest: missing " + k
    assert len(m["pages"]) == 14, "manifest: %d pages, expected 14" % len(m["pages"])
    for p in [m["packet_pdf"], m["review_pdf"], m["zip"]] + [q["png"] for q in m["pages"]] + list(m["d2"].values()):
        assert os.path.exists(p), "missing: " + p
    return m


def slug(t):
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")


def sheet_assets(m):
    """one PNG (8 MB max) + WebP thumb per packet page, fresh pixel buffers"""
    d = os.path.join(PAGE, "sheets"); os.makedirs(d, exist_ok=True)
    out = []
    for q in m["pages"]:
        name = "ett3-A3_packet-%s_%s_%s" % (m["pv"], q["no"], slug(q["title"]))
        src = Image.open(q["png"]).convert("RGB")
        src = Image.frombytes("RGB", src.size, src.tobytes())
        full = os.path.join(d, name + ".png")
        for w in (b1.FULL_W, b1.FULL_W_SMALL, 2550):
            im = src if src.width <= w else src.resize((w, round(src.height * w / src.width)), Image.LANCZOS)
            if not os.path.exists(full) or os.path.getsize(full) / 1e6 > b1.FULL_MAX_MB:
                im.save(full, optimize=True)
            if os.path.getsize(full) / 1e6 <= b1.FULL_MAX_MB:
                break
        th = os.path.join(d, name + ".webp")
        if not os.path.exists(th):
            src.resize((b1.THUMB_W, round(src.height * b1.THUMB_W / src.width)), Image.LANCZOS).save(th, quality=84, method=6)
        out.append(dict(name=name, no=q["no"], title=q["title"], w=im.width, h=im.height, mb=os.path.getsize(full) / 1e6))
    return out


def status(m):
    if m.get("status"):
        return {k: str(v) for k, v in m["status"].items()}
    t = open(m.get("readme_md") or b1.newest("README_group_v*.md"), encoding="utf-8").read()
    g = re.search(r"\|\s*total\s*\|\s*(\d+) slots\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", t)
    if not g:
        return dict(n="see review PDF", field="-", data="-", confirm="-", p="-")
    return dict(zip(("n", "field", "data", "confirm", "p"), g.groups()))


def share_page(sh, files, st, pv, built):
    t = b3.share_page(sh, files, st, pv, built)
    for s in sh:
        t = t.replace("<figcaption>%s</figcaption>" % s["name"], "<figcaption><b>%s</b> %s</figcaption>" % (s["no"], html.escape(s["title"])))
        t = t.replace('data-name="%s"' % s["name"], 'data-name="%s %s"' % (s["no"], html.escape(s["title"])))
    t = t.replace('<a class="btn" href="gsplat/">Splat gallery</a>', '<a class="btn" href="plans/">Site plans (D2 A / B / C)</a><a class="btn" href="gsplat/">Splat gallery</a>')
    t = t.replace("<h2>Sheets</h2>", "<h2>Sheets (%d)</h2>" % len(sh))
    assert "plans/" in t and RELEASES[0][0] in t
    return t


def plans_assets(m):
    d = os.path.join(PAGE, "plans"); os.makedirs(d, exist_ok=True)
    out = {}
    for k in ("A", "B", "C"):
        name = "ett3-A3_D2_site-plan_%s_opt%s" % (m["pv"], k)
        w, h = b3.web(m["d2"][k], os.path.join(d, name + ".webp"), os.path.join(d, name + "_thumb.webp"), 3400, 1200)
        out[k] = dict(name=name, w=w, h=h)
    return out


def plans_page(items, m, built):
    e = html.escape
    o = [b1.head("Site Plans", "D2 site plan of the A3 transect at Alewife Brook in three options: texture, contours only, mesh.",
                 "../../assets/site.css", BASE + "a3-groundtruth/plans/%s_thumb.webp" % items["A"]["name"])]
    o.append('<div class="wrap"><header><h1>Site Plans</h1><p class="sub">D2 · Alewife Brook Conservation Area · transect s 0 to 8.6 m</p>'
             '<p class="status">Three options, same frame, scale and overlays: contours 0.25 ft (index 1 ft), transect, plot, P1 to P3, nest, key, scale, north. '
             'Pick one for the wall.</p></header>')
    o.append(b3.nav("plans/", "../"))
    o.append('<div class="g3" style="margin-top:22px">')
    pins = m.get("nest_marker") or {}
    for k in ("A", "B", "C"):
        it, (ti, ln) = items[k], D2_CAP[k]
        pin = ""
        if k in pins:
            x, y = pins[k]
            pin = '<a class="nestpin" href="../nest/" style="left:%.2f%%;top:%.2f%%" aria-label="%s" title="%s"></a>' % (100 * x, 100 * y, e(NEST_TXT), e(NEST_TXT))
        o.append('<figure class="card"><div class="pin"><button type="button" data-full="%s.webp" data-name="D2 %s"><img src="%s_thumb.webp" alt="D2 %s" loading="lazy" '
                 'width="%d" height="%d"></button>%s</div><figcaption><b>%s</b><br>%s</figcaption></figure>'
                 % (it["name"], e(ti), it["name"], e(ti + ". " + ln), it["w"], it["h"], pin, e(ti), e(ln)))
    o.append('</div>')
    o.append('<p class="callout">Habitat feature: <a href="../nest/">%s</a>. Same symbol on D2 (all options) and D3a. '
             '[FIELD: shrub species] [FIELD: bird species if known]</p>' % e(NEST_TXT))
    o.append('<footer>Built %s · packet %s · <a href="https://github.com/%s/%s">repo</a></footer></div>' % (built, m["pv"], OWNER, REPO))
    o.append(b3.lb("../a3.js"))
    return "\n".join(o)


def nest_page(built):
    slot = '[DROP PHOTOS: _assets-ett3\\nest\\]'
    o = [b1.head("Nest Habitat Adaptation", "A found abandoned nest from Alewife Brook, turned into a readymade sculpture.", "../../assets/site.css",
                 BASE + "a3-groundtruth/masthead.webp")]
    o.append('<div class="wrap"><header><h1>Nest Habitat Adaptation</h1>'
             '<p class="status">A found abandoned nest, Alewife Brook Conservation Area, found [CONFIRM: date], turned into a readymade sculpture.</p>'
             '<p class="sub">Found in a shrub near the fallen log, about 6 ft (1.8 m) above ground, station s 4.5 m [CONFIRM position] · '
             'shrub: [FIELD] · bird: [FIELD: if known] · <a href="../plans/">on the site plans</a></p>'
             '<p class="sub">Group: [FIELD]</p></header>')
    o.append(b3.nav("nest/", "../"))
    o.append('<div class="nestgrid"><div class="slot portrait">Photo slot 1 (portrait) · %s</div><div class="land">' % slot)
    for k in range(2, 6):
        o.append('<div class="slot">Photo slot %d (landscape) · %s</div>' % (k, slot))
    o.append('</div></div><footer>Built %s · no nest photos found yet · <a href="https://github.com/%s/%s">repo</a></footer></div></body></html>' % (built, OWNER, REPO))
    return "\n".join(o)


def photos_page(items, built):
    t = b3.photos_page(items, built)
    k = [0]

    def anchor(_):
        k[0] += 1
        return '<figure class="card" id="photo-%02d">' % k[0]
    return re.sub(r'<figure class="card">', anchor, t)


def photo_href(ref):
    g = re.search(r"(\d+)", ref or "")
    return "../photos/#photo-%02d" % int(g.group(1)) if g else None


def species_page(m, built):
    e = html.escape
    rows = list(csv.DictReader(open(m["species_csv"], encoding="utf-8-sig")))
    cols = [c for c in (rows[0].keys() if rows else []) if c and c.lower() not in ("photo_ref", "photo", "notes_internal")]
    name_col = next((c for c in cols if "common" in c.lower() or "latin" in c.lower() or "species" in c.lower()), cols[0] if cols else None)
    stat_col = next((c for c in cols if "status" in c.lower() and "id" in c.lower()), None)
    o = [b1.head("Plant Species", "Plant species recorded along the A3 transect at Alewife Brook, with wetland indicator and origin.",
                 "../../assets/site.css", BASE + "a3-groundtruth/masthead.webp")]
    o.append('<div class="wrap"><header><h1>Plant Species</h1><p class="sub">Alewife Brook Conservation Area · transect s 0 to 8.6 m · %d species</p>'
             '<p class="status">Grey italic rows are tentative (T, from photos) or proxy (P) until the group confirms the ID. '
             'Click a column head to sort. Same data as sheet D3d.</p></header>' % len(rows))
    o.append(b3.nav("species/", "../"))
    o.append('<div class="tw"><table class="sp"><thead><tr>%s</tr></thead><tbody>' % "".join('<th scope="col"><button type="button">%s</button></th>' % e(c) for c in cols))
    for r in rows:
        st = (r.get(stat_col) or "").lower() if stat_col else ""
        tag = "T" if "tentative" in st else ("P" if "proxy" in st else "")
        cells = []
        for c in cols:
            v = e(r.get(c) or "")
            if c == name_col:
                h = photo_href(r.get("photo_ref") or r.get("photo"))
                if h:
                    v = '<a href="%s">%s</a>' % (h, v)
                if tag:
                    v += '<span class="tag">%s</span>' % tag
            cells.append("<td>%s</td>" % v)
        o.append('<tr%s>%s</tr>' % (' class="tp"' if tag else "", "".join(cells)))
    o.append('</tbody></table></div>')
    if m.get("pole_html"):
        o.append('<section class="pole"><h2>Companion species: the utility pole</h2>%s</section>' % m["pole_html"])
    o.append('<footer>Built %s · data %s · <a href="https://github.com/%s/%s">repo</a></footer></div>%s</body></html>'
             % (built, e(os.path.basename(m["species_csv"])), OWNER, REPO, SORT_JS))
    return "\n".join(o)


def release(files, m):
    tag, title = RELEASES[0]
    if b1.gh("release", "view", tag, "-R", "%s/%s" % (OWNER, REPO)).returncode == 0:
        print("release exists, skipped:", tag); return
    notes = ("Contents: 14 sheets, all 11x17 landscape: cover, D1, D2 options A (texture) / B (contours only, logs outlined) / C (mesh), D3a plot + transect, "
             "D3b plant drawings (P1 fallen oak), D3c field drawings, D3d species, Site Photos, Nest Habitat Adaptation, S1 scan atlas, S2 splat atlas, data. "
             "Packet PDF and review PDF (open slots numbered), .ai per drawing sheet, InDesign .indd + .idml with Links and fonts, README.\n"
             "Proxy status: values measured from the Polycam scan; field values still pending are marked P (proxy), open slots listed in the review PDF.\n"
             "Pages: %sa3-groundtruth/ · plans/ · views/ · photos/ · species/ · gsplat/ · nest/\nPin-up Fri Oct 30 2026, 12 pm, 11x17." % BASE)
    r = b1.gh("release", "create", tag, files["zip_src"], files["pdf_src"], files["review_src"], "-R", "%s/%s" % (OWNER, REPO),
              "--title", title, "--notes", notes, "--latest")
    print(r.stdout, r.stderr)


def check_live(files):
    pages = ["", "a3-groundtruth/", "a3-groundtruth/plans/", "a3-groundtruth/views/", "a3-groundtruth/photos/", "a3-groundtruth/species/",
             "a3-groundtruth/gsplat/", "a3-groundtruth/nest/"]
    seen, ok, n = set(), 0, 0
    for p in pages:
        u = BASE + p
        code, body = b3.fetch(u); n += 1
        t = body.decode("utf-8", "replace")
        good = code == 200 and b1.ROBOTS_META in t
        ok += good
        if not good: print("FAIL page", code, u)
        for r_ in set(re.findall(r'(?:src|href|data-full)="([^"#]+)"', t)):
            au = r_ if r_.startswith("http") else b3.urllib.request.urljoin(u, r_)
            if au in seen or au.startswith("mailto"):
                continue
            seen.add(au)
            code2, _ = b3.fetch(au, 1); n += 1; ok += code2 == 200
            if code2 != 200: print("FAIL", code2, au)
    for f in ("fonts/PublicSans-Regular.woff2", "fonts/PublicSans-SemiBold.woff2", "fonts/PublicSans-Italic.woff2", "site.css"):
        au = BASE + "assets/" + f
        if au not in seen:
            code2, _ = b3.fetch(au, 1); n += 1; ok += code2 == 200
            if code2 != 200: print("FAIL", code2, au)
    for t_, _ in RELEASES:
        au = "https://github.com/%s/%s/releases/tag/%s" % (OWNER, REPO, t_)
        code2, _ = b3.fetch(au, 1); n += 1; ok += code2 == 200
        if code2 != 200: print("FAIL", code2, au)
    print("crawl %d/%d" % (ok, n))


def shots(base=None):
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    base = base or BASE
    stamp = datetime.date.today().strftime("%Y%m%d")
    outdir = os.path.join(LANE, "00_share", "site") if base == BASE else os.environ.get("ETT3_SHOT_DIR", os.environ.get("TEMP", "."))
    for path, name in (("a3-groundtruth/", "share-page"), ("a3-groundtruth/plans/", "site-plans"), ("a3-groundtruth/species/", "species"),
                       ("a3-groundtruth/nest/", "nest")):
        for w, h, tag in ((1440, 4200, "desktop-1440"), (390, 9000, "phone-390")):
            out = os.path.join(outdir, "ett3-A3_%s_%s_%s_v01.png" % (name, tag, stamp))
            k = 1
            while os.path.exists(out):
                k += 1; out = re.sub(r"_v\d+\.png$", "_v%02d.png" % k, out)
            frame = os.path.join(os.environ.get("TEMP", "."), "ett3_shot_%s_%d.html" % (name, w))
            open(frame, "w").write('<!doctype html><body style="margin:0"><iframe src="%s%s" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>' % (base, path, w, h))
            subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--window-size=%d,%d" % (max(w, 800), h), "--virtual-time-budget=25000",
                            "--screenshot=" + out, "file:///" + frame.replace("\\", "/")], capture_output=True, timeout=240)
            if os.path.exists(out):
                Image.open(out).crop((0, 0, w, h)).save(out)
            print("shot", out, os.path.exists(out))


def main():
    m = load_manifest()
    m.setdefault("pv", "v%02d" % b1.vnum(m["packet_pdf"]))
    zp, pdf, review = m["zip"], m["packet_pdf"], m["review_pdf"]
    files = dict(zip=os.path.basename(zp), zip_src=zp, zip_mb=os.path.getsize(zp) / 1e6, pdf=os.path.basename(pdf), pdf_src=pdf,
                 pdf_mb=os.path.getsize(pdf) / 1e6, review=os.path.basename(review), review_src=review, review_mb=os.path.getsize(review) / 1e6)
    if "--check-live" in sys.argv or "--shots" in sys.argv:
        if "--check-live" in sys.argv: check_live(files)
        if "--shots" in sys.argv: shots(os.environ.get("ETT3_SHOT_BASE"))
        return
    readme = m.get("readme_pdf") or b1.newest("README_group_v*.pdf")
    b1.clean_pdf(readme, os.path.join(PAGE, "files", os.path.basename(readme)))
    files["readme"] = os.path.basename(readme)
    shutil.copy(m.get("readme_md") or b1.newest("README_group_v*.md"), os.path.join(PAGE, "files"))
    files["mast"] = b1.masthead()
    sh = sheet_assets(m)
    st = status(m)
    groups, cs = b2.gallery_assets()
    va, pa, pl = b3.views_assets(), b3.photos_assets(), plans_assets(m)
    built = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)")
    css = b1.CSS % {k: v["hex"] for k, v in b1.PAL.items()} + EXTRA_CSS
    pages = [(os.path.join(SITE, "assets", "site.css"), css), (os.path.join(PAGE, "a3.js"), b1.JS),
             (os.path.join(PAGE, "index.html"), share_page(sh, files, st, m["pv"], built)),
             (os.path.join(PAGE, "plans", "index.html"), plans_page(pl, m, built)),
             (os.path.join(PAGE, "gsplat", "index.html"), b3.add_nav(b2.gallery_page(groups, cs, built), "gsplat/", "../")),
             (os.path.join(PAGE, "views", "index.html"), b3.views_page(va, built)),
             (os.path.join(PAGE, "photos", "index.html"), photos_page(pa, built)),
             (os.path.join(PAGE, "nest", "index.html"), nest_page(built)),
             (os.path.join(SITE, "index.html"), b1.landing(built))]
    if m.get("species_csv") and os.path.exists(m["species_csv"]):
        pages.append((os.path.join(PAGE, "species", "index.html"), species_page(m, built)))
    else:
        print("WARN no species CSV, species page not written")
    for p, t in pages:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(t)
    print({k: v for k, v in files.items() if not k.endswith("_src")}, "sheets", len(sh), "views", len(va), "photos", len(pa))
    b1.gate()
    if "--release" in sys.argv:
        release(files, m)


if __name__ == "__main__":
    main()
