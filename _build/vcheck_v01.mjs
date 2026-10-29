// ett3 site · headless Chrome check that the autoplay videos actually play (readyState >= 2, paused false)
// node _build/vcheck_v01.mjs <url> [<url> ...]   (Node 22, global WebSocket; Chrome DevTools protocol, no packages)
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PORT = 9333;
const prof = mkdtempSync(join(tmpdir(), "ett3vc-"));
const ch = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${prof}`, "--autoplay-policy=no-user-gesture-required",
  "--window-size=1440,900", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ok = true;
try {
  let tabs;
  for (let i = 0; i < 40; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); break; } catch { await sleep(250); } }
  const page = tabs.find((t) => t.type === "page");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r));
  let id = 0; const pend = new Map();
  ws.addEventListener("message", (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  const send = (method, params = {}) => new Promise((r) => { const k = ++id; pend.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
  for (const url of process.argv.slice(2)) {
    await send("Page.enable");
    await send("Page.navigate", { url });
    await sleep(6000);
    const r = await send("Runtime.evaluate", { returnByValue: true, expression:
      "JSON.stringify([].map.call(document.querySelectorAll('video[autoplay]'),v=>({src:(v.currentSrc||'').split('/').pop(),readyState:v.readyState,paused:v.paused,t:+v.currentTime.toFixed(2)})))" });
    const vids = JSON.parse(r.result.result.value || "[]");
    const good = vids.length > 0 && vids.every((v) => v.readyState >= 2 && !v.paused);
    ok = ok && good;
    console.log(good ? "PLAYING" : "FAIL", url, JSON.stringify(vids));
  }
  ws.close();
} finally {
  ch.kill();
}
process.exit(ok ? 0 : 1);
