import fs from "fs";
const list = await (await fetch((process.env.CDP||"http://127.0.0.1:9222")+"/json")).json();
const t = list.find(x => x.type==="page" && /arena\.ai/.test(x.url));
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id===1){ fs.writeFileSync(process.argv[2], Buffer.from(m.result.data,"base64")); ws.close(); } };
ws.send(JSON.stringify({id:1, method:"Page.captureScreenshot", params:{format:"jpeg", quality:40}}));
