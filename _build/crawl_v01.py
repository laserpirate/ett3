# ett3 site · live crawl: every A3 page, every link / image / video / download on it (HEAD, GET fallback), screenshots at 1440 and 390 px
# python _build/crawl_v01.py <out dir>
import json, os, re, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://laserpirate.github.io/ett3/"
PAGES = ["", "a3-groundtruth/"] + ["a3-groundtruth/%s/" % p for p in ("plans", "views", "photos", "species", "gsplat", "animations", "nest")]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)


def get(u, method="GET"):
    r = urllib.request.Request(u, method=method, headers={"User-Agent": "ett3-crawl", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(r, timeout=60) as f:
        return f.status, (f.read() if method == "GET" else b""), f.headers.get("Content-Length")


def check(u):
    try:
        s, _, n = get(u, "HEAD"); return u, s, n
    except Exception as e:
        try:
            s, b, _ = get(u); return u, s, str(len(b))
        except Exception as e2:
            return u, str(e2)[:80], None


rep = {"pages": {}, "links": {}}
links = set()
for p in PAGES:
    u = BASE + p; s, b, _ = get(u); t = b.decode("utf-8", "ignore"); rep["pages"][u] = s
    for m in re.findall(r'(?:href|src|data-full)="([^"#]+)"', t):
        if m.startswith(("mailto:", "javascript:")):
            continue
        links.add(urllib.parse.urljoin(u, m))
with ThreadPoolExecutor(12) as ex:
    for u, s, n in ex.map(check, sorted(links)):
        rep["links"][u] = [s, n]
bad = {u: v for u, v in rep["links"].items() if v[0] != 200}
rep["n_links"] = len(links); rep["bad"] = bad
for p in PAGES:
    name = (p.strip("/").replace("/", "_") or "root")
    for w, h in ((1440, 900), (390, 844)):
        png = os.path.join(OUT, "shot_%s_%d.png" % (name, w))
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=%d,%d" % (w, h), "--virtual-time-budget=8000",
                        "--screenshot=%s" % png, BASE + p + "?v=crawl"], capture_output=True, timeout=120)
json.dump(rep, open(os.path.join(OUT, "crawl_v01.json"), "w"), indent=1)
print("pages", rep["pages"]); print("links", len(links), "bad", len(bad))
for u, v in bad.items():
    print("  BAD", v, u)
