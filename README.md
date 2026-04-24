# アイドル診断テスト 2026

10問の質問に答えると，ビッグファイブ性格特性をもとに似ているアイドルを診断する Web アプリ．
会場で複数台のPCから同時受検し，結果は各PCのプリンターで出力，データは Google スプレッドシートに集約する．

## 前バージョン (2025) からの主な変更

- VBA/Excelマクロ → 静的 Web アプリ (HTML + JS)
- 76個あった個別シート → 1つの結果テンプレートに統一
- 700行の If/ElseIf 分岐 → JSON 辞書で表現
- ローカル Excel に蓄積 → Google スプレッドシートに自動集約
- 質問セットは切り替え可能 (JSON を追加するだけ)

## システム構成

```
[受検PC ブラウザ]
  ├── HTML/JS/画像/JSON を取得 ← GitHub Pages
  │   採点・マッチング・印刷はブラウザ内で完結
  └── 結果1行をPOST → Google Apps Script Web App
                       └─ Google スプレッドシートに append
```

## ディレクトリ

| パス | 役割 |
|------|------|
| `data/idols.json`          | 全アイドルのBig5値と説明文 |
| `data/groups.json`         | 11グループ定義 |
| `data/question-sets/*.json`| 質問セット (複数可) |
| `images/idols/`            | 1a.jpg 〜 11i.jpg |
| `src/`                     | 静的フロントエンド (GitHub Pages 配信対象) |
| `gas/recorder.gs`          | Google Apps Script (スプレッドシート記録) |
| `tools/*.py`               | データ移行スクリプト (一度きり) |
| `docs/`                    | 運用マニュアル |

## セットアップ (デプロイまで)

### 1. データ抽出 (完了済)

```bash
cd tools
python extract_idols.py          # idols.json, groups.json, images/
python ocr_descriptions.py       # OCRでdescriptionを埋める (要Vision API認証)
```

→ 詳細は `tools/README.md` 参照．

### 2. Google Apps Script 設定

`gas/README.md` の手順を実施．ウェブアプリURLをコピーして `src/config.json` に貼り付け．

### 3. GitHub Pages 公開

```bash
git init
git add .
git commit -m "initial"
git remote add origin git@github.com:YukiInoueNakata/idol-diagnostic-test.git
git push -u origin main
```

リポジトリ設定 → Pages → Source を main / docs 外に指定．
`src/` をルートで配信したいので，以下いずれか:

- A. `src/` の中身をリポジトリルートへ移す (`data/` と `images/` は `../data`, `../images` 参照を相対で調整)
- B. GitHub Actions で src/ を pages ブランチに publish

**推奨はA**．シンプル．詳細は `docs/deployment.md` 参照．

### 4. 受検PCでのアクセス

各PCのブラウザで `https://YukiInoueNakata.github.io/idol-diagnostic-test/` にアクセス．
事前に各PCのブラウザ印刷設定で既定プリンターを確認しておく．

## 運用

- 画像差し替え: `images/idols/` の jpg を上書き → コミット → push．
- 説明文修正: `data/idols.json` の description を書き換え → コミット → push．
- 新グループ追加: `data/groups.json` に行を足し，該当メンバーを `data/idols.json` に追加．
- 新質問セット: `data/question-sets/` に JSON を追加し，`data/question-sets/index.json` に ID を追記．

## ライセンス

研究・教育目的の内部利用．

## 作者

Yuki Inoue Nakata / 立命館大学 総合心理学部  
Codebase: 中高瀬・土元・小塩 TIPI-J ほか先行研究に依拠．
