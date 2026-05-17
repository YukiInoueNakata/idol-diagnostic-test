# /// script
# requires-python = ">=3.11"
# ///
"""data/idols.json に対し:
  1. 画像と説明に名前を合わせる (A 案・5 件)
  2. 表記ゆれ (typo) を修正 (3 件)
  3. TWICE グループの Big5 値を 0.7 倍に縮約 (1~10 → 概ね 1~7 へ寄せる)
を適用する．冪等．バックアップは .bak で 1 世代だけ残す．
"""
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IDOLS = REPO_ROOT / "data" / "idols.json"

# 1. 画像と一致するように name を上書き
NAME_FIX_IMAGE_ALIGN: dict[tuple[str, str], str] = {
    ("josei_2019", "4a"): "斉藤飛鳥",     # was 西野七瀬
    ("josei_2019", "4b"): "西野七瀬",     # was 斉藤飛鳥
    ("twice",      "10a"): "サナ",        # was モモ
    ("twice",      "10b"): "ジヒョ",      # was サナ
    ("twice",      "10f"): "モモ",        # was ジヒョ
}

# 2. typo 修正 (画像 OCR が正)
NAME_FIX_TYPO: dict[tuple[str, str], str] = {
    ("niziu",       "6h"):  "MIIHI",       # was MIHI
    ("dansei_1980", "7e"):  "西城秀樹",     # was 西条秀樹 (條→城)
    ("snow_man",    "11b"): "深澤辰哉",     # was 深澤辰也
}

# 3. TWICE Big5 を 0.7 倍してスケールを揃える (1~10 → 0.7~7)
TWICE_GROUP_ID = "twice"
SCALE_FACTOR = 0.7


def main() -> None:
    shutil.copyfile(IDOLS, IDOLS.with_suffix(".json.bak"))
    idols = json.loads(IDOLS.read_text(encoding="utf-8"))

    summary = {
        "name_aligned_to_image": [],
        "name_typo_fixed": [],
        "twice_big5_rescaled": [],
    }

    for idol in idols:
        key = (idol["group"], idol["id"])
        if key in NAME_FIX_IMAGE_ALIGN:
            old = idol.get("name")
            idol["name"] = NAME_FIX_IMAGE_ALIGN[key]
            summary["name_aligned_to_image"].append(
                f"{key[0]}/{key[1]}: {old!r} -> {idol['name']!r}"
            )
        if key in NAME_FIX_TYPO:
            old = idol.get("name")
            idol["name"] = NAME_FIX_TYPO[key]
            summary["name_typo_fixed"].append(
                f"{key[0]}/{key[1]}: {old!r} -> {idol['name']!r}"
            )
        if idol["group"] == TWICE_GROUP_ID:
            old_big5 = dict(idol["big5"])
            new_big5 = {k: round(v * SCALE_FACTOR, 4) for k, v in idol["big5"].items()}
            idol["big5"] = new_big5
            summary["twice_big5_rescaled"].append(
                f"{key[1]} ({idol['name']}): "
                + " ".join(f"{k}={old_big5[k]}→{new_big5[k]}" for k in ["E","A","C","N","O"])
            )

    IDOLS.write_text(json.dumps(idols, ensure_ascii=False, indent=2), encoding="utf-8")

    print("== 修正サマリ ==")
    print(f"\n[A 案] 画像と一致するように name を変更 ({len(summary['name_aligned_to_image'])} 件)")
    for line in summary["name_aligned_to_image"]:
        print(f"  {line}")
    print(f"\n[typo 修正] ({len(summary['name_typo_fixed'])} 件)")
    for line in summary["name_typo_fixed"]:
        print(f"  {line}")
    print(f"\n[TWICE Big5 × {SCALE_FACTOR}] ({len(summary['twice_big5_rescaled'])} 件)")
    for line in summary["twice_big5_rescaled"]:
        print(f"  {line}")
    print(f"\nバックアップ: {IDOLS.with_suffix('.json.bak').name}")


if __name__ == "__main__":
    main()
