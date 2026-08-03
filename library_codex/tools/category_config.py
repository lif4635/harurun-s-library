"""Canonical source categories and their documentation/navigation metadata."""


DOMAIN_LABELS = {
    "algorithm": "Algorithms",
    "convolution": "Convolution / FPS",
    "data_structure": "Data Structures",
    "graph": "Graph",
    "math": "Math",
    "tree": "Tree",
    "string": "String",
    "optimization": "Optimization",
    "geometry": "Geometry",
    "game": "Game",
    "random": "Random / Heuristic",
}


CATEGORY_INFO = {
    "algorithm": {
        "label": "アルゴリズム",
        "description": "汎用アルゴリズム・列・順列",
        "domain": "algorithm",
    },
    "convolution": {
        "label": "通常畳み込み",
        "description": "通常の畳み込み・DFT・NTT",
        "domain": "convolution",
    },
    "arithmetic_convolution": {
        "label": "GCD・LCM畳み込み",
        "description": "約数・倍数・GCD・LCM・乗法群上の畳み込み",
        "domain": "convolution",
    },
    "bitwise_convolution": {
        "label": "bitwise畳み込み",
        "description": "OR・AND・XOR・subset変換と畳み込み",
        "domain": "convolution",
    },
    "fps": {
        "label": "FPS (F_p)",
        "description": "有限体上の形式的冪級数と母関数の演算",
        "domain": "convolution",
    },
    "polynomial": {
        "label": "多項式",
        "description": "多項式の評価・補間・GCD・因数分解",
        "domain": "convolution",
    },
    "combinatorial_series": {
        "label": "組合せ数列",
        "description": "組合せ数列・漸化式・数列変換",
        "domain": "convolution",
    },
    "segment_tree": {
        "label": "セグメント木",
        "description": "セグメント木と区間更新・区間集約",
        "domain": "data_structure",
    },
    "fenwick_tree": {
        "label": "Fenwick木",
        "description": "Fenwick木と加算・接頭和",
        "domain": "data_structure",
    },
    "union_find": {
        "label": "Union-Find",
        "description": "Union-Findと連結成分管理",
        "domain": "data_structure",
    },
    "ordered_set": {
        "label": "順序集合・rank",
        "description": "順序集合・trie・rank・k番目",
        "domain": "data_structure",
    },
    "sequence_structure": {
        "label": "列・queue・heap",
        "description": "動的列・queue・heap・SWAG",
        "domain": "data_structure",
    },
    "range_query": {
        "label": "静的区間クエリ",
        "description": "静的区間積・RMQ・Wavelet Matrix",
        "domain": "data_structure",
    },
    "spatial_structure": {
        "label": "2次元・直線",
        "description": "2次元クエリ・矩形・直線集合",
        "domain": "data_structure",
    },
    "graph": {
        "label": "グラフ基盤",
        "description": "グラフ表現・変換・基本走査",
        "domain": "graph",
    },
    "shortest_path": {
        "label": "最短路",
        "description": "単一始点・全点対・k本の最短路",
        "domain": "graph",
    },
    "graph_connectivity": {
        "label": "連結性・分解",
        "description": "連結成分・lowlink・SCC・動的連結性",
        "domain": "graph",
    },
    "graph_flow": {
        "label": "フロー",
        "description": "最大流・最小費用流・b-flow",
        "domain": "graph",
    },
    "graph_matching": {
        "label": "マッチング",
        "description": "二部・一般・重み付きマッチング",
        "domain": "graph",
    },
    "graph_spanning": {
        "label": "全域構造",
        "description": "全域木・Steiner木・merge tree",
        "domain": "graph",
    },
    "graph_enumeration": {
        "label": "列挙・小規模グラフ",
        "description": "clique・cycle・彩色・部分集合DP",
        "domain": "graph",
    },
    "number_theory": {
        "label": "整数・数論",
        "description": "整数演算・合同式・乗法的関数",
        "domain": "math",
    },
    "combinatorics": {
        "label": "組合せ",
        "description": "二項係数・組合せ構成",
        "domain": "math",
    },
    "linear_algebra": {
        "label": "線形代数",
        "description": "行列・線形方程式・線形基底",
        "domain": "math",
    },
    "rational": {
        "label": "有理数・数値",
        "description": "有理数探索・有理級数・数値関数",
        "domain": "math",
    },
    "algebra": {
        "label": "代数",
        "description": "写像・累乗・SAT",
        "domain": "math",
    },
    "prime": {
        "label": "素数・素因数分解",
        "description": "素数判定・素因数分解",
        "domain": "math",
    },
    "tree": {
        "label": "木",
        "description": "木アルゴリズム・動的木",
        "domain": "tree",
    },
    "string": {
        "label": "文字列",
        "description": "文字列アルゴリズム",
        "domain": "string",
    },
    "optimization": {
        "label": "最適化・DP",
        "description": "最適化・DP高速化",
        "domain": "optimization",
    },
    "geometry": {
        "label": "幾何",
        "description": "幾何・2次元点",
        "domain": "geometry",
    },
    "game": {
        "label": "ゲーム",
        "description": "組合せゲーム",
        "domain": "game",
    },
    "heuristic": {
        "label": "ヒューリスティック",
        "description": "ヒューリスティック探索",
        "domain": "random",
    },
    "random": {
        "label": "乱数",
        "description": "乱数・ランダムグラフ",
        "domain": "random",
    },
}


SOURCE_CATEGORIES = tuple(CATEGORY_INFO)
CATEGORY_LABELS = {key: value["label"] for key, value in CATEGORY_INFO.items()}
CATEGORY_DESCRIPTION = {
    key: value["description"] for key, value in CATEGORY_INFO.items()
}
CATEGORY_DOMAINS = {key: value["domain"] for key, value in CATEGORY_INFO.items()}
DATA_STRUCTURE_CATEGORIES = {
    key for key, value in CATEGORY_INFO.items()
    if value["domain"] == "data_structure"
}
