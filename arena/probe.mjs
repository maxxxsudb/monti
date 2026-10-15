const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const t = list.find(x => x.type==="page" && /arena\.ai/.test(x.url));
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
const expr = process.argv[2];
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id===1){ console.log(JSON.stringify(m.result?.result?.value ?? m.result, null, 1)); ws.close(); } };
ws.send(JSON.stringify({id:1, method:"Runtime.evaluate", params:{expression:expr, returnByValue:true, awaitPromise:true}}));
