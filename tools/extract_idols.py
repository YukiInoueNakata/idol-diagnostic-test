"""xlsm の 計算用シート から全11グループ・76名の Big Five 値と ID を抽出し，
idols.json と groups.json を生成する．画像は output/ から images/idols/ へコピー．

一度きりの移行ツール．実行後は data/idols.json を手で編集する運用になる．
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from openpyxl import load_workbook

# ---------------------------------------------------------------------------
# パス設定
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
# OneDrive 上の日本語長パスだと PermissionError になりがちなので，
# 同ディレクトリに ASCII 名でコピーしたファイルを優先して読む
_LOCAL_COPY = REPO_ROOT.parent / "アイドル診断テスト2025" / "test_source.xlsm"
_ORIGINAL = REPO_ROOT.parent / "アイドル診断テスト2025" / "アイドル診断テストオリジナル本体　20250518.xlsm"
SRC_XLSM = _LOCAL_COPY if _LOCAL_COPY.exists() else _ORIGINAL
SRC_OUTPUT_DIR = REPO_ROOT.parent / "アイドル診断テスト2025" / "output"

DATA_DIR = REPO_ROOT / "data"
IMAGES_IDOLS_DIR = REPO_ROOT / "images" / "idols"

# ---------------------------------------------------------------------------
# グループ定義
#   計算用シートの配置を丁寧にマッピング．
#   label_row: メンバーID (1a, 2b ...) が並ぶ行
#   name_row : 本名が並ぶ行 (無い場合は None)
#   big5_start_row: 外向性の値がある行 (以降 協調性/勤勉性/神経症/開放性 が続く)
#   col_start, col_end: メンバーが並ぶ列 (両端含む)
# ---------------------------------------------------------------------------
GROUPS: list[dict] = [
    {
        "id": "akb_kami7",
        "name": "AKB48 神7",
        "label_row": 2, "name_row": None, "big5_start_row": 3,
        "col_start": "B", "col_end": "J",
        "enabled_default": True,
    },
    {
        "id": "dansei_general",
        "name": "男性アイドル (関ジャニ・嵐ほか)",
        "label_row": 2, "name_row": None, "big5_start_row": 3,
        "col_start": "K", "col_end": "S",
        "enabled_default": False,
    },
    {
        "id": "joshi_koukousei_2018",
        "name": "高校生版 2018",
        "label_row": 14, "name_row": 13, "big5_start_row": 15,
        "col_start": "B", "col_end": "F",
        "enabled_default": False,
    },
    {
        "id": "josei_2019",
        "name": "女性アイドル 2019",
        "label_row": 37, "name_row": 36, "big5_start_row": 38,
        "col_start": "B", "col_end": "G",
        "enabled_default": False,
    },
    {
        "id": "king_and_prince",
        "name": "King & Prince",
        "label_row": 61, "name_row": 60, "big5_start_row": 62,
        "col_start": "B", "col_end": "F",
        "enabled_default": False,
    },
    {
        "id": "niziu",
        "name": "NiziU",
        "label_row": 73, "name_row": 72, "big5_start_row": 74,
        "col_start": "B", "col_end": "J",
        "enabled_default": True,
    },
    {
        "id": "dansei_1980",
        "name": "1980年代男性アイドル",
        "label_row": 85, "name_row": 84, "big5_start_row": 86,
        "col_start": "B", "col_end": "F",
        "enabled_default": True,
    },
    {
        "id": "josei_1980",
        "name": "1980年代女性アイドル",
        "label_row": 97, "name_row": 96, "big5_start_row": 98,
        "col_start": "B", "col_end": "F",
        "enabled_default": False,
    },
    {
        "id": "bts",
        "name": "BTS",
        "label_row": 109, "name_row": 108, "big5_start_row": 110,
        "col_start": "B", "col_end": "H",
        "enabled_default": True,
    },
    {
        "id": "twice",
        "name": "TWICE Top6",
        "label_row": 121, "name_row": 120, "big5_start_row": 122,
        "col_start": "B", "col_end": "G",
        "enabled_default": True,
    },
    {
        "id": "snow_man",
        "name": "Snow Man",
        "label_row": 133, "name_row": 132, "big5_start_row": 134,
        "col_start": "B", "col_end": "J",
        "enabled_default": True,
    },
]

BIG5_KEYS = ["E", "A", "C", "N", "O"]  # 外向性 協調性 勤勉性 神経症傾向 開放性


def _col_range(start: str, end: str) -> list[str]:
    """Excel列アルファベットの範囲展開 (A..Z)．本ツールはAA以降を想定しない."""
    assert len(start) == 1 and len(end) == 1, "single-letter columns only"
    return [chr(c) for c in range(ord(start), ord(end) + 1)]


def _normalize_id(raw: str | None) -> str | None:
    """「9ｆ」のような全角英字を半角に正規化．"""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # 全角英小文字 → 半角
    trans = str.maketrans(
        "ａｂｃｄｅｆｇｈｉｊ",
        "abcdefghij",
    )
    return s.translate(trans)


def extract_all() -> tuple[list[dict], list[dict]]:
    wb = load_workbook(SRC_XLSM, data_only=True, keep_vba=False)
    sheet = wb["計算用シート"]

    idols: list[dict] = []
    groups_out: list[dict] = []

    for g in GROUPS:
        cols = _col_range(g["col_start"], g["col_end"])
        members_in_group: list[str] = []

        for col in cols:
            mid = _normalize_id(sheet[f"{col}{g['label_row']}"].value)
            if mid is None:
                continue
            name = None
            if g["name_row"]:
                raw_name = sheet[f"{col}{g['name_row']}"].value
                name = str(raw_name).strip() if raw_name else None

            big5 = {}
            for i, key in enumerate(BIG5_KEYS):
                row = g["big5_start_row"] + i
                val = sheet[f"{col}{row}"].value
                big5[key] = float(val) if val is not None else None

            # JSON保存用に丸める (過剰な桁はノイズ)
            big5 = {k: round(v, 4) if v is not None else None for k, v in big5.items()}

            idols.append({
                "id": mid,
                "group": g["id"],
                "name": name,
                "image": f"{mid}.jpg",
                "big5": big5,
                "description": "",  # 後続の OCR ステップで埋める
            })
            members_in_group.append(mid)

        groups_out.append({
            "id": g["id"],
            "name": g["name"],
            "members": members_in_group,
            "enabled_default": g["enabled_default"],
        })

    return idols, groups_out


def copy_images(idols: list[dict]) -> tuple[int, list[str]]:
    """output/ の写真を images/idols/ にコピー (小文字拡張子)．"""
    IMAGES_IDOLS_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing: list[str] = []

    for idol in idols:
        mid = idol["id"]
        # 現行は 1a.JPG / 2a.jpg などが混在
        candidates = [
            SRC_OUTPUT_DIR / f"{mid}.JPG",
            SRC_OUTPUT_DIR / f"{mid}.jpg",
            SRC_OUTPUT_DIR / f"{mid}.jpeg",
            SRC_OUTPUT_DIR / f"{mid}.png",
            SRC_OUTPUT_DIR / f"{mid}.PNG",
        ]
        src = next((p for p in candidates if p.exists()), None)
        if src is None:
            missing.append(mid)
            continue
        dest = IMAGES_IDOLS_DIR / f"{mid}.jpg"
        shutil.copyfile(src, dest)
        copied += 1
    return copied, missing


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] 計算用シート から Big5 値を抽出中 ...")
    idols, groups_out = extract_all()
    print(f"    -> アイドル {len(idols)} 名 / {len(groups_out)} グループ")

    (DATA_DIR / "idols.json").write_text(
        json.dumps(idols, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (DATA_DIR / "groups.json").write_text(
        json.dumps(groups_out, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"    -> data/idols.json, data/groups.json を書き出し")

    print(f"[2/3] 画像を output/ から images/idols/ へコピー中 ...")
    copied, missing = copy_images(idols)
    print(f"    -> コピー {copied} 件")
    if missing:
        print(f"    -> 画像未発見 ({len(missing)}件): {', '.join(missing)}")

    print(f"[3/3] 完了．次は tools/ocr_descriptions.py を実行してください．")


if __name__ == "__main__":
    main()
