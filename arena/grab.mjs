// node grab.mjs <target> <id>  — сохранить текущую переписку вкладки как ответ на вопрос id
import fs from "fs"; import { evaluate } from "./rpc.mjs";
const [target, id] = process.argv.slice(2);
const r = await evaluate(target, `({ url: location.href, text: document.body.innerText })`);
const q = JSON.parse(fs.readFileSync(new URL(`./queue/${id}.json`, import.meta.url), "utf8"));
fs.writeFileSync(new URL(`./answers/${id}.md`, import.meta.url), `# ${id} (${target})\n${r.url}\n\n## Вопрос\n${q.text}\n\n## Ответ\n${r.text}\n`);
await fetch("http://127.0.0.1:8765/answer", { method: "POST", headers: { "content-type": "application/json" },
  body: JSON.stringify({ id, target, question: q.text, url: r.url, text: r.text, source: "grab" }) });
console.log("saved", r.text.length);
