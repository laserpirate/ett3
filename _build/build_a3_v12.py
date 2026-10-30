# ett3 site · A3 · build v12 · final PIN set v04 (v21 mods: names group-only, type sizes, PIN-01 blueprint, PIN-03 catalog, PIN-05 drawn section, PIN-07 ANM)
# python _build/build_a3_v12.py final "<stamp>" [<release url>]   Final grid v04 + buttons; names rule over the site; Splat Gallery framed stills
# python _build/build_a3_v12.py atmos                              Splat Gallery "Atmos" section from 00_share/gsplat/atmos (after the bonus render)
#   Re-runnable: edits between <!--final:start-->/<!--final:end-->, <!--framed:start-->/<!--framed:end-->, <!--atmos:start-->/<!--atmos:end-->.
#   Repo copies: Submission PDF (37 MB) and REF PDF (18 MB) under files/; the lite zip (85 MB) and package (694 MB) on Release a3-final-v04.
#   Web images: WebP thumbs + 3000 px WebP full size, no 4K masters in the repo.
import glob, html, importlib.util, os, re, shutil, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE); PAGE = os.path.join(SITE, "a3-groundtruth")
A3 = r"Z:\_F26_Fall-2026\2_ett3-26\Assignments-ett3\assignment-3_ground-truth"
FIN = os.path.join(A3, "00_share", "final_v04"); SPL = os.path.join(A3, "01_src", "final_work_v04", "splat"); ATM = os.path.join(A3, "00_share", "gsplat", "atmos")
REL = "https://github.com/laserpirate/ett3/releases/download/a3-final-v04/"
GROUP = "Group: Fernanda Castillo, Arturo Gomez Escobedo, Marko Kihara Manriquez"
TITLES = {"00": "Title page", "PIN-01": "Part A · Patch Delineation", "PIN-02": "Part B · Ground-Truthed Patch Map", "PIN-03": "Part C · Plot + Transect",
          "PIN-04": "Part C · Plants", "PIN-05": "Part C · Field Notes + Observations", "PIN-06": "Site Photos", "PIN-07": "Nest · Habitat Feature", "PIN-08": "Scan + Splat Renders"}
FRAMED = [("PIN-02_persp-A_v04", "CAM_persp_A, framed (PIN-02 inset)"), ("PIN-08_hero_high-orbit-B_v04", "High orbit B, framed (PIN-08 hero)"),
          ("PIN-08_orbit-180_v04", "ORBIT_180, framed"), ("PIN-08_side_v04", "CAM_side, ortho, framed"),
          ("PIN-08_close_pole-side_v04b", "Close: the pole's long side, 3.1 m out"), ("PIN-08_close_moss_v04b", "Close: moss on the pole, 2.5 m out"),
          ("PIN-08_close_down-pole_v04b", "Close: down the length of the pole, 2.5 m out")]
e = html.escape


def webp(src, dst_full, dst_thumb, full_w=3000, thumb_w=1000):
    im = Image.open(src).convert("RGB")
    f = im if im.width <= full_w else im.resize((full_w, round(full_w * im.height / im.width)), Image.LANCZOS)
    f.save(dst_full, quality=90, method=6)
    t = im.resize((thumb_w, round(thumb_w * im.height / im.width)), Image.LANCZOS); t.save(dst_thumb, quality=82, method=6)
    return t.size


def card(sid, png):
    os.makedirs(os.path.join(PAGE, "final"), exist_ok=True)
    full, web = "final/ett3-A3_%s_final_v04.png" % sid, "final/ett3-A3_%s_final_v04.webp" % sid
    im = Image.open(png).convert("RGB"); im.save(os.path.join(PAGE, full), optimize=True)
    im.resize((1200, round(1200 * im.height / im.width)), Image.LANCZOS).save(os.path.join(PAGE, web), quality=82)
    return ('<figure class="card"><button type="button" data-full="%s" data-name="%s %s"><img src="%s" alt="%s %s" loading="lazy" width="1200" height="776">'
            '</button><figcaption><b>%s</b> %s</figcaption></figure>' % (full, sid, e(TITLES[sid]), web, sid, e(TITLES[sid]), sid, e(TITLES[sid])))


def shot(rel_full, rel_thumb, size, name, cap):
    return ('<figure class="card"><button type="button" data-full="%s" data-name="%s"><img src="%s" alt="%s" loading="lazy" width="%d" height="%d"></button>'
            '<figcaption>%s</figcaption></figure>' % (rel_full, e(name), rel_thumb, e(cap), size[0], size[1], e(cap)))


def put(t, tag, sec, before):
    a, b = "<!--%s:start-->" % tag, "<!--%s:end-->" % tag
    if a in t:
        return re.sub(re.escape(a) + ".*?" + re.escape(b), lambda m: a + sec + b, t, flags=re.S)
    assert before in t, before
    return t.replace(before, a + sec + b + "\n" + before, 1)


def names_rule():
    """v21 A: no individual attribution anywhere on the site; only the group line"""
    sp = os.path.join(PAGE, "species", "index.html"); t = open(sp, encoding="utf-8").read()
    open(sp, "w", encoding="utf-8", newline="\n").write(t.replace("field (Marko), confirm species", "field (group), confirm species"))
    for md in glob.glob(os.path.join(PAGE, "files", "README_group_v0*.md")):
        t = open(md, encoding="utf-8").read()
        t = t.replace("Send it to Marko; he re-runs the build", "Send it back to the group; the build is re-run").replace("(send to Marko)", "(send to the group)")
        open(md, "w", encoding="utf-8", newline="\n").write(t)
    import pymupdf
    for pdf in glob.glob(os.path.join(PAGE, "files", "README_group_v0*.pdf")):
        d = pymupdf.open(pdf); n = 0
        for pg in d:
            for r in pg.search_for("Marko"):
                pg.add_redact_annot(r, text="the group", fontsize=0, fill=(1, 1, 1)); n += 1
            pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
        if n:
            tmp = pdf + ".tmp"; d.save(tmp, garbage=4, deflate=True); d.close(); os.replace(tmp, pdf)
    # superseded finals carry individual credits (v02 header, v03 credit lines): out of the repo
    for f in glob.glob(os.path.join(PAGE, "final", "*_final_v0[23].*")) + glob.glob(os.path.join(PAGE, "final", "*_v0[23].*")) + \
            [os.path.join(PAGE, "files", "ett3-A3_PIN-set_final_v03.pdf")]:
        if os.path.exists(f):
            os.remove(f)
    for pg in ("animations", "gsplat"):   # pole wording (v19): the log is a fallen utility pole on oaks
        p = os.path.join(PAGE, pg, "index.html"); t = open(p, encoding="utf-8").read()
        t = t.replace("around the fallen log", "around the fallen utility pole").replace("· fallen log ·", "· fallen utility pole ·")
        open(p, "w", encoding="utf-8", newline="\n").write(t)


def final(stamp):
    p = os.path.join(PAGE, "index.html"); t = open(p, encoding="utf-8").read()
    pngs = {sid: f for sid in TITLES for f in glob.glob(os.path.join(FIN, "png", "ett3-A3_%s_*_final_v04.png" % sid))}
    href = sys.argv[3] if len(sys.argv) > 3 else REL
    for f in ("ett3-A3_PIN-set_final_v04.pdf", "ett3-A3_REF-set_final_v04.pdf"):
        shutil.copy2(os.path.join(FIN, f), os.path.join(PAGE, "files", f))
    mb = lambda f: os.path.getsize(os.path.join(FIN, f)) / 1e6
    head = ('<h2>Final · PIN set (title + 8)</h2><p class="older">Pin-up Fri Oct 30 2026, 12 pm, 11x17 landscape, print at actual size. %s. Built %s.</p>' % (GROUP, stamp))
    btn = ('<div class="row"><a class="btn main" href="files/ett3-A3_PIN-set_final_v04.pdf">Submission PDF (final, %.0f MB)</a>'
           '<a class="btn" href="files/ett3-A3_REF-set_final_v04.pdf">REF PDF (internal, %.0f MB)</a>'
           '<a class="btn" href="%sett3-A3_PIN-lite_final_v04.zip">PIN-lite zip (PDFs, PNGs, IDML, %.0f MB)</a>'
           '<a class="btn main" href="%sett3-A3_final_package_v04.zip">Editable package (.ai, .indd, links, %.0f MB)</a></div>'
           % (mb("ett3-A3_PIN-set_final_v04.pdf"), mb("ett3-A3_REF-set_final_v04.pdf"), href, mb("ett3-A3_PIN-lite_final_v04.zip"), href, mb("ett3-A3_final_package_v04.zip")))
    sec = head + btn + '<div class="grid">\n' + "\n".join(card(k, pngs[k]) for k in TITLES) + "\n</div>"
    t = put(t, "final", sec, "<h2>PIN · submission set")
    open(p, "w", encoding="utf-8", newline="\n").write(t)
    # Splat Gallery: framed stills from this run (v20 rule; close row per the exemption)
    g = os.path.join(PAGE, "gsplat", "index.html"); t = open(g, encoding="utf-8").read(); out = os.path.join(PAGE, "gsplat", "framed"); os.makedirs(out, exist_ok=True)
    cards = []
    for n, cap in FRAMED:
        sz = webp(os.path.join(SPL, "ett3-A3_%s.png" % n), os.path.join(out, "ett3-A3_gsplat_%s.webp" % n), os.path.join(out, "ett3-A3_gsplat_%s_thumb.webp" % n))
        cards.append(shot("framed/ett3-A3_gsplat_%s.webp" % n, "framed/ett3-A3_gsplat_%s_thumb.webp" % n, sz, n, cap))
    sec = ('<h2>Framed stills (final PIN set)</h2><p class="older">Wide views: subject centred, 15 to 25 %% negative space, fitted by scaling, not cropping. '
           'Close row: framed on the pole and moss segment, about 15 %% margin, cameras 2.5 to 3.1 m out. Full size 3000 px.</p><div class="grid shots">\n' + "\n".join(cards) + "\n</div>")
    t = put(t, "framed", sec, "<h2>Contact sheet</h2>")
    open(g, "w", encoding="utf-8", newline="\n").write(t)
    names_rule()


def atmos():
    g = os.path.join(PAGE, "gsplat", "index.html"); t = open(g, encoding="utf-8").read(); out = os.path.join(PAGE, "gsplat", "atmos"); os.makedirs(out, exist_ok=True)
    cards = []; cs = ""
    for f in sorted(glob.glob(os.path.join(ATM, "ett3-A3_atmos_*_v01.png"))):
        n = os.path.splitext(os.path.basename(f))[0]
        sz = webp(f, os.path.join(out, n + ".webp"), os.path.join(out, n + "_thumb.webp"))
        cap = n.replace("ett3-A3_atmos_", "").replace("_v01", "").replace("_", " · ")
        cards.append(shot("atmos/%s.webp" % n, "atmos/%s_thumb.webp" % n, sz, n, cap))
    c = glob.glob(os.path.join(ATM, "ett3-A3_atmos_contact-sheet_v01.png"))
    if c:
        sz = webp(c[0], os.path.join(out, "ett3-A3_atmos_contact-sheet_v01.webp"), os.path.join(out, "ett3-A3_atmos_contact-sheet_v01_view.webp"), 3000, 2000)
        cs = '<a class="contact" href="atmos/ett3-A3_atmos_contact-sheet_v01.webp" title="Open full size"><img src="atmos/ett3-A3_atmos_contact-sheet_v01_view.webp" alt="Atmos contact sheet" width="%d" height="%d"></a>' % sz
    clip = ""
    for v in sorted(glob.glob(os.path.join(ATM, "ett3-A3_atmos_*test-clip*_1920*.mp4"))):
        shutil.copy2(v, os.path.join(out, os.path.basename(v)))
        clip += '<video controls muted loop playsinline preload="metadata" width="1920" height="1080" style="width:100%%;height:auto"><source src="atmos/%s" type="video/mp4"></video>' % os.path.basename(v)
    sec = ('<h2>Atmos</h2><p class="older">The aligned splat uncropped, foreground and background blobs kept, depth blur outside a focus band on each shot\'s subject. '
           'Paper and ink versions, every v07 camera. Full size 3000 px (masters 4000 px, not in the repo).</p>' + cs + clip + '<div class="grid shots">\n' + "\n".join(cards) + "\n</div>")
    t = put(t, "atmos", sec, "<h2>Contact sheet</h2>")
    open(g, "w", encoding="utf-8", newline="\n").write(t)


def gate():
    _s = importlib.util.spec_from_file_location("b1", os.path.join(HERE, "build_a3_v01.py")); b1 = importlib.util.module_from_spec(_s); _s.loader.exec_module(b1)
    b1.gate()
    bad = []
    for p in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True) + glob.glob(os.path.join(PAGE, "files", "*.md")):
        s = open(p, encoding="utf-8").read().replace(GROUP, "")
        h = re.findall(r"Marko|Fernanda|Arturo|Kihara|Manriquez|Castillo|Gomez|Escobedo", s)
        if h:
            bad.append("%s: %d" % (os.path.relpath(p, SITE), len(h)))
    if bad:
        sys.exit("NAMES GATE FAIL\n" + "\n".join(bad))
    print("names gate ok")


if __name__ == "__main__":
    {"final": lambda: final(sys.argv[2] if len(sys.argv) > 2 else ""), "atmos": atmos, "gate": lambda: None}[sys.argv[1]]()
    gate()
