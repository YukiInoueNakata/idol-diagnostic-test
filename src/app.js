// セッション状態を sessionStorage で画面間受け渡し．

const SESSION_KEY = "idol_session";

export function saveSession(patch) {
  const cur = JSON.parse(sessionStorage.getItem(SESSION_KEY) || "{}");
  const merged = { ...cur, ...patch };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(merged));
  return merged;
}

export function loadSession() {
  return JSON.parse(sessionStorage.getItem(SESSION_KEY) || "{}");
}

export function clearSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

/** data/ 配下のJSONを取得 */
export async function fetchJson(relpath) {
  const res = await fetch(relpath, { cache: "no-store" });
  if (!res.ok) throw new Error(`${relpath}: HTTP ${res.status}`);
  return res.json();
}

/** 質問セットの一覧 (data/question-sets/ のディレクトリ一覧はブラウザから取れないので index.json を介する) */
export async function loadQuestionSets() {
  const index = await fetchJson("../data/question-sets/index.json");
  const sets = await Promise.all(
    index.map((id) => fetchJson(`../data/question-sets/${id}.json`)),
  );
  return sets;
}

export async function loadIdols() {
  return fetchJson("../data/idols.json");
}

export async function loadGroups() {
  return fetchJson("../data/groups.json");
}

/** PC識別子: config.json.pcName → localStorage → userAgent フォールバック */
export async function getPcName() {
  try {
    const cfg = await fetchJson("./config.json");
    if (cfg.pcName) return cfg.pcName;
  } catch { /* noop */ }
  let name = localStorage.getItem("idol_pc_name");
  if (!name) {
    const ua = navigator.userAgent;
    name = "pc-" + Math.abs(hashStr(ua)).toString(36).slice(0, 6);
    localStorage.setItem("idol_pc_name", name);
  }
  return name;
}

function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return h;
}
