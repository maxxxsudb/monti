// Montihol bridge (страница): только держит фон активным (ping каждые 3 с) и показывает плашку.
// Всё управление — из фона через chrome.debugger по командам модератора.
if (window.top === window && !document.prerendering) {
  const badge = document.createElement("div");
  badge.style.cssText = "position:fixed;bottom:8px;left:8px;z-index:2147483647;background:#222;color:#0f0;font:12px monospace;padding:4px 8px;border-radius:6px;opacity:.8;pointer-events:none";
  badge.textContent = "montihol: на связи";
  document.documentElement.appendChild(badge);
  const iv = setInterval(() => {
    if (!chrome.runtime?.id) { clearInterval(iv); badge.textContent = "montihol: устарел, обновите вкладку"; return; }
    try { chrome.runtime.sendMessage({ op: "ping" }, () => void chrome.runtime.lastError); } catch (e) {}
  }, 3000);
}
