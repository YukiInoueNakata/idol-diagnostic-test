---
project: アイドル診断テスト 2026
last_updated: 2026-04-24
status: 開発中 (デプロイ前段階)
---

# 現在の作業状況

## 進捗サマリ

`2025/` 版 (Excel VBA) を完全に Web アプリ化する作業．データ抽出・フロント実装・採点ロジックまで完了．
残るは **GitHub リポジトリ作成 → Pages 公開 → GAS デプロイ完了 → 会場動作確認** ．

## 完了済み (2026-04-24)

- [x] 現行xlsmの解析 (81シート，VBAコード抽出，診断ロジック把握)
- [x] 新システム設計 (Webアプリ + GAS + GitHub Pages 構成確定)
- [x] `2026/` プロジェクト構造作成
- [x] `tools/extract_idols.py`: xlsm → idols.json (75件) / groups.json (11件) / images/idols/ (71枚)
- [x] `tools/ocr_descriptions.py`: Google Vision API で全説明文＋名前を抽出，idols.json に統合
- [x] `data/question-sets/tipi-ja-10.json`: TIPI日本語10問 (将来複数セット対応の構造)
- [x] フロントエンド (index/question/result .html + CSS + JS) 実装
- [x] `scoring.js` の動作検証 (Node.js で TIPI採点＋最近傍マッチ確認)
- [x] `gas/recorder.gs` 実装
- [x] `tools/bootstrap.ps1` で認証セットアップ: gcloud CLI + ADC + Vision API有効化
- [x] Google Cloud プロジェクト `ynakata-idol-2026` 作成＋課金アカウントリンク
- [x] 運用マニュアル (docs/operations-manual.md)

## 保留中 (blocking: ユーザー作業)

- [ ] **clasp 再ログイン** — トークン `invalid_grant` 失効．以下を実施してください:
  ```powershell
  clasp logout
  clasp login
  ```

## 次にやるべきこと (clasp再ログイン後，私が実施可)

- [ ] `tools/setup_gas.ps1` 実行 → スプレッドシート新規作成 + GAS push + WebアプリURLを `src/config.json` へ反映
- [ ] GitHub リポジトリ `YukiInoueNakata/idol-diagnostic-test` 作成 (GitHub API or gh CLI)
- [ ] 初回 commit + push
- [ ] GitHub Pages 有効化 (`main` ブランチ / `src/` をルートに配置する場合は構造微調整が必要)
- [ ] ブラウザで本番URL動作確認 (採点・印刷・Sheets記録までの一気通貫)
- [ ] 2025版からの差分を README で明示

## 既知の懸念

1. **GitHub Pages 公開時の相対パス** — 現状 `src/index.html` から `../data/` を参照．
   Pages のルートを `/src/` にするか，全体のルートに `index.html` を置き直すか要判断．
2. **印刷時のレーダーチャート** — Chart.js の canvas は `window.print()` で欠落することがある．
   A4レイアウトで要実機確認．
3. **OCRの句読点** — Vision API は句点を「、」で認識．先生の規約 (「，」「．」) に合わせるなら一括置換の検討余地．
4. **同時5台時の sessionStorage 衝突** — 各PCの独立ブラウザなので問題なしのはずだが念のため本番確認．

## 参考

- 前バージョン保存先: `../アイドル診断テスト2025/` (触らない)
- Google Cloud プロジェクト: `ynakata-idol-2026`
- 課金アカウント: `billingAccounts/01CEB0-6CB0AC-A0BC15`
- Vision API: 有効 (無料枠1000/月内で完結)
- 使用アカウント: dj.y.nakata@gmail.com
