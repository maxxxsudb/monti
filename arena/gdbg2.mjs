import { rpc, evaluate } from "./rpc.mjs";
const T = "gemini", sleep = (ms) => new Promise(r => setTimeout(r, ms));
const q = () => evaluate(T, "({q: document.querySelectorAll('user-query').length, inp: document.querySelector('rich-textarea .ql-editor')?.innerText.slice(0,20)})");
const x = 1082, y = 305;
await rpc(T, "Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
await sleep(200);
await rpc(T, "Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", buttons: 1, clickCount: 1 });
await sleep(120);
await rpc(T, "Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", buttons: 0, clickCount: 1 });
await sleep(4000);
console.log("клик buttons:1", JSON.stringify(await q()));
const s = await q();
if (s.q === 0) {
  await evaluate(T, "document.querySelector('rich-textarea .ql-editor').focus()");
  await rpc(T, "Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", text: "\r", unmodifiedText: "\r", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await rpc(T, "Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
  await sleep(4000);
  console.log("Enter с text", JSON.stringify(await q()));
}
