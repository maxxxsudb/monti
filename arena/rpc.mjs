// Клиент управления браузером пользователя через расширение.
// Использование как модуль: import { rpc, evaluate } from "./rpc.mjs"
// CLI: node rpc.mjs <target|tabs> [method] [paramsJSON]
const BRIDGE = "http://127.0.0.1:8765";
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
export async function rpc(target, method, params = {}, timeout = 60000) {
  const { id } = await (await fetch(`${BRIDGE}/rpc`, { method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ target, method, params }) })).json();
  const t0 = Date.now();
  for (;;) {
    const r = await (await fetch(`${BRIDGE}/rpc/result?id=${id}`)).json();
    if (!r.pending) { if (!r.ok) throw new Error(r.error); return r.result; }
    if (Date.now() - t0 > timeout) throw new Error("rpc timeout " + method);
    await sleep(400);
  }
}
export async function evaluate(target, expression) {
  const r = await rpc(target, "Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + (r.exceptionDetails.exception?.description || ""));
  return r.result?.value;
}
if (process.argv[1] && import.meta.url.endsWith("rpc.mjs") && process.argv[1].endsWith("rpc.mjs")) {
  const [target, method = "tabs", params = "{}"] = process.argv.slice(2);
  const res = target === "tabs" ? await rpc(null, "tabs") : method === "eval" ? await evaluate(target, params) : await rpc(target, method, JSON.parse(params));
  console.log(JSON.stringify(res, null, 1).slice(0, 4000));
}
