// ett3 site · screenshots with real device emulation (headless Chrome cannot size a window below about 500 px)
// node _build/shots_v01.mjs <out dir> <url> [<url> ...]   -> shot_<slug>_1440.png and shot_<slug>_390.png (viewport + full page), plus overflow check
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PORT = 9334;
const [out, ...urls] = process.argv.slice(2);
const prof = mkdtempSync(join(tmpdir(), "ett3sh-"));
const ch = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${prof}`, "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const rep = [];
try {
  let tabs;
  for (let i = 0; i < 40; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); break; } catch { await sleep(250); } }
  const ws = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r));
  let id = 0; const pend = new Map();
  ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  const send = (method, params = {}) => new Promise((r) => { const k = ++id; pend.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
  await send("Page.enable");
  for (const url of urls) {
    const slug = url.replace(/^https?:\/\/[^/]+\//, "").replace(/\/$/, "").replace(/\//g, "_") || "root";
    for (const [w, h, mobile, dpr] of [[1440, 900, false, 1], [390, 844, true, 2]]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile });
      await send("Page.navigate", { url: url + "?v=" + Date.now() });
      await sleep(5000);
      const r = await send("Runtime.evaluate", { returnByValue: true, expression:
        "JSON.stringify({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, sh: document.documentElement.scrollHeight, broken: [].filter.call(document.images, i => i.complete && i.naturalWidth === 0 && !i.src.startsWith('data:')).map(i => i.src)})" });
      const m = JSON.parse(r.result.result.value);
      rep.push({ url, w, overflow_x: m.sw > m.cw, ...m });
      let s = await send("Page.captureScreenshot", { format: "png" });
      writeFileSync(join(out, `shot_${slug}_${w}.png`), Buffer.from(s.result.data, "base64"));
    }
  }
} finally { ch.kill(); }
writeFileSync(join(out, "shots_v01.json"), JSON.stringify(rep, null, 1));
for (const r of rep) console.log(r.w, r.overflow_x ? "OVERFLOW" : "ok", r.sw + "/" + r.cw, "broken " + r.broken.length, r.url);
