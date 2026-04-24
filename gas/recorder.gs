/**
 * アイドル診断テスト — 結果記録用 Google Apps Script
 *
 * ## セットアップ手順
 *
 * 1. Google スプレッドシートを新規作成 (任意のタイトル，例: 「アイドル診断テスト 2026 記録」) ．
 * 2. 拡張機能 → Apps Script を開く．
 * 3. 既存の myFunction を消し，このファイルの内容をすべて貼り付けて保存．
 * 4. デプロイ → 新しいデプロイ → 種類: ウェブアプリ → アクセスできるユーザー: 「全員」→ デプロイ．
 * 5. 発行されるウェブアプリURL (https://script.google.com/macros/s/.../exec) を
 *    src/config.json の gasEndpoint に貼り付ける．
 * 6. 後述の setupSheet() を一度だけ手動実行すると，シートがヘッダー付きで初期化される．
 *
 * ## データ構造
 *
 * 1行につき1人の受検結果．列:
 *   timestamp, pcName, age, gender, questionSetId, groupId,
 *   big5_E, big5_A, big5_C, big5_N, big5_O,
 *   matchedId, matchedName, answersJson (生回答を JSON 文字列で格納)
 */

const SHEET_NAME = 'records';

const HEADERS = [
  'timestamp', 'pcName', 'age', 'gender', 'questionSetId', 'groupId',
  'big5_E', 'big5_A', 'big5_C', 'big5_N', 'big5_O',
  'matchedId', 'matchedName', 'answersJson',
];

/** 最初に1回だけ手動実行: ヘッダー付きシートを作成 */
function setupSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  sh.clear();
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
  sh.setFrozenRows(1);
}

/** POST 受信: {method:'POST'} で fetch してくる想定 */
function doPost(e) {
  try {
    const record = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) {
      sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
      sh.setFrozenRows(1);
    }
    const big5 = record.big5 || {};
    const row = [
      record.timestamp || new Date().toISOString(),
      record.pcName || '',
      record.age ?? '',
      record.gender || '',
      record.questionSetId || '',
      record.groupId || '',
      big5.E ?? '', big5.A ?? '', big5.C ?? '', big5.N ?? '', big5.O ?? '',
      record.matchedId || '',
      record.matchedName || '',
      JSON.stringify(record.answers || {}),
    ];
    sh.appendRow(row);
    return _json({ ok: true, row: sh.getLastRow() });
  } catch (err) {
    return _json({ ok: false, error: String(err) }, 500);
  }
}

/** 動作確認用 GET (ブラウザで URL を開くとヘルスチェック応答) */
function doGet(e) {
  return _json({ ok: true, service: 'idol-diagnostic-recorder', time: new Date().toISOString() });
}

function _json(obj, status) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
