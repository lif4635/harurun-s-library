#!/usr/bin/env python3
"""Build the exhaustive, source-derived API reference for ``library_codex``.

The library deliberately avoids runtime type machinery and annotations in hot
code.  This tool therefore reads the source AST instead of importing modules.
It documents every public top-level function/class, every public class method,
useful Python protocol methods, aliases, and public constants.
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs"
API_ROOT = DOC_ROOT / "api"
SKIP_DIRS = {"verify", "tools", "docs", "__pycache__"}

CATEGORY_DESCRIPTION = {
    "algorithm": "汎用アルゴリズム・列・順列",
    "convolution": "畳み込み・多項式・形式的冪級数",
    "data_structure": "データ構造",
    "game": "組合せゲーム",
    "graph": "グラフアルゴリズム",
    "heuristic": "ヒューリスティック探索",
    "math": "数学・線形代数・数論",
    "optimization": "最適化・DP高速化",
    "prime": "素数・素因数分解",
    "random": "乱数・ランダムグラフ",
    "string": "文字列アルゴリズム",
    "tree": "木アルゴリズム・動的木",
}

# Modules added after the overview table in README was written.  The other
# overviews and complexity notes are read directly from that table.
MODULE_OVERRIDES = {
    "algorithm/Base64Integers.py": ("符号付き整数列のBase64可変長符号化・復号", "入出力サイズに線形"),
    "algorithm/MiscAlgorithms.py": ("商列挙・区間列挙などの汎用小アルゴリズム", "各標準計算量"),
    "algorithm/PermutationGroup.py": ("置換の合成・逆元と置換群の生成元簡約", "主に O(N^2K)"),
    "algorithm/SequenceOrdering.py": ("点更新される列の辞書順比較・版圧縮", "更新・比較 O(log N)"),
    "convolution/AdvancedSeries.py": ("指数合成・等比点評価など高度なFPS変換", "主に高速多項式演算依存"),
    "convolution/FPSWrappers.py": ("有理FPSと双対FPSの演算ラッパー", "各FPS演算依存"),
    "convolution/IncreasingSequences.py": ("単調増加列に関する母関数計算", "高速多項式演算依存"),
    "convolution/MultivariateFPS.py": ("多変数形式的冪級数の逆元・指数・対数・冪", "O(N log N) 系"),
    "convolution/OnlineFormalPowerSeries.py": ("係数を逐次確定するオンラインFPS演算", "償却 O(N log N) 系"),
    "convolution/PRecursive.py": ("P再帰列の推定・列挙・巨大添字項", "多項式行列積依存"),
    "convolution/PolynomialFactorization.py": ("有限体上の多項式GCD・因数分解", "高速Euclid / Cantor--Zassenhaus"),
    "convolution/StirlingMatrix.py": ("Stirling変換を表す行列作用", "高速多項式演算依存"),
    "data_structure/AdvancedOrdered.py": ("高度な順序集合・区間集合・永続順序構造", "各操作 O(log N) 系"),
    "data_structure/AdvancedRangeStructures.py": ("Top-K区間集約・KD木・sortable sequence", "各構造の計算量"),
    "data_structure/LinearOptimization.py": ("直線集合とrange linear add/range min", "各操作 O(log^2 N) 系"),
    "data_structure/RangeLIS.py": ("Seaweed monoidによる静的区間LIS", "構築 O(N^2 log N) 系、query O(log N)"),
    "game/PartizanGame.py": ("partizan gameのSurreal/NumStar値と反復solver", "状態・遷移数依存"),
    "graph/GeneralWeightedMatching.py": ("一般グラフの最大重みmatching", "O(V^3)"),
    "math/ArbitraryBinomial.py": ("任意合成数法・巨大素数法の二項係数", "素因数分解・sqrt block依存"),
    "math/BinomialQueries.py": ("二項係数prefix和と巨大添字Stirlingの一括query", "Mo法 / 補間依存"),
    "math/Elementary.py": ("gcd・lcm・整数根など初等数学関数", "各標準計算量"),
    "math/FloorPolynomialSum.py": ("floorを含む多項式和", "Euclid pathと次数依存"),
    "math/FractionSearch.py": ("Stern--Brocot/Farey型の有理数探索", "探索深さ依存"),
    "math/MultiplicativeFunctions.py": ("乗法的関数・Dirichlet積・Min_25型prefix和", "商集合・素数列挙依存"),
    "math/Nimber.py": ("Conway nimber積・逆元・基底変換", "固定語長 O(1)"),
    "math/RationalFormalPowerSeries.py": ("有理形式的冪級数の係数・prefix和", "Bostan--Mori依存"),
    "math/Strassen.py": ("任意長方形行列の反復Strassen積", "O(N^log2(7))"),
    "tree/DynamicRerooting.py": ("rake-compress top treeによる動的rerooting", "各更新・query償却 O(log N)"),
    "tree/IncrementalForest.py": ("辺追加だけのforest・LCA・path集約", "追加・query O(log N) 系"),
}

# Methods that are private by spelling but form part of normal Python usage.
PROTOCOL_METHODS = {
    "__bool__": "bool(obj) と真偽値文脈",
    "__call__": "obj(...) として呼び出す",
    "__contains__": "value in obj",
    "__enter__": "with 文へ入る",
    "__exit__": "with 文から出る",
    "__getitem__": "obj[key] で取得する",
    "__iter__": "iter(obj)・for 文",
    "__len__": "len(obj)",
    "__next__": "next(obj)",
    "__setitem__": "obj[key] = value で更新する",
    "__delitem__": "del obj[key] で削除する",
    "__reversed__": "reversed(obj)",
    "__add__": "obj + other",
    "__radd__": "other + obj",
    "__iadd__": "obj += other",
    "__sub__": "obj - other",
    "__rsub__": "other - obj",
    "__isub__": "obj -= other",
    "__mul__": "obj * other",
    "__rmul__": "other * obj",
    "__imul__": "obj *= other",
    "__truediv__": "obj / other",
    "__floordiv__": "obj // other",
    "__mod__": "obj % other",
    "__pow__": "obj ** exponent",
    "__neg__": "-obj",
    "__pos__": "+obj",
    "__invert__": "~obj",
    "__and__": "obj & other",
    "__or__": "obj | other",
    "__xor__": "obj ^ other",
    "__lshift__": "obj << amount",
    "__rshift__": "obj >> amount",
    "__eq__": "obj == other",
    "__ne__": "obj != other",
    "__lt__": "obj < other",
    "__le__": "obj <= other",
    "__gt__": "obj > other",
    "__ge__": "obj >= other",
    "__int__": "int(obj)",
    "__index__": "整数indexとして使う",
    "__hash__": "hash(obj)",
}

ARGUMENT_DESCRIPTION = {
    "a": "第1入力（意味は関数の説明を参照）",
    "b": "第2入力（意味は関数の説明を参照）",
    "c": "定数・係数・第3入力",
    "x": "値・座標・問い合わせ対象",
    "y": "値・座標・問い合わせ対象",
    "z": "値・座標・問い合わせ対象",
    "u": "頂点番号（0-indexed）",
    "v": "頂点番号（0-indexed）",
    "s": "始点または入力列",
    "t": "終点または対象値",
    "n": "要素数・頂点数・次数",
    "m": "要素数・辺数・次数",
    "k": "個数・順位・移動量（APIの文脈に従う）",
    "q": "query数・値",
    "p": "位置・素数法・確率（APIの文脈に従う）",
    "i": "0-indexedの位置",
    "j": "0-indexedの位置",
    "index": "0-indexedの位置",
    "indices": "0-indexed位置の列",
    "position": "0-indexedの位置",
    "left": "半開区間の左端（含む）",
    "right": "半開区間の右端（含まない）",
    "l": "半開区間の左端（含む）",
    "r": "半開区間の右端（含まない）",
    "top": "矩形の上端（含む）",
    "bottom": "矩形の下端（含まない）",
    "row": "0-indexedの行番号",
    "column": "0-indexedの列番号",
    "height": "高さ・行数",
    "width": "幅・列数",
    "size": "要素数・universe size",
    "length": "長さ",
    "count": "個数",
    "limit": "上限。NoneならAPI既定の上限",
    "lower": "下限（包含関係はAPIの説明を参照）",
    "upper": "上限（包含関係はAPIの説明を参照）",
    "start": "始点・開始位置",
    "goal": "終点。Noneなら全体を処理",
    "source": "始点",
    "sink": "終点",
    "root": "根の頂点番号・原始根",
    "vertex": "頂点番号（0-indexed）",
    "node": "頂点・内部node番号",
    "edge": "辺または隣接list",
    "edges": "辺のiterable/list",
    "graph": "隣接listまたはグラフobject",
    "tree": "木の隣接list",
    "values": "初期値のiterable。整数ならsizeを表す場合がある",
    "value": "追加・設定・問い合わせる値",
    "data": "入力data",
    "sequence": "入力列",
    "array": "入力配列",
    "polynomial": "昇冪係数列 `[a0, a1, ...]`",
    "series": "昇冪の形式的冪級数係数列",
    "degree": "必要な係数数・次数上限",
    "coefficients": "係数列",
    "initial": "初期値または初項列",
    "points": "評価点の列",
    "weights": "重みの列",
    "matrix": "行をlistで持つ行列",
    "vector": "vector・1次元配列",
    "mod": "法。Noneの場合は整数上の演算",
    "modulus": "法",
    "op": "結合的な二項演算 `op(left, right)`",
    "operation": "演算callback",
    "identity": "演算 `op` の単位元",
    "e": "単位元、または単位元を返すcallable",
    "mapping": "作用を値へ適用するcallback",
    "composition": "新旧の作用を合成するcallback",
    "action": "遅延作用・更新作用",
    "predicate": "判定callback",
    "condition": "判定callback",
    "func": "callback関数",
    "function": "callback関数",
    "callback": "各要素・状態で呼ぶ関数",
    "key": "比較・格納に使うkey",
    "default": "省略時に使う値",
    "seed": "乱数seed。Noneなら実装既定値",
    "trials": "乱択試行回数",
    "minimize": "Trueなら最小値、Falseなら最大値を扱う",
    "directed": "Trueなら有向グラフとして扱う",
    "inclusive": "端点を含めるかどうか",
    "reverse": "逆向き・降順を使うかどうか",
    "inplace": "Trueなら入力を破壊的に更新する",
    "text": "検索対象の文字列・列",
    "pattern": "検索patternの文字列・列",
    "alphabet": "文字集合またはalphabet size",
    "wildcard": "wildcardとして扱う記号",
    "word": "登録・検索する文字列・列",
    "words": "文字列・列のiterable",
    "version": "参照するversion番号",
    "time": "operation時刻",
    "cost": "辺・選択の費用",
    "capacity": "容量",
    "flow_limit": "流量上限。Noneなら可能な最大量",
    "ratio": "等比数列の公比",
    "scale": "scale係数",
    "exponent": "非負の指数",
    "power": "冪指数",
    "first": "第1入力・左側の値",
    "second": "第2入力・右側の値",
    "third": "第3入力",
    "other": "同じ型のもう一方のobject・値",
    "number": "整数",
    "target": "探索・判定・更新の対象値",
    "amount": "加算量・移動量",
    "variable": "Boolean変数番号（0-indexed）",
    "point": "評価点・座標",
    "base": "底・基準となる値または列",
    "base2": "第2のhash base",
    "weight": "重み",
    "profit": "利益（負なら費用）",
    "weighted": "重み付き辺を生成・保持するか",
    "weight_min": "生成する辺重みの下限",
    "weight_max": "生成する辺重みの上限",
    "prime": "素数法",
    "numerator": "有理式の分子多項式",
    "denominator": "有理式の分母多項式",
    "dividend": "多項式の被除数",
    "divisor": "多項式の除数",
    "state": "rollback状態番号・状態object",
    "symbol": "文字・alphabet上の記号",
    "delta": "加算差分",
    "parent": "親頂点・親配列",
    "chosen": "選ぶ個数",
    "steps": "移動step数",
    "multiplier": "乗数または乗算する多項式",
    "query_left": "問い合わせ半開区間の左端",
    "query_right": "問い合わせ半開区間の右端",
    "prefix": "prefix列・prefix長",
    "palindrome": "回文node・回文列",
    "sort_positions": "位置listを整列するか",
    "child": "子cluster・子頂点",
    "restore": "復元情報も計算するか",
    "zero": "加法単位元・0相当の値",
    "addend": "加える値",
    "shift": "平行移動量・bit shift量",
    "outer": "外側の多項式/FPS `f`",
    "inner": "内側の多項式/FPS `g`",
    "xor": "全要素へ作用させるXOR値",
    "include_empty": "空集合・空列も結果に含めるか",
    "include_zero": "0も列挙結果に含めるか",
    "vertex_count": "頂点数",
    "operator": "行列作用 `v -> A v` またはoperator object",
    "permutation": "0-indexed置換 `p[i]` の列",
    "permutations": "生成元となる置換のlist",
    "order": "順序・次数・並べ方",
    "slope": "直線の傾き",
    "intercept": "直線の切片",
    "right_size": "二部グラフ右側の頂点数",
    "left_size": "二部グラフ左側の頂点数",
    "coordinate": "多次元座標",
    "transitions": "遷移・隣接移動のiterable",
    "distance": "距離・距離配列",
    "multiply": "積を計算するcallback",
    "residues": "各法に対する剰余の列",
    "moduli": "法の列",
    "prime_power": "素数冪における値を返すcallback",
    "arbitrary": "任意列側の入力",
    "convex": "凸列側の入力",
    "concave": "凹列側の入力",
    "infinity": "到達不能・無限大を表す値",
    "selected": "現在選択中の要素集合・bool列",
    "costs": "費用の列",
    "info": "clusterへ付随させる情報",
    "code": "符号列・Prüfer列",
    "encoded": "符号化済みbytes/string",
    "signed": "符号付き整数として符号化・復号するか",
    "strict": "狭義（等値を許さない）として扱うか",
    "mask": "bit mask",
    "intervals": "区間 `(left, right)` のiterable",
    "iterations": "反復回数",
    "bits": "使用bit数",
    "bit_count": "使用bit数",
    "digit_bits": "radix 1桁に使うbit数",
    "keys": "整列keyの列またはkey callback",
    "fractions": "`(numerator, denominator)` の列",
    "polynomials": "多項式係数列のiterable",
    "recurrence": "P再帰式・線形漸化式の係数",
    "terms": "返す項数",
    "scalar": "scalar倍する値",
    "derivative": "微分係数を計算するcallback",
    "rectangles": "矩形 `(left, bottom, right, top)` のiterable",
    "game": "局面遷移を提供するgame object",
    "states": "初期局面・局面集合",
    "options": "局面から遷移先を列挙するcallback",
    "terminals": "Steiner木で接続するterminal頂点列",
    "queries": "一括処理するqueryの列",
    "clause": "SAT節を表すliteral列",
    "assumptions": "一時的に真と仮定するliteral列",
    "threshold": "naive法等へ切り替える閾値",
    "rows": "行数",
    "columns": "列数",
    "compare": "2候補を比較するcallback",
    "heights": "各列の高さ",
    "truthy": "通行可能/1と扱う値または判定callback",
    "variables": "変数数",
    "arguments": "位置引数のtuple",
    "rectangle1": "第1矩形 `(top, left, bottom, right)`",
    "rectangle2": "第2矩形 `(top, left, bottom, right)`",
    "sequences": "入力列のiterable",
    "subsequence": "部分列候補",
    "suffix_array": "対応するsuffix array",
    "vertices": "頂点番号のiterable",
}

EXACT_PURPOSE = {
    "access": "指定位置の元の値を取得する。",
    "add": "値・辺・要素を追加する。詳細はclass/moduleの説明に従う。",
    "all_prod": "全区間の集約値を返す。",
    "apply": "指定した作用を適用する。",
    "bisect_left": "条件を満たす最初の位置を二分探索する。",
    "bisect_right": "条件を満たす境界の直後を二分探索する。",
    "build": "内部構造を構築する。",
    "clear": "保持している要素・状態を空にする。",
    "connected": "2頂点が同じ連結成分か判定する。",
    "contains": "指定値を保持しているか判定する。",
    "count": "条件に合う要素数を返す。",
    "cut": "指定辺をforestから切断する。",
    "discard": "要素があれば削除する。",
    "distance": "距離を求める。",
    "empty": "空かどうかを判定する。",
    "enumerate": "対象を列挙する。",
    "erase": "指定要素を削除する。",
    "evaluate": "指定点で値を評価する。",
    "find": "代表元・位置・対象要素を探す。",
    "flow": "指定した始点から終点へflowを流す。",
    "fold": "指定範囲・pathを演算で集約する。",
    "get": "指定位置・辺・状態の値を取得する。",
    "insert": "指定位置へ要素を挿入する。",
    "inverse": "逆元・逆変換を求める。",
    "kth": "0-indexedでk番目の要素を取得する。",
    "lca": "2頂点の最小共通祖先を求める。",
    "link": "異なる木の2頂点を辺で接続する。",
    "lower_bound": "指定値以上となる最初の位置を返す。",
    "max_right": "左端からpredicateを満たす最大の右端を探す。",
    "merge": "2要素・2成分・2構造を併合する。",
    "min_left": "右端まででpredicateを満たす最小の左端を探す。",
    "pop": "要素を1つ取り除いて返す。",
    "prod": "半開区間またはpathの集約値を返す。",
    "push": "要素を追加する。",
    "query": "指定した対象への問い合わせ結果を返す。",
    "range_freq": "半開区間内で値域条件に合う要素数を返す。",
    "rank": "指定範囲内の出現数または線形代数上のrankを返す。",
    "remove": "指定要素を削除する。",
    "restore": "計算結果から経路・列・元データを復元する。",
    "rollback": "指定snapshotまで状態を巻き戻す。",
    "set": "指定位置・状態を値で置き換える。",
    "size": "要素数または連結成分sizeを返す。",
    "snapshot": "現在のrollback位置を保存して返す。",
    "solve": "設定済みの問題を解き、答えを返す。",
    "split": "指定位置・条件で構造を2つに分割する。",
    "sum": "半開区間・集合の和を返す。",
    "top": "次に取り出される要素を削除せず返す。",
    "unite": "2要素が属する連結成分を併合する。",
    "update": "指定位置・辺・状態を更新する。",
}

NOUN = {
    "all": "全体", "and": "AND", "any": "任意", "array": "配列",
    "biconnected": "二重頂点連結", "binary": "二分", "binomial": "二項係数",
    "bitwise": "bit演算", "bridge": "橋", "centroid": "重心",
    "characteristic": "特性", "coefficient": "係数", "coefficients": "係数列",
    "coloring": "彩色", "component": "連結成分", "components": "連結成分",
    "compose": "合成", "composition": "合成", "convolution": "畳み込み",
    "count": "個数", "cycle": "閉路", "degree": "次数", "derivative": "微分",
    "diameter": "直径", "difference": "差", "directed": "有向", "distance": "距離",
    "divisor": "約数", "edge": "辺", "edges": "辺", "enumerate": "列挙",
    "evaluate": "評価", "exponential": "指数", "factor": "因子", "factorial": "階乗",
    "flow": "flow", "forest": "forest", "frequency": "頻度", "gcd": "GCD",
    "graph": "グラフ", "hash": "hash", "independent": "独立", "integral": "積分",
    "interpolate": "補間", "interpolation": "補間", "inverse": "逆元",
    "kth": "k番目", "largest": "最大", "lcm": "LCM", "left": "左",
    "length": "長さ", "linear": "線形", "logarithm": "対数", "matching": "matching",
    "matrix": "行列", "max": "最大", "maximum": "最大", "min": "最小",
    "minimum": "最小", "mobius": "Möbius", "modular": "法", "multiply": "積",
    "path": "path", "polynomial": "多項式", "power": "冪", "prefix": "prefix",
    "prime": "素数", "prod": "積", "product": "積", "range": "区間",
    "remainder": "剰余", "right": "右", "root": "根", "shortest": "最短",
    "smallest": "最小", "spanning": "全域", "square": "平方", "string": "文字列",
    "subsequence": "部分列", "subset": "部分集合", "suffix": "suffix", "sum": "和",
    "tree": "木", "undirected": "無向", "value": "値", "values": "値列",
    "vertex": "頂点", "vertices": "頂点", "xor": "XOR", "zeta": "zeta",
}

RETURN_NAME_HINT = {
    "answer": "答え",
    "answers": "答えのlist",
    "component": "連結成分番号",
    "components": "連結成分情報",
    "count": "個数（int）",
    "distance": "距離",
    "distances": "各頂点への距離list",
    "edge_ids": "辺IDのlist",
    "edges": "辺のlist",
    "index": "0-indexedの位置（int）",
    "indices": "位置のlist",
    "parent": "親情報",
    "parents": "親のlist",
    "path": "pathを表すlist",
    "result": "計算結果",
    "results": "計算結果のlist",
    "roots": "根・代表元のlist",
    "size": "size（int）",
    "total": "合計値",
    "value": "値",
    "values": "値のlist",
}

RETURN_SEMANTIC = {
    "__bool__": "bool",
    "__contains__": "bool",
    "__eq__": "bool",
    "__ne__": "bool",
    "__lt__": "bool",
    "__le__": "bool",
    "__gt__": "bool",
    "__ge__": "bool",
    "__len__": "要素数（int）",
    "__iter__": "iterator",
    "__next__": "次の要素",
    "__getitem__": "格納値、sliceなら同種の部分構造",
    "__int__": "int",
    "__index__": "int",
    "access": "指定位置の元の値",
    "all_prod": "全体の集約値（入力要素型）",
    "bisect_left": "境界index（int）",
    "bisect_right": "境界index（int）",
    "connected": "bool",
    "contains": "bool",
    "count": "個数（int）",
    "empty": "bool",
    "find": "代表元・位置・node番号（int）",
    "get": "指定対象に格納された値・edge object",
    "kth": "k番目の値",
    "lca": "最小共通祖先の頂点番号（int）",
    "lower_bound": "条件を満たす最小index（int。存在しなければsize）",
    "max_right": "半開区間の右端index（int）",
    "min_left": "半開区間の左端index（int）",
    "prefix_sum": "prefixの和（入力要素型）",
    "prod": "区間・pathの集約値（入力要素型）",
    "query": "問い合わせ結果（型・tuple形状はclassの用途に従う）",
    "rank": "rank・出現数（int）",
    "range_freq": "条件に合う要素数（int）",
    "same": "bool",
    "size": "size（int）",
    "snapshot": "rollback状態番号（int）",
    "sum": "区間・集合の和（入力要素型）",
    "top": "次に取り出される要素",
}


def markdown_escape(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(text):
    return "`" + str(text).replace("`", "\\`") + "`"


def first_paragraph(doc):
    if not doc:
        return ""
    text = " ".join(doc.strip().splitlines()).strip()
    text = re.sub(r"\s+", " ", text)
    return text if len(text) <= 220 else text[:217] + "..."


def split_words(name):
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [part.lower() for part in name.strip("_").split("_") if part]


def translated_object(name):
    words = split_words(name)
    if not words:
        return code(name)
    converted = [NOUN.get(word, code(word)) for word in words]
    return "・".join(converted)


def purpose_for(name, node, owner=None):
    doc = first_paragraph(ast.get_docstring(node, clean=True))
    if doc:
        return doc
    if name in PROTOCOL_METHODS:
        return PROTOCOL_METHODS[name] + "。"
    if name in EXACT_PURPOSE:
        return EXACT_PURPOSE[name]
    words = split_words(name)
    if not words:
        return code(name) + " を実行する。"
    prefix = words[0]
    obj = "・".join(NOUN.get(word, code(word)) for word in words[1:])
    if prefix in ("is", "has", "can"):
        return (obj or code(name)) + "かどうかを判定する。"
    if prefix in ("get", "query", "access"):
        return (obj or "値") + "を取得する。"
    if prefix in ("set", "assign"):
        return (obj or "値") + "を設定する。"
    if prefix in ("add", "append", "push", "insert"):
        return (obj or "要素") + "を追加する。"
    if prefix in ("remove", "delete", "erase", "discard", "pop"):
        return (obj or "要素") + "を削除する。"
    if prefix in ("build", "make", "construct", "create"):
        return (obj or "構造") + "を構築する。"
    if prefix in ("count", "number"):
        return (obj or "対象") + "の個数を求める。"
    if prefix in ("find", "search", "detect"):
        return (obj or "対象") + "を探索する。"
    if prefix in ("enumerate", "list"):
        return (obj or "対象") + "を列挙する。"
    if prefix in ("restore", "decode"):
        return (obj or "対象") + "を復元する。"
    if prefix in ("encode",):
        return (obj or "対象") + "を符号化する。"
    if prefix in ("update", "change", "modify"):
        return (obj or "状態") + "を更新する。"
    if prefix in ("range", "prefix", "suffix") and words[-1] in EXACT_PURPOSE:
        return translated_object(name) + "を処理する。"
    if prefix in ("minimum", "maximum", "shortest", "longest"):
        return translated_object(name) + "を求める。"
    if any(word in words for word in ("sum", "product", "convolution", "inverse", "logarithm",
                                      "exponential", "interpolation", "rank", "determinant",
                                      "factorization", "decomposition", "transform")):
        return translated_object(name) + "を計算する。"
    suffix = "method" if owner else "function"
    return "%s の %s を実行する。" % (code(owner) if owner else "module", code(name + " " + suffix))


def class_purpose(name, node, module_overview):
    doc = first_paragraph(ast.get_docstring(node, clean=True))
    if doc:
        return doc
    return "%sを扱う %s。" % (module_overview.rstrip("。"), code(name))


def argument_parts(arguments, skip_first=False):
    positional = list(arguments.posonlyargs) + list(arguments.args)
    defaults = [None] * (len(positional) - len(arguments.defaults)) + list(arguments.defaults)
    parts = []
    for idx, (arg, default) in enumerate(zip(positional, defaults)):
        if skip_first and idx == 0 and arg.arg in ("self", "cls"):
            continue
        parts.append((arg.arg, default, "positional", arg.annotation))
        if arguments.posonlyargs and idx + 1 == len(arguments.posonlyargs):
            parts.append(("/", None, "marker", None))
    if arguments.vararg is not None:
        parts.append(("*" + arguments.vararg.arg, None, "vararg", arguments.vararg.annotation))
    elif arguments.kwonlyargs:
        parts.append(("*", None, "marker", None))
    for arg, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
        parts.append((arg.arg, default, "keyword", arg.annotation))
    if arguments.kwarg is not None:
        parts.append(("**" + arguments.kwarg.arg, None, "kwarg", arguments.kwarg.annotation))
    return parts


def render_default(node):
    if node is None:
        return None
    try:
        text = ast.unparse(node)
    except Exception:
        text = "..."
    return text if len(text) <= 80 else text[:77] + "..."


def render_annotation(node):
    if node is None:
        return ""
    try:
        return ": " + ast.unparse(node)
    except Exception:
        return ""


def render_signature(name, node, skip_first=False, property_mode=False):
    if property_mode:
        return name
    parts = []
    for arg_name, default, kind, annotation in argument_parts(node.args, skip_first):
        if kind == "marker":
            parts.append(arg_name)
            continue
        item = arg_name + render_annotation(annotation)
        value = render_default(default)
        if value is not None:
            item += "=" + value
        parts.append(item)
    result = "%s(%s)" % (name, ", ".join(parts))
    if node.returns is not None:
        try:
            result += " -> " + ast.unparse(node.returns)
        except Exception:
            pass
    return result


def argument_description(name):
    plain = name.lstrip("*")
    if plain in ARGUMENT_DESCRIPTION:
        return ARGUMENT_DESCRIPTION[plain]
    if plain.endswith("_id"):
        return plain[:-3] + " のID（0-indexed）"
    if plain.endswith("_ids"):
        return plain[:-4] + " のID列"
    if plain.endswith("_list"):
        return translated_object(plain[:-5]) + "のlist"
    if plain.startswith("is_") or plain.startswith("use_"):
        return translated_object(plain) + "を有効にするか"
    if plain.startswith("max_"):
        return translated_object(plain) + "の上限"
    if plain.startswith("min_"):
        return translated_object(plain) + "の下限"
    return translated_object(plain) + "として渡す値（APIの文脈に従う）"


def render_arguments(node, skip_first=False):
    rows = []
    for name, default, kind, _ in argument_parts(node.args, skip_first):
        if kind == "marker":
            continue
        desc = argument_description(name)
        value = render_default(default)
        if value is not None:
            desc += "。省略時: " + code(value)
        rows.append("%s: %s" % (code(name), desc))
    return "<br>".join(rows) if rows else "なし"


def iter_function_nodes(root):
    """Yield nodes in a function body without entering nested definitions."""
    stack = list(reversed(root.body))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            if node is not root:
                continue
        children = list(ast.iter_child_nodes(node))
        stack.extend(reversed(children))


def _expression_type_atom(node, assignments):
    if node is None:
        return "None"
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        if isinstance(node.value, bool):
            return "bool"
        return type(node.value).__name__
    if isinstance(node, ast.List) or isinstance(node, ast.ListComp):
        return "list"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, ast.Dict) or isinstance(node, ast.DictComp):
        return "dict"
    if isinstance(node, ast.Set) or isinstance(node, ast.SetComp):
        return "set"
    if isinstance(node, ast.GeneratorExp):
        return "iterator"
    if isinstance(node, (ast.Compare, ast.BoolOp)):
        return "bool"
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return "bool"
    if isinstance(node, ast.Name):
        return assignments.get(node.id, "")
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            if func.id in ("list", "tuple", "dict", "set", "int", "float", "str", "bytes", "bool"):
                return func.id
            if func.id and func.id[0].isupper():
                return func.id
        if isinstance(func, ast.Attribute) and func.attr in ("copy",):
            return "入力と同じ型"
    if isinstance(node, ast.BinOp):
        return "数値または入力要素型"
    return ""


def expression_type(node, assignments):
    if not isinstance(node, ast.IfExp):
        return _expression_type_atom(node, assignments)
    kinds = []
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, ast.IfExp):
            stack.append(current.orelse)
            stack.append(current.body)
            continue
        kind = _expression_type_atom(current, assignments)
        if kind and kind not in kinds:
            kinds.append(kind)
    return kinds[0] if len(kinds) == 1 else "/".join(kinds)


def collect_assignments(function):
    result = {}
    for node in iter_function_nodes(function):
        target = value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        if isinstance(target, ast.Name) and value is not None:
            kind = expression_type(value, result)
            if not kind and isinstance(value, ast.BinOp) and isinstance(value.op, ast.Mult):
                if isinstance(value.left, (ast.List, ast.Tuple)) or isinstance(value.right, (ast.List, ast.Tuple)):
                    kind = "list" if isinstance(value.left, ast.List) or isinstance(value.right, ast.List) else "tuple"
            if kind:
                result[target.id] = kind
    return result


def component_description(node, assignments):
    if isinstance(node, ast.Name):
        label = RETURN_NAME_HINT.get(node.id, code(node.id))
        kind = assignments.get(node.id)
        if kind and kind not in label:
            label += "（%s）" % kind
        return label
    kind = expression_type(node, assignments)
    if isinstance(node, ast.Constant):
        return code(repr(node.value))
    try:
        text = ast.unparse(node)
    except Exception:
        text = "式"
    if len(text) > 65:
        text = text[:62] + "..."
    return (kind + " " if kind else "") + code(text)


def return_description(name, function):
    if function.returns is not None:
        try:
            annotation = ast.unparse(function.returns)
        except Exception:
            annotation = None
    else:
        annotation = None
    assignments = collect_assignments(function)
    returns = []
    has_bare = False
    has_yield = False
    for node in iter_function_nodes(function):
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            has_yield = True
        elif isinstance(node, ast.Return):
            if node.value is None or (isinstance(node.value, ast.Constant) and node.value.value is None):
                has_bare = True
            else:
                returns.append(node.value)
    if has_yield:
        return "iterator（yieldされる要素）"
    if not returns:
        return code(annotation) if annotation and annotation != "None" else code("None")

    semantic = RETURN_SEMANTIC.get(name)
    if semantic:
        return semantic + (" / " + code("None") if has_bare else "")
    doc = first_paragraph(ast.get_docstring(function, clean=True))
    match = re.match(r"(?:Return|Compute and return)\s+(.+?)(?:\.|$)", doc)
    if match:
        text = match.group(1).strip()
        if text:
            return text + (" / " + code("None") if has_bare else "")

    descriptions = []
    for value in returns:
        if isinstance(value, ast.Tuple):
            item = "tuple(" + ", ".join(component_description(elt, assignments) for elt in value.elts) + ")"
        elif isinstance(value, ast.Name):
            item = RETURN_NAME_HINT.get(value.id, code(value.id))
            kind = assignments.get(value.id)
            if kind and kind not in item:
                item += "（%s）" % kind
        else:
            kind = expression_type(value, assignments)
            if kind == "bool":
                item = "bool"
            elif kind in ("list", "dict", "set", "tuple", "iterator"):
                item = kind
            elif kind and isinstance(value, ast.Call):
                item = kind + " instance"
            else:
                item = component_description(value, assignments)
        if item not in descriptions:
            descriptions.append(item)
    if annotation and annotation not in ("None", "Any"):
        descriptions.insert(0, code(annotation))
    if name.startswith(("is_", "has_", "can_")) or name in ("same", "connected", "empty", "contains"):
        descriptions = ["bool"]
    if len(descriptions) > 4:
        descriptions = descriptions[:4] + ["ほか（source参照）"]
    text = " / ".join(descriptions)
    if has_bare:
        text += " / " + code("None")
    return text


def decorators(node):
    names = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call):
            decorator = decorator.func
        if isinstance(decorator, ast.Name):
            names.append(decorator.id)
        elif isinstance(decorator, ast.Attribute):
            names.append(decorator.attr)
    return names


def public_methods(class_node):
    methods = []
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name == "__init__":
            continue
        if node.name.startswith("_") and node.name not in PROTOCOL_METHODS:
            continue
        methods.append(node)
    return methods


def aliases_in(body, valid_names):
    aliases = []
    for node in body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id in ("staticmethod", "classmethod", "property")
                and len(value.args) == 1):
            value = value.args[0]
        if not isinstance(value, ast.Name) or value.id not in valid_names:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and not target.id.startswith("_") and target.id != value.id:
                aliases.append((target.id, value.id, node.lineno))
    return aliases


def dataclass_constructor(class_node):
    if "dataclass" not in decorators(class_node):
        return None
    fields = []
    for node in class_node.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        fields.append((node.target.id, node.value, node.annotation))
    return fields


def inherited_constructor(class_node, classes_by_name):
    """Return (init_node, defining_class) for a same-module base class."""
    current = class_node
    seen = {class_node.name}
    while True:
        init = next((node for node in current.body
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and node.name == "__init__"), None)
        if init is not None:
            return init, current
        next_class = None
        for base in current.bases:
            if isinstance(base, ast.Name) and base.id in classes_by_name and base.id not in seen:
                next_class = classes_by_name[base.id]
                break
        if next_class is None:
            return None, None
        seen.add(next_class.name)
        current = next_class


def render_dataclass_signature(class_name, fields):
    parts = []
    for name, default, annotation in fields:
        item = name + render_annotation(annotation)
        value = render_default(default)
        if value is not None:
            item += "=" + value
        parts.append(item)
    return "%s(%s)" % (class_name, ", ".join(parts))


def render_dataclass_arguments(fields):
    rows = []
    for name, default, _ in fields:
        desc = argument_description(name)
        value = render_default(default)
        if value is not None:
            desc += "。省略時: " + code(value)
        rows.append("%s: %s" % (code(name), desc))
    return "<br>".join(rows) if rows else "なし"


def public_constants(module):
    values = []
    for node in module.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        for target in targets:
            if not isinstance(target, ast.Name) or not target.id.isupper() or target.id.startswith("_"):
                continue
            try:
                rendered = ast.unparse(value)
            except Exception:
                rendered = "..."
            if len(rendered) > 100:
                rendered = rendered[:97] + "..."
            values.append((target.id, rendered, node.lineno))
    return values


def read_overviews():
    overviews = dict(MODULE_OVERRIDES)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    by_basename = {}
    for path in source_modules():
        by_basename.setdefault(path.name, []).append(path)
    for line in readme.splitlines():
        if not line.startswith("|") or "`" not in line or ".py`" not in line:
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 3:
            continue
        match = re.fullmatch(r"`([^`]+\.py)`", columns[0])
        if not match:
            continue
        raw = match.group(1)
        candidates = []
        direct = ROOT / raw
        if direct.exists():
            candidates = [direct]
        elif os.path.basename(raw) in by_basename:
            candidates = by_basename[os.path.basename(raw)]
        if len(candidates) == 1:
            key = candidates[0].relative_to(ROOT).as_posix()
            overviews.setdefault(key, (columns[1], columns[2]))
    return overviews


def source_modules():
    result = []
    for category in sorted(path for path in ROOT.iterdir() if path.is_dir() and path.name not in SKIP_DIRS):
        for path in sorted(category.glob("*.py")):
            if path.name != "__init__.py" and not path.name.startswith("_"):
                result.append(path)
    return result


def source_link(relative_path, lineno=None):
    suffix = "#L%d" % lineno if lineno else ""
    return "../../../%s%s" % (relative_path.as_posix(), suffix)


def method_row(node, source_relative, owner):
    decs = decorators(node)
    is_property = "property" in decs
    skip_first = bool(node.args.args and node.args.args[0].arg in ("self", "cls"))
    signature = render_signature(node.name, node, skip_first, is_property)
    kind = "property" if is_property else ("classmethod" if "classmethod" in decs else "method")
    purpose = purpose_for(node.name, node, owner)
    arguments = "なし" if is_property else render_arguments(node, skip_first)
    returned = return_description(node.name, node)
    api = "[%s](%s)" % (code(signature), source_link(source_relative, node.lineno))
    return "| %s | %s | %s | %s | %s |" % tuple(
        markdown_escape(value) for value in (api, kind, purpose, arguments, returned)
    )


def function_row(node, source_relative):
    signature = render_signature(node.name, node)
    api = "[%s](%s)" % (code(signature), source_link(source_relative, node.lineno))
    return "| %s | %s | %s | %s |" % tuple(markdown_escape(value) for value in (
        api, purpose_for(node.name, node), render_arguments(node), return_description(node.name, node)
    ))


def render_module(path, overview, complexity):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    relative = path.relative_to(ROOT)
    module_name = ".".join(("library_codex",) + relative.with_suffix("").parts)
    functions = [node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")]
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and not node.name.startswith("_")]
    defined = {node.name for node in functions + classes}
    classes_by_name = {node.name: node for node in classes}
    aliases = aliases_in(tree.body, defined)
    constants = public_constants(tree)
    count_methods = sum(len(public_methods(node)) for node in classes)
    protocol_count = sum(node.name in PROTOCOL_METHODS for cls in classes for node in public_methods(cls))

    lines = [
        "<!-- Generated by tools/build_api_reference.py; do not edit directly. -->",
        "# `%s`" % module_name,
        "",
        overview.rstrip("。") + "。",
        "",
        "- 計算量の目安: %s" % complexity,
        "- source: [`%s`](%s)" % (relative.as_posix(), source_link(relative)),
        "- 公開API: function %d、class %d、method/property %d（Python protocol %dを含む）" % (
            len(functions), len(classes), count_methods, protocol_count),
        "",
    ]
    import_names = [node.name for node in functions + classes]
    if import_names:
        lines.extend(["## Import", "", "```python"])
        if len(import_names) <= 4:
            lines.append("from %s import %s" % (module_name, ", ".join(import_names)))
        else:
            lines.append("from %s import (" % module_name)
            lines.extend("    %s," % name for name in import_names)
            lines.append(")")
        lines.extend(["```", ""])

    if constants:
        lines.extend(["## 公開定数", "", "| 定数 | 値 | source |", "| --- | --- | --- |"])
        for name, value, lineno in constants:
            lines.append("| %s | %s | [L%d](%s) |" % (
                code(name), code(value), lineno, source_link(relative, lineno)))
        lines.append("")

    if functions:
        lines.extend([
            "## Functions", "",
            "| signature | 用途 | 引数 | 返り値 |",
            "| --- | --- | --- | --- |",
        ])
        lines.extend(function_row(node, relative) for node in functions)
        lines.append("")

    for class_node in classes:
        dataclass_fields = dataclass_constructor(class_node)
        init, init_owner = inherited_constructor(class_node, classes_by_name)
        if dataclass_fields is not None:
            signature = render_dataclass_signature(class_node.name, dataclass_fields)
            args = render_dataclass_arguments(dataclass_fields)
            constructor_line = class_node.lineno
        elif init is None:
            signature = class_node.name + "()"
            args = "なし"
            constructor_line = class_node.lineno
        else:
            signature = render_signature(class_node.name, init, True)
            args = render_arguments(init, True)
            constructor_line = init.lineno
        lines.extend([
            "## Class `%s`" % class_node.name,
            "",
            class_purpose(class_node.name, class_node, overview),
            "",
            "- constructor: [`%s`](%s)" % (signature, source_link(relative, constructor_line)),
            "- 引数: %s" % args,
            "- 返り値: `%s` instance" % class_node.name,
        ])
        if init_owner is not None and init_owner is not class_node:
            lines.append("- constructorは `%s` から継承。" % init_owner.name)
        if class_node.bases:
            base_names = []
            for base in class_node.bases:
                try:
                    base_names.append(ast.unparse(base))
                except Exception:
                    pass
            if base_names:
                lines.append("- 継承元: %s" % ", ".join(code(name) for name in base_names))
        lines.append("")
        methods = public_methods(class_node)
        valid = {node.name for node in methods}
        class_aliases = aliases_in(class_node.body, valid | defined)
        if methods or class_aliases:
            lines.extend([
                "| method / property | 種別 | 用途 | 引数 | 返り値 |",
                "| --- | --- | --- | --- | --- |",
            ])
            lines.extend(method_row(node, relative, class_node.name) for node in methods)
            for alias, target, lineno in class_aliases:
                api = "[%s](%s)" % (code(alias), source_link(relative, lineno))
                lines.append("| %s | alias | %s の別名。 | 同じ | 同じ |" % (api, code(target)))
            lines.append("")
        inherited = []
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id in classes_by_name:
                inherited.append(base.id)
        if inherited:
            lines.extend([
                "継承methodは同ページの %s を参照してください。" % ", ".join(code(name) for name in inherited),
                "",
            ])

    if aliases:
        lines.extend(["## Module aliases", ""])
        for alias, target, lineno in aliases:
            lines.append("- [%s](%s) = %s" % (code(alias), source_link(relative, lineno), code(target)))
        lines.append("")
    if not functions and not classes and not constants:
        lines.extend(["公開APIはありません。", ""])
    return "\n".join(lines).rstrip() + "\n", (len(functions), len(classes), count_methods, len(constants), len(aliases))


def render_category(category, modules):
    lines = [
        "<!-- Generated by tools/build_api_reference.py; do not edit directly. -->",
        "# %s" % category,
        "",
        CATEGORY_DESCRIPTION.get(category, category) + "のAPI一覧です。",
        "",
        "| module | 概要 | functions | classes | methods |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in modules:
        lines.append("| [%s](%s.md) | %s | %d | %d | %d |" % (
            code(item["stem"]), item["stem"], markdown_escape(item["overview"]),
            item["counts"][0], item["counts"][1], item["counts"][2]))
    lines.append("")
    return "\n".join(lines)


def render_index(categories, totals):
    lines = [
        "<!-- Generated by tools/build_api_reference.py; do not edit directly. -->",
        "# library_codex APIリファレンス",
        "",
        "Geometryを除く `library_codex` の公開APIを、source ASTから網羅的に抽出した参照書です。",
        "関数・constructor・methodのsignature、各引数の意味、返り値、source位置を確認できます。",
        "",
        "## 読み方と共通規約",
        "",
        "- 配列・頂点・辺IDは、個別に明記しない限り0-indexedです。",
        "- 区間引数 `(left, right)` / `(l, r)` は、個別に明記しない限り半開区間 `[left, right)` です。",
        "- 多項式・FPSは、個別に明記しない限り昇冪係数列 `[a0, a1, ...]` です。",
        "- `mod=None` は整数上、`mod` 指定時は法 `mod` 上の演算を表します。",
        "- `op` は原則として結合的二項演算、`identity` / `e` はその単位元です。非可換対応の構造では引数順も保持されます。",
        "- `None` を返すmethodの多くは破壊的更新です。version番号を返す永続構造は元versionを変更しません。",
        "- 入力依存のgenericな型は「計算結果」「入力要素型」などと表記します。正確な分岐は各行のsource linkで確認できます。",
        "- API表は手編集せず、`pypy3 library_codex/tools/build_api_reference.py` で再生成します。`--check` はsourceとの同期だけを検査します。",
        "",
        "## 最小の使い方",
        "",
        "```python",
        "from library_codex.data_structure.FenwickTree import FenwickTree",
        "",
        "fw = FenwickTree([3, 1, 4, 1, 5])",
        "fw.add(2, 10)            # index 2 に10加算。返り値はNone",
        "answer = fw.sum(1, 4)    # [1, 4) の和を返す",
        "```",
        "",
        "## Categories",
        "",
        "| category | 内容 | modules | functions | classes | methods |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for category, modules in categories.items():
        cf = sum(item["counts"][0] for item in modules)
        cc = sum(item["counts"][1] for item in modules)
        cm = sum(item["counts"][2] for item in modules)
        lines.append("| [%s](api/%s/README.md) | %s | %d | %d | %d | %d |" % (
            category, category, CATEGORY_DESCRIPTION.get(category, category), len(modules), cf, cc, cm))
    lines.extend([
        "",
        "合計: **%d modules / %d functions / %d classes / %d methods・properties**。" % totals,
        "",
    ])
    return "\n".join(lines)


def build_documents():
    overviews = read_overviews()
    documents = {}
    categories = {}
    total_modules = total_functions = total_classes = total_methods = 0
    missing = []
    for path in source_modules():
        relative = path.relative_to(ROOT)
        key = relative.as_posix()
        if key not in overviews:
            missing.append(key)
            overview = translated_object(path.stem)
            complexity = "source参照"
        else:
            overview, complexity = overviews[key]
        content, counts = render_module(path, overview, complexity)
        destination = API_ROOT / relative.parent / (path.stem + ".md")
        documents[destination] = content
        item = {
            "stem": path.stem,
            "overview": overview,
            "complexity": complexity,
            "counts": counts,
        }
        categories.setdefault(relative.parts[0], []).append(item)
        total_modules += 1
        total_functions += counts[0]
        total_classes += counts[1]
        total_methods += counts[2]
    for category, modules in categories.items():
        documents[API_ROOT / category / "README.md"] = render_category(category, modules)
    totals = (total_modules, total_functions, total_classes, total_methods)
    documents[DOC_ROOT / "README.md"] = render_index(categories, totals)
    return documents, totals, missing


def write_documents(documents):
    expected = set(documents)
    if API_ROOT.exists():
        for old in API_ROOT.rglob("*.md"):
            if old not in expected:
                old.unlink()
    for path, content in documents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")


def check_documents(documents):
    errors = []
    expected = set(documents)
    actual = set(API_ROOT.rglob("*.md")) if API_ROOT.exists() else set()
    extra = actual - expected
    if extra:
        errors.extend("extra generated document: %s" % path.relative_to(ROOT) for path in sorted(extra))
    for path, content in documents.items():
        if not path.exists():
            errors.append("missing generated document: %s" % path.relative_to(ROOT))
        elif path.read_text(encoding="utf-8") != content:
            errors.append("stale generated document: %s" % path.relative_to(ROOT))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated files without writing")
    args = parser.parse_args()
    documents, totals, missing = build_documents()
    if missing:
        for path in missing:
            print("missing module overview:", path, file=sys.stderr)
        return 1
    if args.check:
        errors = check_documents(documents)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("API reference is current: %d modules, %d functions, %d classes, %d methods" % totals)
        return 0
    write_documents(documents)
    print("Wrote %d API documents: %d modules, %d functions, %d classes, %d methods" % (
        len(documents), totals[0], totals[1], totals[2], totals[3]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
