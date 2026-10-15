// Перечитать готовый чат: node rescrape.mjs <url> <out.md>
import fs from "fs";
const CDP = process.env.CDP || "http://127.0.0.1:9222";
const list = await (await fetch(`${CDP}/json`)).json();
const t = list.find(x => x.type === "page" && /arena\.ai|chatgpt|gemini/.test(x.url));
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const W = new Map(); ws.onmessage = e => { const m = JSON.parse(e.data); if (W.has(m.id)) { W.get(m.id)(m); W.delete(m.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; W.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send("Page.navigate", { url: process.argv[2] });
let txt = "";
for (let i = 0; i < 60; i++) {
  await new Promise(r => setTimeout(r, 5000));
  txt = (await send("Runtime.evaluate", { expression: "document.body.innerText || document.body.textContent", returnByValue: true })).result?.result?.value || "";
  if (txt.length > 2000 && !/Generating|Searching|Thinking/.test(txt)) break;
}
fs.writeFileSync(process.argv[3], `${process.argv[2]}\n\n## Ответ\n${txt}`); ws.close(); console.log("ok", txt.length);
