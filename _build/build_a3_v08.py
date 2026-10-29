# ett3 site · A3 · build v08 · group packet v01 (PIN / REF); build_a3_v07 kept and reused for the gate and the live checks
# python _build/build_a3_v08.py            share page: "Group packet (editable)" + "Submission set (PDF)" buttons, sheet grid regrouped under PIN and REF
# python _build/build_a3_v08.py --crawl    fetch the share page and every src / href on it (200 or FAIL)
#   Edits a3-groundtruth/index.html in place (the v07 output); sheet images: the group packet PNGs as 1200 px WebP + full PNG in sheets/.
import glob, html, importlib.util, os, re, sys, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PAGE = os.path.join(SITE, "a3-groundtruth")
PKG = r"Z:\_F26_Fall-2026\2_ett3-26\Assignments-ett3\assignment-3_ground-truth\00_share\group-packet_v01\ett3-A3_group-packet_v01"
ZIP = os.path.join(os.path.dirname(PKG), "ett3-A3_group-packet_v01.zip")
REL = "https://github.com/laserpirate/ett3/releases/download/a3-group-packet-v01/"
TITLES = {"00": "Read First", "00b": "Read First · register (cont.)", "PIN-01": "Part A · Patch Delineation", "PIN-02": "Part B · Ground-Truthed Patch Map",
          "PIN-03": "Part C · Plot + Transect", "PIN-04": "Part C · Plants", "PIN-05": "Part C · Field Drawings", "PIN-06": "Site Photos",
          "PIN-07": "Nest Habitat Adaptation", "REF-01": "D2 Alt · Contours + Fallen Tree", "REF-02": "D2 Alt · Contours + Mesh", "REF-03": "Species Table",
          "REF-04": "Scan Atlas", "REF-05": "Splat Atlas", "REF-06": "Data", "REF-07": "Blank Base Plan"}


def card(sid, png):
    e = html.escape
    b = os.path.splitext(os.path.basename(png))[0]
    full, web = "sheets/%s.png" % b, "sheets/%s.webp" % b
    if not os.path.exists(os.path.join(PAGE, web)):
        im = Image.open(png).convert("RGB")
        im.save(os.path.join(PAGE, full), optimize=True)
        im.resize((1200, round(1200 * im.height / im.width)), Image.LANCZOS).save(os.path.join(PAGE, web), quality=82)
    return ('<figure class="card"><button type="button" data-full="%s" data-name="%s %s"><img src="%s" alt="%s" loading="lazy" width="1200" height="776">'
            '</button><figcaption><b>%s</b> %s</figcaption></figure>' % (full, sid, e(TITLES[sid]), web, b, sid, e(TITLES[sid])))


def main():
    p = os.path.join(PAGE, "index.html"); t = open(p, encoding="utf-8").read()
    pngs = {re.search(r"ett3-A3_(\w+-?\d*\w?)_", os.path.basename(f)).group(1): f for f in glob.glob(os.path.join(PKG, "0*", "png", "*.png"))}
    mb = lambda f: "%.0f MB" % (os.path.getsize(f) / 1e6)
    btn = ('<a class="btn main" href="%sett3-A3_group-packet_v01.zip">Group packet (editable, %s)</a>'
           '<a class="btn main" href="%sett3-A3_PIN-set_v01.pdf">Submission set (PDF, %s)</a>'
           '<a class="btn" href="%sett3-A3_full-packet_v01.pdf">Full packet PDF (%s)</a>'
           % (REL, mb(ZIP), REL, mb(os.path.join(PKG, "ett3-A3_PIN-set_v01.pdf")), REL, mb(os.path.join(PKG, "ett3-A3_full-packet_v01.pdf"))))
    t = t.replace('<div class="row"><a class="btn main" href="https://github.com/laserpirate/ett3/releases/download/a3-groundtruth-packet-v06/',
                  '<div class="row">' + btn + '<a class="btn" href="https://github.com/laserpirate/ett3/releases/download/a3-groundtruth-packet-v06/', 1)
    pin = [k for k in TITLES if not k.startswith("REF")]; ref = [k for k in TITLES if k.startswith("REF")]
    grids = ('<h2>PIN · submission set (%d)</h2><p class="older">Submitted on Canvas and pinned up Fri Oct 30, 12 pm, 11x17. Magenta text = placeholder for the group.</p>'
             '<div class="grid">\n%s\n</div>\n<h2>REF · internal reference (%d)</h2><p class="older">For the group\'s design work only, not submitted.</p><div class="grid">\n%s\n</div>'
             % (len(pin), "\n".join(card(k, pngs[k]) for k in pin), len(ref), "\n".join(card(k, pngs[k]) for k in ref)))
    t2 = re.sub(r'<h2>Sheets \(\d+\)</h2><div class="grid">.*?</div>(?=<footer>)', lambda m: grids, t, count=1, flags=re.S)
    assert t2 != t and "Group packet (editable" in t2
    t2 = re.sub(r"Built [^<]*?· packet v06", "Built %s · group packet v01" % __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (UTC%z)"), t2)
    open(p, "w", encoding="utf-8", newline="\n").write(t2)
    _s = importlib.util.spec_from_file_location("b1", os.path.join(HERE, "build_a3_v01.py")); b1 = importlib.util.module_from_spec(_s); _s.loader.exec_module(b1)
    b1.gate()


def crawl():
    u = "https://laserpirate.github.io/ett3/a3-groundtruth/"
    body = urllib.request.urlopen(u, timeout=30).read().decode("utf-8", "replace")
    ok = n = 0
    for r in sorted(set(re.findall(r'(?:src|href|data-full|poster)="([^"#]+)"', body))):
        if r.startswith("data:") or r.startswith("mailto:"):
            continue
        a = urllib.parse.urljoin(u, r); n += 1
        try:
            req = urllib.request.Request(a, method="HEAD"); c = urllib.request.urlopen(req, timeout=30).status
        except Exception as ex:
            c = getattr(ex, "code", str(ex))
        ok += c == 200
        if c != 200:
            print("FAIL", c, a)
    print("crawl share page %d/%d" % (ok, n), "PIN heading" if "PIN · submission set" in body else "NO PIN HEADING (cache?)")


if __name__ == "__main__":
    import urllib.parse
    crawl() if "--crawl" in sys.argv else main()
