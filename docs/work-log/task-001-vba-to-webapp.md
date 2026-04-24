---
task: VBA/Excel から GitHub Pages + GAS の Web アプリへ刷新
started: 2026-04-24
status: in_progress
---

# タスク 1: アイドル診断テスト VBA版 → Web版 移行

## 目的

- 現行の xlsm (VBA 700行の If/ElseIf 連鎖，76個の個別シート，15MB) を，JSONベースのWebアプリに刷新
- 複数PC同時受検 (5台想定) ・結果をGoogleスプレッドシートに自動集約
- 画像・説明文・質問セットの追加編集を容易にする

## 方針

| 項目 | 決定事項 |
|------|--------|
| フロント | 素のHTML/JS (ESM) + Chart.js．フレームワーク不使用． |
| データ | `data/*.json` (idols/groups/question-sets) |
| 画像 | `images/idols/*.jpg` (既存の output/ を継承) |
| 採点 | クライアント側で完結 (TIPI → ユークリッド二乗距離で最近傍1名) |
| 印刷 | `window.print()` + 印刷用CSS．各PC既定プリンター． |
| データ記録 | Google Apps Script Web App → Sheets append |
| ホスティング | GitHub Pages (無料・CDN) |
| 質問セット | 複数対応 (JSON追加で切替．初期はTIPI-J10問) |

## 経過記録

### 2026-04-24

- **午前**: xlsm の解析完了 (81シート，11グループ，76メンバー分の Big5 プロファイル) ．
- **午前**: 2026/ 配下にディレクトリ構造・スクリプト群作成．extract_idols.py で data/ と images/ を生成．
- **午後**: フロントエンド実装．scoring.js を Node で検証．
- **午後**: Google Cloud プロジェクト作成．Billing リンク．Vision API 有効化．
- **午後**: ocr_descriptions.py で全71画像をOCR．75エントリ全てに name + description 投入．
  - 伝播遅延で3回リトライが必要だったがキャッシュにより無駄なし
- **次回**: clasp再ログイン待ち → setup_gas.ps1 → GitHub Pages 公開

## 技術メモ (将来の自分への申し送り)

- PowerShell 5.1 は native command の stderr を NativeCommandError に変換するので
  gcloud 呼び出しは `cmd.exe /c "...gcloud... 2>nul"` 経由にすると無難．
- .ps1 ファイルは UTF-8 BOM 付きで保存．Write tool のデフォルトは BOM なしなので明示的に付加が必要．
- 複数グループ間で同じ member_id (例: 1a, 1c, 3b, 3c) が共有される．idols.json では (group, id) で一意．
- OneDrive 上の日本語パスは openpyxl/zipfile が PermissionError を出しがち．
  ASCIIコピー (test_source.xlsm) をフォールバックに用意．

## 未解決の事項

- GitHub Pages のルート配置 (src/ 直下公開 vs ルートに寄せる)
- 印刷時 Chart.js レーダーの実機確認
- OCR 句読点の「、」→「，」置換ポリシー (研究者規約準拠 vs 原文尊重)
