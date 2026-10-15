import { rpc, evaluate } from "./rpc.mjs";
const T = "gemini";
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
await rpc(T, "Emulation.setFocusEmulationEnabled", { enabled: true });
const st = async () => evaluate(T, `({inp:(document.querySelector('rich-textarea .ql-editor')||{}).innerText?.slice(0,30), q: document.querySelectorAll('user-query').length, r: document.querySelectorAll('model-response').length,
  btn: (b => b && {l: b.getAttribute('aria-label'), r: b.getBoundingClientRect().toJSON(), d: b.disabled})(document.querySelector('button[aria-label="Send message"], button[aria-label*="Отправ"]')), vis: document.visibilityState})`);
await rpc(T, "Page.navigate", { url: "https://gemini.google.com/u/1/app" });
for (let i = 0; i < 20 && !(await evaluate(T, "!!document.querySelector('rich-textarea .ql-editor')").catch(() => false)); i++) await sleep(1500);
await evaluate(T, "document.querySelector('rich-textarea .ql-editor').focus()");
await rpc(T, "Input.insertText", { text: "Ответь одним словом: ок" });
await sleep(1500);
console.log("до", JSON.stringify(await st()));
const s = await st();
if (s.btn) {
  const x = s.btn.r.x + s.btn.r.width / 2, y = s.btn.r.y + s.btn.r.height / 2;
  for (const type of ["mouseMoved", "mousePressed", "mouseReleased"])
    await rpc(T, "Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount: 1 });
  await sleep(4000);
  console.log("после клика мышью", JSON.stringify(await st()));
}
const s2 = await st();
if (s2.q === 0) {
  await evaluate(T, `document.querySelector('rich-textarea .ql-editor').focus()`);
  await rpc(T, "Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await rpc(T, "Input.dispatchKeyEvent", { type: "char", text: "\r", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await rpc(T, "Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await sleep(4000);
  console.log("после Enter(raw+char)", JSON.stringify(await st()));
}
