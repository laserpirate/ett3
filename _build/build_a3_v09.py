# ett3 site · A3 · build v09 · final PIN set (prompt v18); build_a3_v08 kept
# python _build/build_a3_v09.py preview   section "Final (preview, in progress)" at the top of the sheets, from 00_share/final_v01/preview/
# python _build/build_a3_v09.py final     the same section as "Final", PNGs from final_v01/png, buttons to Release a3-final-v01 (or repo files)
#   Edits a3-groundtruth/index.html in place between <!--final:start--> and <!--final:end--> (re-runnable); images in a3-groundtruth/final/
import glob, html, importlib.util, os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE); PAGE = os.path.join(SITE, "a3-groundtruth")
FIN = r"Z:\_F26_Fall-2026\2_ett3-26\Assignments-ett3\assignment-3_ground-truth\00_share\final_v01"
REL = "https://github.com/laserpirate/ett3/releases/download/a3-final-v01/"
TITLES = {"00": "Title page", "PIN-01": "Part A · Patch Delineation", "PIN-02": "Part B · Ground-Truthed Patch Map", "PIN-03": "Part C · Plot + Transect",
          "PIN-04": "Part C · Plants", "PIN-05": "Part C · Field Notes + Observations", "PIN-06": "Site Photos", "PIN-07": "Nest · Habitat Feature"}


def card(sid, png, tag):
    e = html.escape; os.makedirs(os.path.join(PAGE, "final"), exist_ok=True)
    full, web = "final/ett3-A3_%s_%s.png" % (sid, tag), "final/ett3-A3_%s_%s.webp" % (sid, tag)
    im = Image.open(png).convert("RGB"); im.save(os.path.join(PAGE, full), optimize=True)
    im.resize((1200, round(1200 * im.height / im.width)), Image.LANCZOS).save(os.path.join(PAGE, web), quality=82)
    return ('<figure class="card"><button type="button" data-full="%s" data-name="%s %s"><img src="%s" alt="%s %s" loading="lazy" width="1200" height="776">'
            '</button><figcaption><b>%s</b> %s</figcaption></figure>' % (full, sid, e(TITLES[sid]), web, sid, e(TITLES[sid]), sid, e(TITLES[sid])))


def main(mode, stamp):
    p = os.path.join(PAGE, "index.html"); t = open(p, encoding="utf-8").read()
    if mode == "preview":
        pngs = {sid: os.path.join(FIN, "preview", "ett3-A3_%s_preview_v01.png" % sid) for sid in TITLES}
        head = '<h2>Final (preview, in progress)</h2><p class="older">First-pass renders of the final PIN set from the group\'s material (Fernanda\'s plant catalog, field observations, nest photos). Updated %s. The printable PDF follows.</p>' % stamp
        btn = ""
    else:
        pngs = {sid: f for sid in TITLES for f in glob.glob(os.path.join(FIN, "png", "ett3-A3_%s_*.png" % sid))}
        head = '<h2>Final · PIN set (title + 7)</h2><p class="older">Pin-up Fri Oct 30 2026, 12 pm, 11x17 landscape, print at actual size. Built %s.</p>' % stamp
        href = sys.argv[3] if len(sys.argv) > 3 else REL
        btn = ('<div class="row"><a class="btn main" href="%sett3-A3_PIN-set_final_v01.pdf">Submission PDF (final)</a>'
               '<a class="btn main" href="%sett3-A3_final_package_v01.zip">Editable package (final)</a></div>' % (href, href))
    sec = "<!--final:start-->" + head + btn + '<div class="grid">\n' + "\n".join(card(k, pngs[k], mode) for k in TITLES) + "\n</div><!--final:end-->"
    if "<!--final:start-->" in t:
        t2 = re.sub(r"<!--final:start-->.*?<!--final:end-->", lambda m: sec, t, flags=re.S)
    else:
        t2 = t.replace("<h2>PIN · submission set", sec + "\n<h2>PIN · submission set", 1)
    assert t2 != t
    open(p, "w", encoding="utf-8", newline="\n").write(t2)
    _s = importlib.util.spec_from_file_location("b1", os.path.join(HERE, "build_a3_v01.py")); b1 = importlib.util.module_from_spec(_s); _s.loader.exec_module(b1)
    b1.gate()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
