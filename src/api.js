// Google Apps Script Web App への POST 送信．
// オフライン時は localStorage にキューし，次回起動時に再送．

const QUEUE_KEY = "idol_pending_submissions";

/** config.js で設定するエンドポイントURL (GAS デプロイ後に埋め込む) */
export async function getEndpoint() {
  const res = await fetch("./config.json", { cache: "no-store" });
  if (!res.ok) throw new Error("config.json not found");
  const cfg = await res.json();
  if (!cfg.gasEndpoint) throw new Error("gasEndpoint is empty in config.json");
  return cfg.gasEndpoint;
}

/** 送信失敗分を localStorage に積む */
function enqueue(record) {
  const existing = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
  existing.push(record);
  localStorage.setItem(QUEUE_KEY, JSON.stringify(existing));
}

/** 積んであった失敗分を順次再送．成功したものは取り除く． */
export async function flushQueue() {
  const queue = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
  if (queue.length === 0) return { sent: 0, remaining: 0 };
  let endpoint;
  try {
    endpoint = await getEndpoint();
  } catch {
    return { sent: 0, remaining: queue.length };
  }
  const remaining = [];
  let sent = 0;
  for (const r of queue) {
    try {
      await postOnce(endpoint, r);
      sent += 1;
    } catch {
      remaining.push(r);
    }
  }
  localStorage.setItem(QUEUE_KEY, JSON.stringify(remaining));
  return { sent, remaining: remaining.length };
}

async function postOnce(endpoint, record) {
  // GAS は fetch の CORS をシンプルに扱うため text/plain で送るのが無難
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify(record),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * 1件の受検結果を送信．
 * 失敗時はキューに積んで後で再送．
 */
export async function submitRecord(record) {
  try {
    const endpoint = await getEndpoint();
    await postOnce(endpoint, record);
    return { ok: true };
  } catch (e) {
    enqueue(record);
    return { ok: false, error: String(e), queued: true };
  }
}
