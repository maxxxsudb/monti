// ==UserScript==
// @name         Montihol bridge
// @version      1.0
// @description  Вопросы из локальной очереди 127.0.0.1:8765 -> ChatGPT / Gemini / Arena
// @match        https://chatgpt.com/*
// @match        https://gemini.google.com/*
// @match        https://arena.ai/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @run-at       document-idle
// ==/UserScript==
// Montihol bridge: работает только в одной вкладке на сайт (флаг в sessionStorage), задаёт вопрос из очереди и отправляет ответ.
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const host = location.host;
const SITE = host.includes("chatgpt") ? {
  target: "chatgpt",
  input: () => document.querySelector("#prompt-textarea"),
  send: () => document.querySelector('[data-testid="send-button"]'),
  busy: () => !!document.querySelector('[data-testid="stop-button"]'),
  count: () => document.querySelectorAll('[data-message-author-role="assistant"]').length,
  answer: () => { const a = document.querySelectorAll('[data-message-author-role="assistant"]'); return a.length ? a[a.length - 1].innerText : ""; },
  home: "https://chatgpt.com/", newChat: true,
} : host.includes("gemini") ? {
  target: "gemini",
  input: () => document.querySelector("rich-textarea .ql-editor, .ql-editor[contenteditable='true']"),
  send: () => document.querySelector("button[aria-label='Отправить сообщение'], button[aria-label='Send message'], .send-button-container button, button.send-button, button[aria-label*='Отправ'], button[aria-label*='Send']"),
  busy: () => !!document.querySelector("button[aria-label*='Stop'], button[aria-label*='Останов']"),
  count: () => document.querySelectorAll("model-response").length,
  answer: () => { const a = document.querySelectorAll("model-response"); return a.length ? a[a.length - 1].innerText : ""; },
  home: "https://gemini.google.com/app", newChat: false,
} : {
  target: "arena",
  input: () => document.querySelector('textarea[placeholder^="Ask"]') || document.querySelector("textarea"),
  send: () => document.querySelector('button[aria-label="Send message"]'),
  busy: () => /Generating|Searching|Thinking/.test(document.body.innerText),
  count: () => 0,
  answer: () => document.body.innerText,
  home: "https://arena.ai/", newChat: true,
};
const call = (m) => new Promise(r => {
  const url = m.op === "next" ? `http://127.0.0.1:8765/next?target=${m.target}` : `http://127.0.0.1:8765/${m.op}`;
  GM_xmlhttpRequest({ method: m.op === "next" ? "GET" : "POST", url,
    headers: { "content-type": "application/json" }, data: m.op === "next" ? undefined : JSON.stringify(m.body),
    onload: (x) => { try { r(JSON.parse(x.responseText)); } catch { r({}); } }, onerror: () => r({}) });
}); } else r(x || {}); }); }
  catch (e) { log("ошибка sendMessage:", e.message); r({}); }
});
const badge = document.createElement("div");
badge.id = "montihol-badge";
badge.style.cssText = "position:fixed;bottom:8px;left:8px;z-index:2147483647;background:#222;color:#0f0;font:12px monospace;padding:4px 8px;border-radius:6px;opacity:.85;pointer-events:none";
document.documentElement.appendChild(badge);
const log = (...a) => { console.log("[montihol]", ...a); badge.textContent = "montihol: " + a.join(" "); };
log("скрипт загружен");

function setText(el, text) {
  el.focus();
  if (el.tagName === "TEXTAREA") {
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value").set.call(el, text);
    el.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    document.execCommand("selectAll", false);
    document.execCommand("insertText", false, text);
  }
}

async function askOne(item) {
  const el = SITE.input();
  if (!el) throw new Error("нет поля ввода");
  const n0 = SITE.count();
  setText(el, item.text);
  await sleep(1500);
  let b = null;
  for (let i = 0; i < 10; i++) {            // ждём, пока кнопка станет активной
    b = SITE.send();
    if (b && !b.disabled && b.getAttribute("aria-disabled") !== "true") break;
    await sleep(500);
  }
  if (b && !b.disabled && b.getAttribute("aria-disabled") !== "true") { b.click(); log("нажал отправить"); }
  else {
    log("кнопка не найдена — Enter");
    for (const type of ["keydown", "keypress", "keyup"])
      el.dispatchEvent(new KeyboardEvent(type, { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true }));
  }
  await sleep(4000);
  if (SITE.target !== "arena" && SITE.count() <= n0 && (SITE.input()?.innerText || SITE.input()?.value || "").trim().length > 20)
    throw new Error("текст не отправлен: кнопка=" + (b ? (b.getAttribute("aria-label") || b.className) : "нет"));
  await sleep(8000);
  if (SITE.target !== "arena") {           // ждём появления НОВОГО ответа
    const t0 = Date.now();
    while (SITE.count() <= n0) { if (Date.now() - t0 > 300000) throw new Error("новый ответ не появился"); await sleep(3000); }
  }
  log("пишет ответ…");
  let last = "", stable = Date.now();
  const start = Date.now();
  while (Date.now() - start < 15 * 60 * 1000) {
    await sleep(5000);
    const t = SITE.answer();
    if (t !== last) { last = t; stable = Date.now(); }
    else if (!SITE.busy() && t && Date.now() - stable > 25000) break;
  }
  return last;
}

(async () => {
  // одна рабочая вкладка на сайт: первая открытая забирает «замок»
  const key = "montihol-worker-" + SITE.target;
  const now = Date.now();
  const lock = JSON.parse(localStorage.getItem(key) || "null");
  if (lock && now - lock.t < 60000 && lock.id !== sessionStorage.getItem(key)) return log("другая вкладка уже работает");
  const myId = sessionStorage.getItem(key) || String(Math.random());
  sessionStorage.setItem(key, myId);
  setInterval(() => localStorage.setItem(key, JSON.stringify({ id: myId, t: Date.now() })), 20000);
  localStorage.setItem(key, JSON.stringify({ id: myId, t: now }));
  log("готов, цель:", SITE.target);
  for (;;) {
    const item = await call({ op: "next", target: SITE.target });
    if (!item || !item.id) { log("жду вопрос", item && (item.error || JSON.stringify(item.wait ?? ""))); await sleep(30000); continue; }
    log("вопрос", item.id);
    try {
      if (!SITE.input()) { location.href = SITE.home; return; }
      const text = await askOne(item);
      await call({ op: "answer", body: { id: item.id, tag: item.tag, target: SITE.target, question: item.text, url: location.href, text, source: "extension" } });
      log("ответ сохранён", text.length);
    } catch (e) {
      log("ошибка", e.message);
      await call({ op: "error", body: { id: item.id, target: SITE.target, error: e.message, url: location.href,
        input: !!SITE.input(), send: !!SITE.send(), count: SITE.count() } });
    }
    await sleep(5000);
    if (SITE.newChat) { location.href = SITE.home; return; }   // ChatGPT/Arena: новый чат; Gemini: остаёмся в текущем (контекст «Астрон»)
  }
})();
