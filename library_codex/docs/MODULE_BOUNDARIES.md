# モジュール境界の方針

サイトの1ページとPythonの1ファイルを、原則として「1つの目的」で対応させます。

## 別ファイルに分けるもの

- 利用者が片方だけを選んで使える、目的の異なるデータ構造・アルゴリズム
- 実装方式や更新条件が異なり、constructorや計算量も別に説明すべきもの
- `Advanced*`、`*Extras`、`Collections`、`Structures`のような名前だけでは内容を予測できない寄せ集め

たとえば通常・lazy・dual Segment Tree、各Union-Find、各最短路、彩色数と独立集合、各多項式アルゴリズムは別ファイルです。

## 同じファイルに残すもの

- 同じデータ表現を共有する基本操作の集合
- 片方がもう片方の内部node・view・backendで、単独利用する意味が薄いもの
- 同じ問題に対するforward/inverseやmin/maxなど、同じ前提と説明を共有する関数群

例として `FormalPowerSeries` の基本演算群、`CSRGraph` とCSR専用探索、`RollingHash` のview、`StaticTopTree` のDP wrapperは同じfamilyとして残します。

## bundle

各ページのbundleは、そのページのsourceと実際にimportしているlibrary内依存を再帰的に集めます。別ページの無関係なclassや関数は含めません。依存先も同じ規則で分割されているため、ライブラリが増えてもbundleの範囲はimport関係に沿って決まります。

## 新しい実装を追加するとき

1. 既存の目的と同じで内部表現も共有するなら、既存moduleへの追加を検討する。
2. 単独で選べる別目的なら、その目的が分かる名前の新しいfileに置く。
3. module先頭のdocstringへ「何ができるか」を1文で書く。
4. 公開methodごとの計算量・引数の意味・返り値の形式をdocstringまたはmetadataへ追加する。
5. API生成、bundle検査、全testを通す。
