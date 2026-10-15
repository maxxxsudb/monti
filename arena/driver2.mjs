// Общий драйвер: очередь (docker :8765) -> вкладки отдельного профиля Яндекс Браузера (DevTools :9223).
// Цели: arena | chatgpt | gemini. Вход в аккаунты пользователь делает сам; обхода защит нет.
// Частоту ограничивает сервер очереди отдельно для каждой цели.
// Запуск: node arena/driver2.mjs [targets через запятую]
import fs from "fs";

const BRIDGE = "http://127.0.0.1:8765";
const CDP = process.env.CDP || "http://127.0.0.1:9223";
const TARGETS = (process.argv[2] || "arena,chatgpt,gemini").split(",");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const SITES = {
  arena: {
    host: /arena\.ai/, home: "https://arena.ai/",
    input: `document.querySelector('textarea[placeholder^="Ask"]') || document.querySelector('textarea')`,
    native: true,
    send: `document.querySelector('button[aria-label="Send message"]')`,
    sent: (url) => /\/c\//.test(url),
    busy: /Generating|Thinking|Searching|Reasoning/i,
    extract: `document.body.innerText || document.body.textContent`,
  },
  chatgpt: {
    host: /chatgpt\.com/, home: "https://chatgpt.com/",
    input: `document.querySelector('#prompt-textarea')`,
    send: `document.querySelector('[data-testid="send-button"]')`,
    sent: (url) => /\/c\//.test(url),
    busyJs: `!!document.querySelector('[data-testid="stop-button"]')`,
    extract: `(() => { const a = [...document.querySelectorAll('[data-message-author-role="assistant"]')]; return a.length ? a[a.length-1].innerText : ''; })()`,
  },
  gemini: {
    host: /gemini\.google\.com/, home: "https://gemini.google.com/app",
    input: `document.querySelector('rich-textarea .ql-editor, div.ql-editor[contenteditable="true"], [contenteditable="true"]')`,
    send: `document.querySelector('button.send-button, button[aria-label*="Send"], button[aria-label*="Отправ"]')`,
    sent: (url) => /\/app\/[0-9a-f]/.test(url),
    busyJs: `!!document.querySelector('button[aria-label*="Stop"], button[aria-label*="Останов"]')`,
    extract: `(() => { const a = [...document.querySelectorAll('model-response, .model-response-text')]; return a.length ? a[a.length-1].innerText : ''; })()`,
  },
};

async function connect(site) {
  const list = await (await fetch(`${CDP}/json`)).json();
  let t = list.find((x) => x.type === "page" && site.host.test(x.url));
  if (!t) t = await (await fetch(`${CDP}/json/new?${site.home}`, { method: "PUT" })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m); waiting.delete(m.id); } };
  const closed = new Promise((_, rej) => (ws.onclose = () => rej(new Error("соединение с вкладкой закрыто"))));
  closed.catch(() => {});
  const send = (method, params = {}) => Promise.race([closed,
    new Promise((res) => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); })]);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error("ws error")); });
  const ev = async (expr) => (await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true })).result?.result?.value;
  return { ws, send, ev };
}

async function ask(target, item) {
  const site = SITES[target];
  const { ws, send, ev } = await connect(site);
  try {
    await send("Page.bringToFront");
    await send("Emulation.setFocusEmulationEnabled", { enabled: true });
    await send("Page.navigate", { url: site.home });
    await sleep(9000);
    const url0 = await ev("location.href");
    if (!site.host.test(url0)) throw new Error("не на сайте (вход?): " + url0);
    if (!(await ev(`!!(${site.input})`))) throw new Error("нет поля ввода (нужен вход?)");
    if (site.native) {
      await ev(`(() => { const ta = ${site.input}; ta.focus();
        Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, ${JSON.stringify(item.text)});
        ta.dispatchEvent(new Event('input', { bubbles: true })); })()`);
    } else {
      await ev(`(${site.input}).focus()`);
      await send("Input.insertText", { text: item.text });
    }
    await sleep(2000);
    const clicked = await ev(`(() => { const b = ${site.send}; if (!b || b.disabled) return false; b.click(); return true; })()`);
    if (!clicked) {
      for (const type of ["keyDown", "keyUp"])
        await send("Input.dispatchKeyEvent", { type, key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
    }
    for (let i = 0; i < 15 && !site.sent(await ev("location.href")); i++) await sleep(2000);
    if (!site.sent(await ev("location.href"))) throw new Error("сообщение не ушло");
    // ждём окончания генерации: текст стабилен 25 с и нет признаков генерации; максимум 15 минут (Pro думает долго)
    let last = "", stable = Date.now(), text = "";
    const start = Date.now();
    while (Date.now() - start < 900000) {
      await sleep(5000);
      text = (await ev(site.extract)) || "";
      const body = site.busy ? await ev("document.body.innerText") : "";
      const busy = (site.busyJs && (await ev(site.busyJs))) || (site.busy && site.busy.test(body));
      if (text !== last) { last = text; stable = Date.now(); }
      else if (!busy && text.length > 0 && Date.now() - stable > 25000) break;
    }
    return { url: await ev("location.href"), text };
  } finally { ws.close(); }
}

console.log("driver2:", TARGETS.join(","), "via", CDP);
for (;;) {
  let worked = false;
  for (const target of TARGETS) {
    let item;
    try { item = await (await fetch(`${BRIDGE}/next?target=${target}`)).json(); } catch { continue; }
    if (!item.id) continue;
    worked = true;
    console.log(new Date().toISOString(), target, "вопрос", item.id);
    try {
      const r = await ask(target, item);
      await fetch(`${BRIDGE}/answer`, { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: item.id, tag: item.tag, target, question: item.text, url: r.url, text: r.text }) });
      fs.writeFileSync(new URL(`./answers/${item.id}.md`, import.meta.url), `# ${item.id} (${target})\n${r.url}\n\n## Вопрос\n${item.text}\n\n## Ответ\n${r.text}\n`);
      console.log("  ответ сохранён", target, r.text.length, "симв.");
    } catch (e) { console.log("  ошибка", target, e.message); }
  }
  if (!worked) await sleep(20000);
}
