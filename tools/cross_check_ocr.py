# /// script
# requires-python = ">=3.11"
# ///
"""OCR cache の各画像から取得した name と，idols.json の name を突き合わせて
画像 vs 計算用シート の食い違いを網羅検出する．
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE = REPO_ROOT / "tools" / ".ocr_cache.json"
IDOLS = REPO_ROOT / "data" / "idols.json"

cache = json.loads(CACHE.read_text(encoding="utf-8"))
idols = json.loads(IDOLS.read_text(encoding="utf-8"))

TITLE_RE = re.compile(r"あなたは(.+?)タイプです")

# 1 画像 = 1 OCR name (ユニーク)．各エントリ (group, id, name) を画像 OCR name と比べる
mismatches = []
for idol in idols:
    img = idol["image"]
    cached = cache.get(img)
    if not cached:
        continue
    ocr_name = (cached.get("name") or "").strip()
    json_name = (idol.get("name") or "").strip()
    # 全角空白除去等の弱正規化
    norm_json = json_name.replace("　", "").replace("TWICE", "").strip()
    norm_ocr = ocr_name.replace("　", "").replace("TWICE", "").strip()
    if not norm_ocr:
        continue
    if norm_json != norm_ocr:
        mismatches.append({
            "group": idol["group"],
            "id": idol["id"],
            "image": img,
            "json_name": json_name,
            "ocr_name": ocr_name,
        })

print(f"画像 OCR name と idols.json name のミスマッチ: {len(mismatches)} 件\n")
for m in mismatches:
    print(f"  {m['group']:25s} / id={m['id']:5s} / image={m['image']:8s} / json={m['json_name']!r:18s} / ocr={m['ocr_name']!r}")
