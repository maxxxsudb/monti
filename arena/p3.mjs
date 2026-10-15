const list = await (await fetch("http://127.0.0.1:9223/json")).json();
for (const t of list.filter(x=>x.type==="page")) {
  const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
  const v = await new Promise(r=>{ ws.onmessage=e=>r(JSON.parse(e.data).result?.result?.value); ws.send(JSON.stringify({id:1,method:"Runtime.evaluate",params:{expression:process.argv[2],returnByValue:true}})); });
  console.log(t.url.slice(0,40), "=>", JSON.stringify(v)); ws.close();
}
