// 採点・マッチングの純粋関数群．フロントでもテストでも使える．

/**
 * 質問セットの items[] と回答値 {q1: 5, q2: 3, ...} から
 * Big Five 5次元スコアを計算して返す．
 *
 * @param {object} questionSet - tipi-ja-10.json 相当のオブジェクト
 * @param {object} answers - {itemId: numericValue}
 * @returns {{E:number,A:number,C:number,N:number,O:number}}
 */
export function computeBig5(questionSet, answers) {
  const { items, scale, aggregation } = questionSet;
  const max = scale.max; // 通常 7

  // 各次元ごとに当該項目の値を集める (逆転項目は max+1-v に変換)
  const buckets = { E: [], A: [], C: [], N: [], O: [] };
  for (const item of items) {
    const raw = answers[item.id];
    if (typeof raw !== "number" || Number.isNaN(raw)) {
      throw new Error(`missing answer for ${item.id}`);
    }
    const v = item.reverse ? max + 1 - raw : raw;
    buckets[item.dimension].push(v);
  }

  const result = {};
  for (const dim of ["E", "A", "C", "N", "O"]) {
    const vs = buckets[dim];
    if (vs.length === 0) {
      throw new Error(`no items for dimension ${dim}`);
    }
    if (aggregation === "mean_of_pair" || aggregation === "mean") {
      result[dim] = vs.reduce((a, b) => a + b, 0) / vs.length;
    } else {
      throw new Error(`unsupported aggregation: ${aggregation}`);
    }
  }
  return result;
}

/**
 * 指定グループ内のメンバーから，ユーザーのBig5と最も近い1名を返す．
 * 距離は5次元のユークリッド二乗距離 (平方根不要 — 最近傍判定には十分) ．
 *
 * @param {{E,A,C,N,O}} userBig5
 * @param {Array<{id,group,big5}>} idols - idols.json 全体
 * @param {string} groupId - 対象グループID
 * @returns {{idol: object, distance: number}}
 */
export function findNearest(userBig5, idols, groupId) {
  const candidates = idols.filter((i) => i.group === groupId);
  if (candidates.length === 0) {
    throw new Error(`no idols in group: ${groupId}`);
  }
  let best = null;
  let bestDist = Infinity;
  for (const c of candidates) {
    let d = 0;
    for (const k of ["E", "A", "C", "N", "O"]) {
      const diff = userBig5[k] - c.big5[k];
      d += diff * diff;
    }
    if (d < bestDist) {
      bestDist = d;
      best = c;
    }
  }
  return { idol: best, distance: bestDist };
}
