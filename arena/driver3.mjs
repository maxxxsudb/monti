// Драйвер через расширение (chrome.debugger в основном профиле Яндекса): очередь :8765 -> ChatGPT / Gemini / Arena.
// Настоящие события ввода (Input.insertText + Enter), ожидание нового ответа по счётчику, сохранение в answers/.
// Запуск: node arena/driver3.mjs [chatgpt,gemini,arena]
import fs from "fs";
import { rpc, evaluate } from "./rpc.mjs";

const BRIDGE = "http://127.0.0.1:8765";
const TARGETS = (process.argv[2] || "chatgpt,gemini,arena").split(",");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const SITES = {
  chatgpt: {
    home: "https://chatgpt.com/",
    input: `document.querySelector('#prompt-textarea, .ProseMirror[contenteditable="true"]')`,
    count: `document.querySelectorAll('[data-message-author-role="assistant"]').length`,
    busy: `!!document.querySelector('[data-testid="stop-button"]')`,
    answer: `(() => { const a = document.querySelectorAll('[data-message-author-role="assistant"]'); return a.length ? a[a.length-1].innerText : ''; })()`,
  },
  gemini: {
    home: "https://gemini.google.com/u/1/app",
    input: `document.querySelector('rich-textarea .ql-editor')`,
    count: `document.querySelectorAll('model-response').length`,
    busy: `!!document.querySelector('button[aria-label*="Stop"], button[aria-label*="Останов"], .stop-icon')`,
    answer: `(() => { const a = document.querySelectorAll('model-response'); return a.length ? a[a.length-1].innerText : ''; })()`,
  },
  arena: {
    home: "https://arena.ai/",
    input: `(document.querySelector('textarea[placeholder^="Ask"]') || document.querySelector('textarea'))`,
    count: `0`,
    busy: `/Generating|Searching|Thinking|Reasoning/.test(document.body.innerText)`,
    answer: `document.body.innerText`,
  },
};

async function ask(target, item) {
  const S = SITES[target];
  await rpc(target, "Page.navigate", { url: S.home });
  for (let i = 0; i < 20 && !(await evaluate(target, `!!${S.input}`).catch(() => false)); i++) await sleep(1500);
  if (!(await evaluate(target, `!!${S.input}`))) throw new Error("нет поля ввода");
  const n0 = await evaluate(target, S.count);
  await rpc(target, "Emulation.setFocusEmulationEnabled", { enabled: true });
  await evaluate(target, `${S.input}.focus()`);
  {
    await sleep(4000);   // дать странице догидратироваться
    await evaluate(target, `${S.input}.focus()`);
    await rpc(target, "Input.insertText", { text: item.text });
  }
  await sleep(1500);
  const clicked = await evaluate(target, `(() => { const b = document.querySelector('[data-testid="send-button"], button[aria-label="Send message"], button[aria-label*="Отправ"], button[aria-label*="Send"], button.send-button');
    if (b && !b.disabled && b.getAttribute('aria-disabled') !== 'true') { b.click(); return true; } return false; })()`);
  if (!clicked)
    for (const type of ["keyDown", "keyUp"])
      await rpc(target, "Input.dispatchKeyEvent", { type, key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await sleep(5000);
  if (target === "arena") {
    if (!/\/c\//.test(await evaluate(target, "location.href"))) {
      await evaluate(target, `document.querySelector('button[aria-label="Send message"]')?.click()`);
      await sleep(5000);
    }
    if (!/\/c\//.test(await evaluate(target, "location.href"))) throw new Error("arena: сообщение не ушло");
  } else {
    const t0 = Date.now();
    while ((await evaluate(target, S.count)) <= n0) {
      if (Date.now() - t0 > 240000) throw new Error("новый ответ не появился");
      await sleep(3000);
    }
  }
  let last = "", stable = Date.now();
  const start = Date.now();
  while (Date.now() - start < 20 * 60000) {
    await sleep(5000);
    const t = (await evaluate(target, S.answer)) || "";
    const busy = await evaluate(target, S.busy);
    if (t !== last) { last = t; stable = Date.now(); }
    else if (!busy && t && Date.now() - stable > 25000) break;
  }
  return { url: await evaluate(target, "location.href"), text: last };
}

console.log("driver3:", TARGETS.join(","));
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
    } catch (e) {
      console.log("  ошибка", target, e.message);
      await fetch(`${BRIDGE}/error`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ id: item.id, target, error: e.message }) }).catch(() => {});
    }
  }
  if (!worked) await sleep(15000);
}
