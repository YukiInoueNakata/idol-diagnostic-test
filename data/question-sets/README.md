# 質問セットの追加方法

このディレクトリに `*.json` を追加するだけで新しい質問セットが使えるようになります．

## 必須フィールド

| キー | 説明 |
|------|------|
| `id` | URLセーフな識別子．他と被らないこと． |
| `name` | 画面表示名 (例: 「TIPI日本語版」) |
| `description` | 受検者への説明 (任意) |
| `instructions` | 回答前に表示する教示文 |
| `scale.min` / `scale.max` | 回答値の範囲．通常は 1 と 7． |
| `scale.labels` | 各値のラベル (長さ = max - min + 1) |
| `items[]` | 質問項目配列 |
| `aggregation` | 項目→次元への集約方式．`mean_of_pair` のみ実装済． |
| `output_scale` | 最終的なBig5値の目盛 (アイドル側と合わせる必要あり) |
| `dimensions` | Big5の5次元定義．キーは `E, A, C, N, O` |

## items の各項目

```json
{
  "id": "q1",
  "text": "活発で，外向的だと思う",
  "dimension": "E",
  "reverse": false
}
```

`dimension` は `E/A/C/N/O` のいずれか．`reverse: true` は逆転項目 (スコアを `8 - v` に変換) ．

## 新しい集約方式を追加したい場合

現状は `mean_of_pair` (2項目平均) のみ実装．`sum_with_weights` 等を増やす場合は
`src/scoring.js` に実装を足してください．

## アイドル側のスケールとの整合性

idols.json の big5 値は 1〜7 スケールで保存されています．
新しい質問セットで `output_scale` が 1〜7 でない場合，
正規化するか idols.json 側を再計算する必要があります．
