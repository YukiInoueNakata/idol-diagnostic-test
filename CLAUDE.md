# アイドル診断テスト 2026 — Claude Code 用ガイド

## プロジェクトの概要

10問のTIPI質問に答えてビッグファイブ性格特性を測定し，似たアイドルを提示するWebアプリ．
会場で5台同時・6時間で200名規模の運用を想定．

## データフロー

```
受検者のブラウザ
  → index.html (基本情報・質問セット・グループ選択)
  → question.html (10問回答)
  → result.html (採点・マッチング・レーダーチャート・印刷)
       ├── 結果1行をGAS Webアプリへ POST
       └── 各PC既定プリンターで印刷
```

## 重要ファイル

- `data/idols.json` — 全アイドル (約71画像で75エントリ，複数グループにまたがるIDあり)
- `data/groups.json` — 11グループ．`enabled_default` が true のものだけ画面に出る
- `data/question-sets/*.json` — 質問セット．index.json が一覧
- `src/scoring.js` — computeBig5 / findNearest．純粋関数
- `src/api.js` — GAS エンドポイントへの POST ＋ localStorage キュー
- `src/config.json` — GAS URL と PC名をここで設定 (gitignoreしない: URLは公開前提)
- `gas/recorder.gs` — Apps Script．Spreadsheet に 1行 append

## 既知の注意点

1. **グループ間でIDが重複する** — 例えば `1a` は akb_kami7 にも josei_2019 にもあり得る．
   `idols.json` では `(group, id)` で一意．マッチングは必ず groupId でフィルタしてから．

2. **Big5 スケールは 1〜7** — 新しい質問セットを足す場合，output_scale を 1〜7 に合わせるか，
   idols.json 側を再計算する必要がある．

3. **OneDrive 上の日本語パスは PermissionError を起こしやすい** — 
   tools スクリプトは `test_source.xlsm` (ASCII名コピー) を優先して読む構造．

4. **印刷は window.print() 一発** — `print.css` の @page と `.no-print` に注意．
   GitHub Pages 配下で A4 固定．

5. **CORS / GAS** — fetch の Content-Type は text/plain で送る．JSON にすると preflight が走り，
   GAS 側で 405 になる場合がある．

## よく行う作業

- ローカル動作確認: `python -m http.server 8000` → `http://localhost:8000/src/index.html`
- 画像差し替え後の反映: ブラウザで Ctrl+Shift+R (no-cache)
- GAS URL の反映: `src/config.json` 編集してコミット
- 新しい質問セット追加: JSON を `data/question-sets/` に置いて，`index.json` にIDを追記

## Big5 採点ロジック (TIPI-J)

```
E = (q1 + (8 - q6)) / 2
A = ((8 - q2) + q7) / 2
C = (q3 + (8 - q8)) / 2
N = (q4 + (8 - q9)) / 2
O = (q5 + (8 - q10)) / 2
```

## マッチング

5次元ユークリッド二乗距離が最小の1名を返す (平方根はとらない — 最小判定には不要) ．

## notion_page_id

現時点では Notion DB 登録保留．必要時にここに記載．
