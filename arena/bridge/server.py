"""Arena bridge: очередь вопросов к arena.ai с ограничением частоты.

Транспорт — userscript в обычном браузере пользователя (arena-bridge.user.js)
или ручной режим через веб-страницу http://localhost:8765/ .
Только stdlib.
"""
import json, os, time, uuid, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

DATA = os.environ.get("DATA_DIR", "/data")
MIN_INTERVAL = int(os.environ.get("MIN_INTERVAL_SEC", "120"))   # не чаще 1 вопроса в 2 мин
DAILY_CAP = int(os.environ.get("DAILY_CAP", "40"))
QUEUE = os.path.join(DATA, "queue")
ANSWERS = os.path.join(DATA, "answers")
STATE = os.path.join(DATA, "state.json")
os.makedirs(QUEUE, exist_ok=True)
os.makedirs(ANSWERS, exist_ok=True)
lock = threading.Lock()


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_issue": 0, "day": "", "count": 0, "inflight": {}}


def save_state(s):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)


def pending():
    items = []
    for name in sorted(os.listdir(QUEUE)):
        if name.endswith(".json"):
            with open(os.path.join(QUEUE, name), encoding="utf-8") as f:
                items.append(json.load(f))
    return items


def answered_ids():
    return {n[:-5] for n in os.listdir(ANSWERS) if n.endswith(".json")}


PAGE = """<!doctype html><meta charset=utf-8><title>Arena bridge</title>
<style>body{font:14px system-ui;max-width:900px;margin:20px auto;padding:0 16px}
pre{white-space:pre-wrap;background:#f4f4f4;padding:8px}textarea{width:100%;height:120px}</style>
<h2>Arena bridge — очередь</h2><p id=st></p><div id=q></div>
<script>
async function load(){const r=await (await fetch('/status')).json();
document.getElementById('st').textContent=JSON.stringify(r.limits);
const q=document.getElementById('q');q.innerHTML='';
for(const it of r.pending){const d=document.createElement('div');
d.innerHTML=`<h3>${it.id} (${it.tag||''})</h3><pre>${it.text.replace(/</g,'&lt;')}</pre>
<button onclick="navigator.clipboard.writeText(document.getElementById('t_${it.id}').textContent)">copy</button>
<span hidden id=t_${it.id}></span>
<p>Модель A: <input id=ma_${it.id}> Модель B: <input id=mb_${it.id}></p>
<textarea id=a_${it.id} placeholder="ответ A"></textarea><textarea id=b_${it.id} placeholder="ответ B"></textarea>
<button onclick="send('${it.id}')">сохранить ответ</button><hr>`;
q.appendChild(d);document.getElementById('t_'+it.id).textContent=it.text;}}
async function send(id){const v=k=>document.getElementById(k+'_'+id).value;
await fetch('/answer',{method:'POST',headers:{'content-type':'application/json'},
body:JSON.stringify({id,source:'manual',responses:[{model:v('ma'),text:v('a')},{model:v('mb'),text:v('b')}]})});load();}
load();
</script>"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj, ctype="application/json"):
        body = obj.encode() if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, "")

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        with lock:
            s = load_state()
            today = time.strftime("%Y-%m-%d")
            if s["day"] != today:
                s.update(day=today, count=0)
            done = answered_ids()
            pend = [p for p in pending() if p["id"] not in done]
            if self.path.startswith("/cmd?"):
                target = self.path.split("target=")[1]
                c = s.pop("cmd_" + target, None)
                save_state(s)
                return self._send(200, {"cmd": c})
            if self.path == "/rpc/next":
                q = s.get("rpcq", [])
                it = q.pop(0) if q else None
                s["rpcq"] = q; save_state(s)
                return self._send(200, it or {})
            if self.path.startswith("/rpc/result?id="):
                rid = self.path.split("=", 1)[1]
                fp = os.path.join(DATA, "rpc", rid + ".json")
                if os.path.exists(fp):
                    with open(fp, encoding="utf-8") as f:
                        return self._send(200, json.load(f))
                return self._send(200, {"pending": True})
            if self.path == "/version":
                try:
                    with open(os.path.join(DATA, "extension", "VERSION"), encoding="utf-8") as f:
                        return self._send(200, f.read().strip(), "text/plain")
                except Exception:
                    return self._send(200, "0", "text/plain")
            if self.path.endswith(".user.js"):
                with open(os.path.join(DATA, "extension", "montihol-bridge.user.js"), encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/javascript")
            if self.path == "/":
                return self._send(200, PAGE, "text/html")
            if self.path == "/status":
                wait = max(0, int(s["last_issue"] + MIN_INTERVAL - time.time()))
                return self._send(200, {"pending": pend, "limits": {
                    "today": s["count"], "cap": DAILY_CAP, "next_in_sec": wait}})
            if self.path.startswith("/next"):
                print("REQLOG", time.strftime("%H:%M:%S"), self.path, self.headers.get("Origin"), flush=True)
                target = (self.path.split("target=")[1] if "target=" in self.path else "arena")
                lk = "last_" + target
                now = time.time()
                if s["count"] >= DAILY_CAP:
                    return self._send(200, {"wait": "daily_cap"})
                if now - s.get(lk, 0) < MIN_INTERVAL:
                    return self._send(200, {"wait": int(s.get(lk, 0) + MIN_INTERVAL - now)})
                # не выдаём повторно то, что выдано < 10 мин назад
                cand = [p for p in pend if p.get("target", "arena") == target and now - s["inflight"].get(p["id"], 0) > 600]
                if not cand:
                    return self._send(200, {"wait": "empty"})
                it = cand[0]
                s["inflight"][it["id"]] = now
                s["last_issue"] = now
                s[lk] = now
                s["count"] += 1
                save_state(s)
                return self._send(200, it)
            if self.path == "/answers":
                out = []
                for n in sorted(os.listdir(ANSWERS)):
                    with open(os.path.join(ANSWERS, n), encoding="utf-8") as f:
                        out.append(json.load(f))
                return self._send(200, out)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        b = self._body()
        with lock:
            if self.path == "/ask":
                it = {"id": b.get("id") or time.strftime("%m%d%H%M%S-") + uuid.uuid4().hex[:4],
                      "text": b["text"], "tag": b.get("tag", ""), "target": b.get("target", "arena"), "created": time.time()}
                with open(os.path.join(QUEUE, it["id"] + ".json"), "w", encoding="utf-8") as f:
                    json.dump(it, f, ensure_ascii=False, indent=1)
                return self._send(200, it)
            if self.path == "/rpc":
                s0 = load_state(); b["id"] = b.get("id") or uuid.uuid4().hex[:10]
                s0.setdefault("rpcq", []).append(b); save_state(s0)
                return self._send(200, {"id": b["id"]})
            if self.path == "/rpc/result":
                os.makedirs(os.path.join(DATA, "rpc"), exist_ok=True)
                with open(os.path.join(DATA, "rpc", b["id"] + ".json"), "w", encoding="utf-8") as f:
                    json.dump(b, f, ensure_ascii=False)
                return self._send(200, {"ok": True})
            if self.path == "/cmdset":
                s0 = load_state(); s0["cmd_" + b["target"]] = b["cmd"]; save_state(s0)
                return self._send(200, {"ok": True})
            if self.path == "/diag":
                line = time.strftime("%H:%M:%S") + " " + json.dumps(b, ensure_ascii=False)
                with open(os.path.join(DATA, "diag.log"), "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                return self._send(200, {"ok": True})
            if self.path == "/shot":
                import base64
                name = time.strftime("%H%M%S") + "-" + b.get("target", "x") + ".jpg"
                os.makedirs(os.path.join(DATA, "shots"), exist_ok=True)
                with open(os.path.join(DATA, "shots", name), "wb") as f:
                    f.write(base64.b64decode(b["data"].split(",", 1)[1]))
                return self._send(200, {"ok": True, "file": name})
            if self.path == "/error":
                line = time.strftime("%H:%M:%S") + " " + json.dumps(b, ensure_ascii=False)
                print("ERRLOG", line, flush=True)
                with open(os.path.join(DATA, "errors.log"), "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                s0 = load_state(); s0["inflight"].pop(b.get("id", ""), None); save_state(s0)
                return self._send(200, {"ok": True})
            if self.path == "/answer":
                b["received"] = time.time()
                with open(os.path.join(ANSWERS, b["id"] + ".json"), "w", encoding="utf-8") as f:
                    json.dump(b, f, ensure_ascii=False, indent=1)
                return self._send(200, {"ok": True})
        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"arena bridge on :8765, interval={MIN_INTERVAL}s cap={DAILY_CAP}/day", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8765), H).serve_forever()
