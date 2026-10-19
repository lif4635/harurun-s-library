# 外部実装のライセンス

`range_query/StaticRangeInversions.py`は、Library Checkerの`static_range_inversions_query/sol/correct.cpp`をPythonへ移した実装で、[Apache License 2.0](Apache-2.0.txt)に従う。リポジトリ直下のUnlicenseではなく、この条件を適用する。生成したstandalone codeにも出典・変更点・ライセンスの表記を残している。

- 元の実装: [correct.cpp](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/data_structure/static_range_inversions_query/sol/correct.cpp)
- 元のライセンス: [LICENSE](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/LICENSE)
- 変更点: Python化、頻度表の整数配列化、分割幅の指定、空配列と範囲検査、デバッグ表示。

`geometry/ConvexLayers.py`も、Library Checkerの実装をPythonへ移したため、[Apache License 2.0](Apache-2.0.txt)に従う。生成したstandalone codeにも出典・変更点・ライセンスの表記を残す。

- 元の実装: [correct.cpp](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/convex_layers/sol/correct.cpp)
- 元のライセンス: [LICENSE](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/LICENSE)
- 変更点: 配列による非再帰実装、同じ層の一括削除、残存する接線の再利用、重複点・空入力・辺の途中の点を残す設定への対応。

`geometry/Delaunay.py`は、Library Checkerのユークリッド最小全域木の実装に含まれる三角形分割をPythonへ移したため、[Apache License 2.0](Apache-2.0.txt)に従う。これを含む`EuclideanMST`のstandalone codeにも出典・変更点・ライセンスの表記を残す。

- 元の実装: [correct.cpp](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/euclidean_mst/sol/correct.cpp)
- 元のライセンス: [LICENSE](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/LICENSE)
- 変更点: 非再帰のPython実装、半辺を平坦な配列で管理して削除領域を再利用、空入力への対応、重複点を元の入力番号で接続。
