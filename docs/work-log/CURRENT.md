---
project: アイドル診断テスト 2026
last_updated: 2026-04-24
status: デプロイ完了・UIテスト待ち
---

# 現在の作業状況

## 本番URL

- **Webアプリ (受検画面)**: https://yukiinouenakata.github.io/idol-diagnostic-test/
- **GitHub リポジトリ**: https://github.com/YukiInoueNakata/idol-diagnostic-test (public)
- **スプレッドシート (記録)**: https://drive.google.com/open?id=1vjpUFMrAjLr2FC25ce6HwjfWWrlOciQr7xT9_qPqcAk
- **Apps Script エディタ**: https://script.google.com/d/1Rje3l9cM1GVnVdsEt12uSzjQN1DA6yCgrz4Hx8J_pKkH9fPKVqDUlOD0/edit
- **GAS ウェブアプリ**: https://script.google.com/macros/s/AKfycbzUQwMeFYnhy8OBT7h7WZgs5exbpiXTwEoPZoMaWTyDIlOzB2kp5L7BmWKeOp4bs8u9/exec

## 疎通確認済み

- ✅ GitHub Pages ビルド成功．全アセット配信OK (data/*.json, images/idols/*.jpg)
- ✅ GAS エンドポイント GET (ヘルスチェック) 200
- ✅ GAS エンドポイント POST (スモークテスト) → スプレッドシート行2 に書き込み成功

## 未実施 (次のアクション — 先生にやっていただきたい)

- [ ] **ブラウザで通しテスト** — https://yukiinouenakata.github.io/idol-diagnostic-test/ を開き，
      基本情報入力 → 10問回答 → 結果画面 → 印刷プレビューまで実機確認
- [ ] 印刷用レーダーチャートが画面通りに出るか目視 (Chart.js は window.print() で落ちることがある)
- [ ] 複数の会場想定PCでの動作確認
- [ ] スプレッドシートに正しく集約されているか確認 (現時点で smoke-test の1行あり)

## 完了済み (2026-04-24 一日で一気通貫)

- [x] 旧 xlsm 解析 (81シート，VBA) → JSON構造設計
- [x] `extract_idols.py` で Big5数値・画像を抽出 (75エントリ / 71ユニーク画像)
- [x] Google Vision API で 75/75 エントリに name + description 投入
- [x] `data/question-sets/tipi-ja-10.json` 作成 (将来複数セット対応)
- [x] フロント3画面＋印刷CSS＋Chart.js
- [x] GAS `recorder.gs` 作成
- [x] Google Cloud プロジェクト `ynakata-idol-2026` 作成・Billing リンク・Vision API 有効化
- [x] clasp で Sheet + Apps Script 自動生成＋デプロイ
- [x] OAuth 認可 (setupSheet 手動実行)
- [x] GitHub public リポジトリ作成＋push＋Pages 有効化＋ビルド完了
- [x] GET/POST スモークテスト成功

## 運用変更時の手順

| やりたいこと | 方法 |
|---|---|
| 画像差し替え | `images/idols/` の jpg を上書き → `git push` |
| 説明文修正 | `data/idols.json` を直接編集 → `git push` |
| グループ追加 | `data/groups.json` に行追加．idols.json に対応メンバー追加 |
| 質問セット追加 | `data/question-sets/` に JSON 追加，`index.json` にID追記 |
| GAS コード修正 | `gas/recorder.gs` 編集 → `cd gas && clasp push && clasp redeploy AKfycbzUQw...` |
| 新規PC追加 | ブラウザで URL 開くだけ．事前設定不要 |

## 既知の注意点

1. **GAS ウェブアプリの初回 OAuth 認可** は所有者 (dj.y.nakata) が一度だけ手動実施済み．
   スクリプトを大きく変更してスコープが増えた場合は再認可が必要．
2. **リポジトリは public** — 写真は著作権物の可能性があるため，必要なら private 化を検討．
   (Private 化すると GitHub Pro 以外では Pages が公開不可になる．)
3. **OCR 句読点** — Vision API は「、」を返す．先生の規約 (「，」「．」) に一括置換したい場合は
   `data/idols.json` を一度 Python で正規化すれば良い．

## 参考ファイル

- `docs/operations-manual.md` — 会場当日の運用手順
- `tools/README.md` — 移行・セットアップの再実行方法
- `gas/README.md` — GAS 関連の手順
