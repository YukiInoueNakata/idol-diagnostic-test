# 移行・セットアップツール

`アイドル診断テスト2025/` の Excel ファイルから新システム (`2026/`) 用のデータを生成し，
Google Cloud 認証・GASデプロイまでを自動化するスクリプト群．

## ワンショットセットアップ (推奨)

```powershell
# 1. 外部サービス認証をまとめて実施 (ブラウザが開きます．1回だけ)
powershell -ExecutionPolicy Bypass -File tools\bootstrap.ps1

# 2. データ抽出 (完了済み．再実行したい場合のみ)
python tools\extract_idols.py

# 3. OCR で説明文を抽出 (Vision API 呼び出し)
python tools\ocr_descriptions.py

# 4. Sheet + GAS を自動構築してウェブアプリURLを src/config.json に書き込み
powershell -ExecutionPolicy Bypass -File tools\setup_gas.ps1
```

## 各スクリプトの役割

| スクリプト | 目的 |
|-----------|------|
| `bootstrap.ps1`        | gcloud auth + Vision API 有効化 + clasp login |
| `extract_idols.py`     | xlsm → data/idols.json, data/groups.json, images/idols/*.jpg |
| `ocr_descriptions.py`  | images/idols/*.jpg → Vision API → idols.json に description/name マージ |
| `setup_gas.ps1`        | Sheet 作成 + Apps Script push + ウェブアプリ公開 + config.json 更新 |

依存:
- Python (openpyxl, google-cloud-vision)
- Node.js (@google/clasp は bootstrap.ps1 実行前に `npm install -g @google/clasp` 済みの想定)
- gcloud CLI (`winget install Google.CloudSDK` で導入済み)

---

## Google Vision API のセットアップ (ocr_descriptions.py を動かす前に1回だけ)

### 方法A: gcloud CLI を使う (推奨．通常の論文執筆PCで使い回せる)

1. [Cloud SDK インストーラ](https://cloud.google.com/sdk/docs/install) から `gcloud` を入れる  
   Windows インストーラ (MSI) が楽．インストール後は PowerShell/terminal を再起動．
2. `gcloud auth application-default login` を実行．ブラウザが開き Google アカウントを選択．
3. Google Cloud Console で プロジェクトを1つ作る (既存プロジェクトがあるならそれでOK) ．
4. そのプロジェクトで Vision API を有効化:  
   <https://console.cloud.google.com/apis/library/vision.googleapis.com>
5. `gcloud config set project YOUR_PROJECT_ID`

これで `python tools/ocr_descriptions.py` が動くようになります．

### 方法B: サービスアカウントキーを使う

1. Cloud Console → IAMと管理 → サービスアカウント → 新規作成
2. 役割: Cloud Vision API ユーザー (roles/cloudvision.admin でも可)
3. 鍵を追加 → JSON をダウンロード
4. 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` にその JSON のフルパスをセット  
   例: `setx GOOGLE_APPLICATION_CREDENTIALS "C:\Users\YIN\secrets\vision-sa.json"`
   → PowerShell を再起動
5. Vision API を有効化 (方法Aの手順4と同じ)

### 料金について

- 2026年現在，Vision API は毎月 **1000ユニット無料**
- 本プロジェクトは **71画像のみ** なので完全無料枠内で収まります
- 繰り返し実行しないよう `.ocr_cache.json` に結果をキャッシュしています

### うまく動かないとき

- `google.auth.exceptions.DefaultCredentialsError` → 認証されていない．方法A/Bを再確認
- `PermissionDenied: 403 Cloud Vision API has not been used...` → プロジェクトで API 未有効化
- `Quota exceeded` → 1000/月を超えた場合．翌月まで待つか有料化
