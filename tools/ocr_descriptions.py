"""images/idols/*.jpg を Google Cloud Vision API で OCR し，
各メンバーの「名前」と「説明文」を抽出して data/idols.json の description/name を更新する．

前提:
  pip install google-cloud-vision
  環境変数 GOOGLE_APPLICATION_CREDENTIALS にサービスアカウント鍵JSONの絶対パスを設定
  または gcloud auth application-default login を済ませておく

画像は「あなたは○○タイプです！！」というタイトル＋吹き出し内の説明段落，
という共通レイアウト．タイトル行からメンバー名を，それ以外を説明文として抽出する．

重複画像 (例: akb_kami7/1a と josei_2019/1a は同じ画像) は
unique な画像ファイル単位で1回だけ OCR し，同じIDの全エントリに展開する．
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from google.cloud import vision

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
IMAGES_DIR = REPO_ROOT / "images" / "idols"
OCR_CACHE = REPO_ROOT / "tools" / ".ocr_cache.json"  # API呼び出し節約用


TITLE_RE = re.compile(r"あなたは(.+?)タイプです")


def load_cache() -> dict[str, dict]:
    if OCR_CACHE.exists():
        return json.loads(OCR_CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, dict]) -> None:
    OCR_CACHE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8",
    )


def ocr_one(client: vision.ImageAnnotatorClient, image_path: Path) -> str:
    """Vision API の DOCUMENT_TEXT_DETECTION 結果をプレーンテキストで返す."""
    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    # 日本語ヒント
    response = client.document_text_detection(
        image=image,
        image_context=vision.ImageContext(language_hints=["ja"]),
    )
    if response.error.message:
        raise RuntimeError(f"Vision API error: {response.error.message}")
    return response.full_text_annotation.text if response.full_text_annotation else ""


def parse_text(raw: str) -> tuple[str | None, str]:
    """OCR 生テキストから (name, description) を取り出す．

    想定レイアウト:
        あなたは指原莉乃タイプです！！
        指原莉乃タイプのあなたは,
        おしゃべりが好きで,活発な,社交性が...
        （中略）
        ...じタイプです。
    """
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    name: str | None = None
    description_lines: list[str] = []

    for ln in lines:
        m = TITLE_RE.search(ln)
        if m and name is None:
            name = m.group(1).strip("　 ")
            continue
        description_lines.append(ln)

    # 改行を維持しつつ空白を詰める
    description = "\n".join(description_lines)
    # 「○○タイプのあなたは，」で始まる冗長な導入を除去しない (そのまま温存)
    return name, description


def main() -> None:
    idols_path = DATA_DIR / "idols.json"
    idols = json.loads(idols_path.read_text(encoding="utf-8"))

    # ユニーク画像ファイル一覧
    unique_images = sorted({idol["image"] for idol in idols})
    print(f"[1/3] OCR 対象: {len(unique_images)} 画像 (重複排除済)")

    cache = load_cache()
    client = vision.ImageAnnotatorClient()

    print(f"[2/3] Vision API 呼び出し中 ...")
    for i, img in enumerate(unique_images, 1):
        if img in cache:
            print(f"    [{i:3d}/{len(unique_images)}] {img}  (cached)")
            continue
        path = IMAGES_DIR / img
        if not path.exists():
            print(f"    [{i:3d}/{len(unique_images)}] {img}  SKIP (file not found)")
            continue
        try:
            raw = ocr_one(client, path)
        except Exception as e:
            print(f"    [{i:3d}/{len(unique_images)}] {img}  ERROR: {e}")
            continue
        name, desc = parse_text(raw)
        cache[img] = {"raw": raw, "name": name, "description": desc}
        save_cache(cache)  # 逐次保存 (途中失敗への保険)
        print(f"    [{i:3d}/{len(unique_images)}] {img}  name={name!r}")

    print(f"[3/3] idols.json を更新中 ...")
    updated = 0
    name_filled = 0
    for idol in idols:
        cached = cache.get(idol["image"])
        if not cached:
            continue
        if cached["description"]:
            idol["description"] = cached["description"]
            updated += 1
        if not idol.get("name") and cached.get("name"):
            idol["name"] = cached["name"]
            name_filled += 1

    idols_path.write_text(
        json.dumps(idols, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"    -> description を埋めた: {updated} 件")
    print(f"    -> name を補完した: {name_filled} 件")
    print(f"    完了．tools/.ocr_cache.json に生OCR結果を保存してあります．")
    print(f"    精度チェックは data/idols.json を直接見て必要に応じ手修正してください．")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
