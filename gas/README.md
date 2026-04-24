# Google Apps Script 設定手順

## 1. 新しい Google スプレッドシートを作成

- [sheets.new](https://sheets.new) を開く
- タイトルを「アイドル診断テスト 2026 記録」等に設定

## 2. Apps Script を開く

- 拡張機能 → Apps Script

## 3. コードを貼り付け

- デフォルトの `myFunction` を削除
- `recorder.gs` の内容をすべてコピー＆ペースト
- 💾 保存 (プロジェクト名は任意．例: "idol-recorder")

## 4. 初期化 (1回だけ)

- エディタ上部の関数選択で `setupSheet` を選び，▶ 実行
- 初回は権限付与ダイアログが出るので承認
- スプレッドシートに `records` シートが作成されヘッダー行が入ればOK

## 5. ウェブアプリとしてデプロイ

- 右上の「デプロイ」→「新しいデプロイ」
- 種類: ウェブアプリ
- 説明: "idol diagnostic recorder v1"
- 実行するユーザー: 自分
- アクセスできるユーザー: 全員 ← 重要
- デプロイ

## 6. URLをコピー

- 表示される「ウェブアプリURL」 (`https://script.google.com/macros/s/AKfy.../exec`) をコピー
- `src/config.json` の `gasEndpoint` に貼り付け
- コミット & push

## 動作確認

```bash
# ヘッダー行のデバッグ
curl https://script.google.com/macros/s/XXX/exec

# テストPOST
curl -X POST -H "Content-Type: text/plain" \
  -d '{"timestamp":"2026-04-24T10:00:00Z","pcName":"test","age":25,"gender":"female","questionSetId":"tipi-ja-10","groupId":"niziu","big5":{"E":5,"A":4,"C":5,"N":3,"O":5},"answers":{"q1":5,"q2":3},"matchedId":"6a","matchedName":"MAKO"}' \
  https://script.google.com/macros/s/XXX/exec
```

Spreadsheet に 1行追加されればOK．

## コードを修正した場合

- Apps Script 側でコードを編集したら，「デプロイ → デプロイを管理 → 編集 → バージョン: 新バージョン → デプロイ」
- URLは同じまま使える (バージョン番号だけ更新される)
