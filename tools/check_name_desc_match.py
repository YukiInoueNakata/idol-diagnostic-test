# /// script
# requires-python = ">=3.11"
# ///
"""data/idols.json の各エントリで name と description 冒頭の「○○タイプのあなたは」が一致するかチェック．
ズレを一覧表示する．
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IDOLS = REPO_ROOT / "data" / "idols.json"

# description 内に最初に出てくる「○○タイプのあなたは」を拾う
DESC_TYPE_RE = re.compile(r"([^\s,，。、！!？?]+?)タイプのあなたは")

idols = json.loads(IDOLS.read_text(encoding="utf-8"))

mismatched = []
no_marker = []
for idol in idols:
    name = (idol.get("name") or "").strip()
    desc = idol.get("description") or ""
    m = DESC_TYPE_RE.search(desc)
    if not m:
        no_marker.append((idol["group"], idol["id"], name))
        continue
    desc_name = m.group(1).strip()
    # 全角空白除去や TWICE 接頭を吸収する簡易正規化
    norm_name = name.replace("TWICE", "").replace("　", "").strip()
    if desc_name != norm_name:
        mismatched.append({
            "group": idol["group"],
            "id": idol["id"],
            "name": name,
            "desc_name": desc_name,
        })

print(f"全 {len(idols)} エントリ中")
print(f"  description 冒頭マーカー無し: {len(no_marker)} 件")
print(f"  name ≠ desc_name のズレ: {len(mismatched)} 件")
print()
if no_marker:
    print("[マーカー無し]")
    for g, i, n in no_marker:
        print(f"  {g} / {i} / name={n!r}")
    print()
if mismatched:
    print("[ズレ一覧]")
    for r in mismatched:
        print(f"  {r['group']:25s} / {r['id']:4s} / name={r['name']!r:20s} / desc冒頭={r['desc_name']!r}")
