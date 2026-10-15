// Драйвер: берёт вопрос из очереди (docker, :8765) и задаёт его в ОБЫЧНОМ окне Edge,
// где пользователь сам прошёл проверку arena.ai. Управление через DevTools-порт 9222.
// Без маскировки; частоту ограничивает сервер очереди (1 вопрос / 2 мин, 40/день).
// Запуск: node arena/driver.mjs        (Node >= 22, без зависимостей)

const BRIDGE = "http://127.0.0.1:8765";
const CDP = "http://127.0.0.1:9222";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function tab() {
  const list = await (await fetch(`${CDP}/json`)).json();
  const t = list.find((x) => x.type === "page" && /arena\.ai/.test(x.url));
  if (!t) throw new Error("Нет вкладки arena.ai в окне Edge");
  return t;
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const waiting = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m); waiting.delete(m.id); }
  };
  const send = (method, params = {}) =>
    new Promise((res) => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  return new Promise((res) => (ws.onopen = () => res({ ws, send })));
}

async function evaluate(send, expr) {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  return r.result?.result?.value;
}

const SNAPSHOT = `(() => {
  const blocks = [...document.querySelectorAll('.prose, [class*="markdown"], [class*="message"]')]
    .map(e => e.innerText.trim()).filter(t => t.length > 20);
  const uniq = blocks.filter(b => !blocks.some(o => o !== b && o.includes(b)));
  return { url: location.href, title: document.title, body: document.body.innerText,
           main: (() => { const m = document.querySelector('main') || document.body; const c = m.cloneNode(true); c.querySelectorAll('script,style').forEach(x => x.remove()); return m.innerText || c.textContent; })(), blocks: uniq };
})()`;

async function askOne(item) {
  const t = await tab();
  const { ws, send } = await connect(t.webSocketDebuggerUrl);
  try {
    await send("Page.navigate", { url: "https://arena.ai/" });
    await sleep(8000);
    const title = await evaluate(send, "document.title");
    if (/момент|moment|attention/i.test(title)) throw new Error("Страница проверки — пройдите её вручную в окне Edge");
    await send("Page.bringToFront");
    await send("Emulation.setFocusEmulationEnabled", { enabled: true });
    await sleep(1000);
    const ok = await evaluate(send, `(() => {
      const ta = document.querySelector('textarea[placeholder^="Ask"]') || document.querySelector('textarea');
      if (!ta) return false;
      ta.focus();
      const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      set.call(ta, ${JSON.stringify(item.text)});
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      return true; })()`);
    if (!ok) throw new Error("Не найдено поле ввода");
    await sleep(1500);
    const clicked = await evaluate(send, `(() => {
      const b = document.querySelector('button[aria-label="Send message"]');
      if (!b || b.disabled) return false; b.click(); return true; })()`);
    if (!clicked) throw new Error("Кнопка отправки недоступна (текст не вставился?)");
    for (let i = 0; i < 10 && !/\/c\//.test(await evaluate(send, "location.href")); i++) await sleep(2000);
    if (!/\/c\//.test(await evaluate(send, "location.href"))) throw new Error("Сообщение не ушло (URL не /c/)");
    // ждём: нет "Generating", текст стабилен 20 с; максимум 8 минут
    let last = "", stableSince = Date.now(), snap;
    const start = Date.now();
    while (Date.now() - start < 480000) {
      await sleep(5000);
      snap = await evaluate(send, SNAPSHOT);
      if (!snap || !/arena\.ai/.test(snap.url))
        throw new Error("Ушли с arena.ai (вход/проверка?) — нужен ручной вход в окне Edge");
      const cur = snap.body || "";
      const busy = /Generating|Thinking|Генерир/i.test(cur);
      if (cur !== last) { last = cur; stableSince = Date.now(); }
      else if (!busy && Date.now() - stableSince > 20000 && Date.now() - start > 40000) break;
    }
    return snap;
  } finally { ws.close(); }
}

console.log("driver: жду вопросы из очереди", BRIDGE);
for (;;) {
  let item;
  try { item = await (await fetch(`${BRIDGE}/next`)).json(); }
  catch { console.log("очередь недоступна"); await sleep(30000); continue; }
  if (!item.id) { await sleep(typeof item.wait === "number" ? Math.min(item.wait, 60) * 1000 + 1000 : 30000); continue; }
  console.log(new Date().toISOString(), "вопрос", item.id, item.tag || "");
  try {
    const snap = await askOne(item);
    await fetch(`${BRIDGE}/answer`, { method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ id: item.id, tag: item.tag, question: item.text, source: "edge-cdp", snapshot: snap }) });
    console.log("  ответ сохранён, блоков:", snap?.blocks?.length);
  } catch (e) { console.log("  ошибка:", e.message); await sleep(60000); }
}
