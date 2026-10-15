// Фон Montihol bridge.
// 1) RPC: модератор кладёт CDP-команды в очередь сервера (/rpc), фон выполняет их во вкладке через chrome.debugger
//    и возвращает результат (/rpc/result). Даёт полное управление без перезагрузок.
// 2) Самообновление: при смене VERSION на сервере расширение перечитывается с диска.
const BRIDGE = "http://127.0.0.1:8765";
const SITES = { chatgpt: "https://chatgpt.com/*", gemini: "https://gemini.google.com/*", arena: "https://arena.ai/*" };
const attached = new Set();

async function post(path, body) {
  return fetch(`${BRIDGE}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
}

async function findTab(target) {
  if (typeof target === "number") return target;
  const tabs = await chrome.tabs.query({ url: SITES[target] || target });
  if (!tabs.length) throw new Error("нет вкладки " + target);
  tabs.sort((a, b) => (b.active - a.active) || (b.lastAccessed || 0) - (a.lastAccessed || 0));
  return tabs[0].id;
}

async function attach(tabId) {
  if (attached.has(tabId)) return;
  try { await chrome.debugger.attach({ tabId }, "1.3"); }
  catch (e) {
    // старое подключение этого же расширения (после перезапуска фона) — отключаем и подключаемся заново
    try { await chrome.debugger.detach({ tabId }); } catch (_) {}
    try { await chrome.debugger.attach({ tabId }, "1.3"); }
    catch (e2) { throw new Error(String(e2.message || e2) + " — возможно, на вкладке открыты DevTools (F12)"); }
  }
  attached.add(tabId);
}
chrome.debugger.onDetach.addListener((src) => attached.delete(src.tabId));

async function runRpc(r) {
  if (r.method === "tabs") {
    const tabs = await chrome.tabs.query({});
    return tabs.filter(t => /chatgpt|gemini|arena/.test(t.url || "")).map(t => ({ id: t.id, url: t.url, title: t.title, active: t.active }));
  }
  const tabId = await findTab(r.target);
  if (r.method === "ownWindow") {               // вынести вкладку в отдельное окно, чтобы она всегда была активной
    const t = await chrome.tabs.get(tabId);
    const others = await chrome.tabs.query({ windowId: t.windowId });
    if (others.length > 1) await chrome.windows.create({ tabId, focused: false, state: "normal", width: 1280, height: 900 });
    return { ok: true, moved: others.length > 1 };
  }
  if (r.method === "activate") { await chrome.tabs.update(tabId, { active: true }); return { ok: true }; }
  await attach(tabId);
  return await chrome.debugger.sendCommand({ tabId }, r.method, r.params || {});
}

let busy = false;
async function pump() {
  if (busy) return;
  busy = true;
  try {
    for (let i = 0; i < 20; i++) {
      const r = await (await fetch(`${BRIDGE}/rpc/next`)).json();
      if (!r.id) break;
      let out;
      try { out = { id: r.id, ok: true, result: await runRpc(r) }; }
      catch (e) { out = { id: r.id, ok: false, error: String(e && e.message || e) }; }
      await post("/rpc/result", out);
    }
  } catch (e) { /* сервер недоступен */ }
  busy = false;
}

// держим фон живым и часто опрашиваем очередь: content-скрипты пингуют каждые 3 с
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg.op === "ping") { pump(); reply({ ok: true }); return false; }
  if (msg.op === "next" || msg.op === "answer" || msg.op === "diag" || msg.op === "error") {
    const url = msg.op === "next" ? `${BRIDGE}/next?target=${msg.target}` : `${BRIDGE}/${msg.op}`;
    const init = msg.op === "next" ? {} : { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(msg.body) };
    fetch(url, init).then(r => r.json()).then(reply).catch(e => reply({ error: String(e) }));
    return true;
  }
  return false;
});

async function checkVersion() {
  try {
    const v = (await (await fetch(`${BRIDGE}/version`)).text()).trim();
    const { loaded } = await chrome.storage.local.get("loaded");
    if (!loaded) return chrome.storage.local.set({ loaded: v });
    if (v && v !== loaded) { await chrome.storage.local.set({ loaded: v }); chrome.runtime.reload(); }
  } catch (e) {}
}

async function reloadSiteTabs() {
  for (const t of await chrome.tabs.query({ url: Object.values(SITES) })) chrome.tabs.reload(t.id);
}

chrome.alarms.create("tick", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener(() => { checkVersion(); pump(); });
chrome.runtime.onInstalled.addListener(async () => {
  const v = (await fetch(`${BRIDGE}/version`).then(r => r.text()).catch(() => "")).trim();
  await chrome.storage.local.set({ loaded: v });
  reloadSiteTabs();
});
chrome.runtime.onStartup.addListener(checkVersion);
