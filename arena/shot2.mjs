import fs from "fs"; import { rpc } from "./rpc.mjs";
const r = await rpc(process.argv[2], "Page.captureScreenshot", { format: "jpeg", quality: 45 });
fs.writeFileSync(process.argv[3], Buffer.from(r.data, "base64")); console.log("ok");
