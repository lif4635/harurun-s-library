"""Generate the canonical machine-readable catalog for library_codex."""

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import html
import json
import os
import re
import runpy
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


CATEGORY_LABELS = {}
CATEGORY_DOMAINS = {}
DOMAIN_LABELS = {}
SEARCH_TERMS_BY_MODULE = {}
SEARCH_TERMS_BY_SYMBOL = {}
API_DETAILS_BY_SYMBOL = {}
CLASS_DETAILS_BY_SYMBOL = {}
COMPLEXITY_BY_MODULE = {}
SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "library-catalog.json"
COMPATIBILITY_MODULES = {
    "algorithm/BasicAlgorithms.py",
    "algorithm/MiscAlgorithms.py",
}


def source_revision(library_root):
    repository = library_root.parent
    try:
        branch = subprocess.run(
            ["git", "-C", str(repository), "symbolic-ref", "--short", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.strip()
        if branch:
            return branch
    except (OSError, subprocess.CalledProcessError):
        pass
    try:
        return subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "working-tree"


def verified_test_count(library_root):
    readme = (library_root / "README.md").read_text(encoding="utf-8")
    match = re.search(r"PyPy 全検証:\s*(\d+) passed", readme)
    return int(match.group(1)) if match else 0


def clean_markdown(value):
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("<br>", " · ").replace("`", "").replace(r"\|", "|")
    value = re.sub(r"\s+", " ", html.unescape(value))
    return value.strip()


def unique_search_terms(*groups):
    result = []
    seen = set()
    for group in groups:
        for raw in group:
            term = clean_markdown(str(raw)).strip()
            key = term.casefold()
            if term and key not in seen:
                seen.add(key)
                result.append(term)
    return result


def identifier_search_terms(value):
    value = str(value).strip()
    if not value:
        return []
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
    spaced = re.sub(r"[_./]+", " ", spaced)
    return unique_search_terms((value, spaced))


def symbol_search_terms(module_key, name, signature, summary):
    return unique_search_terms(
        identifier_search_terms(name),
        (signature,),
        SEARCH_TERMS_BY_SYMBOL.get((module_key, name), ()),
    )


def api_detail(module_key, owner, name):
    return API_DETAILS_BY_SYMBOL.get((module_key, owner, name), {})


def class_detail(module_key, name):
    return CLASS_DETAILS_BY_SYMBOL.get((module_key, name), {})


PROSE_REPLACEMENTS = (
    ("priority queue", "優先度付きキュー"),
    ("functional graph", "関数グラフ"),
    ("binary lifting", "ダブリング"),
    ("adjacency list", "隣接リスト"),
    ("隣接list", "隣接リスト"),
    ("頂点group", "頂点グループ"),
    ("dict/固定alphabet", "辞書/固定文字集合"),
    ("lower/upper bound", "下限・上限探索"),
    ("segment tree", "セグメント木"),
    ("bit mask", "ビットマスク"),
    ("set bit", "1になっているビット"),
    ("0-indexed", "0始まり"),
    ("1-indexed", "1始まり"),
    ("backend", "実装"),
    ("bipartite", "二部グラフ"),
    ("substring", "部分文字列"),
    ("matching", "マッチング"),
    ("callback", "コールバック"),
    ("alphabet", "文字集合"),
    ("offline", "オフライン"),
    ("online", "オンライン"),
    ("monoid", "モノイド"),
    ("cluster", "クラスタ"),
    ("rollback", "ロールバック"),
    ("version", "バージョン"),
    ("pattern", "パターン"),
    ("circular", "巡回"),
    ("prefix", "接頭"),
    ("suffix", "接尾"),
    ("forest", "森"),
    ("graph", "グラフ"),
    ("node", "ノード"),
    ("path", "経路"),
    ("group", "グループ"),
    ("query", "クエリ"),
    ("range", "区間"),
    ("shift", "シフト"),
    ("sparse", "疎"),
    ("lazy", "遅延"),
    ("grid", "グリッド"),
    ("heap", "ヒープ"),
    ("queue", "キュー"),
    ("hash", "ハッシュ"),
    ("rank", "ランク"),
    ("profit", "利益"),
    ("cost", "コスト"),
    ("sort", "ソート"),
    ("object", "オブジェクト"),
    ("iterable", "反復可能オブジェクト"),
    ("edge", "辺"),
    ("mask", "マスク"),
    ("bit", "ビット"),
)


def localize_prose(value):
    """Translate incidental English in user-facing prose, not code or types."""
    value = clean_markdown(value)
    for english, japanese in PROSE_REPLACEMENTS:
        value = re.sub(
            rf"(?<![A-Za-z_]){re.escape(english)}(?![A-Za-z_])",
            japanese,
            value,
            flags=re.IGNORECASE,
        )
    return value


def localize_class_description(name, value):
    value = localize_prose(value)
    match = re.fullmatch(rf"(.+?)を扱う\s+{re.escape(name)}。", value)
    if not match:
        return value
    topic = match.group(1)
    if topic.endswith("を扱う"):
        return f"{name} は{topic}。"
    return f"{name} は{topic}を扱う。"


def localize_capability(value):
    value = localize_prose(value)
    match = re.match(r"^([A-Za-z_]\w*):\s*(.+)$", value)
    if not match:
        return value
    name, description = match.groups()
    description = localize_class_description(name, description)
    prefix = f"{name} は"
    if description.startswith(prefix):
        description = description[len(prefix):]
    return f"{name}: {description}"


def split_markdown_row(line):
    """Split a Markdown table row without breaking escaped union pipes."""
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [cell.strip().replace(r"\|", "|") for cell in cells]


def clean_complexity(value):
    value = clean_markdown(value).replace("$", "")
    replacements = {
        "\\log": "log ",
        "\\sqrt": "sqrt ",
        "\\alpha": "α",
        "\\sigma": "σ",
        "\\lceil": "⌈",
        "\\rceil": "⌉",
    }
    for before, after in replacements.items():
        value = value.replace(before, after)
    translations = {
        "number of exponent blocks": "K",
        "sqrt(number)": "sqrt N",
        "sqrt(count)": "sqrt K",
        "log index": "log n",
        "offline全処理": "オフライン全処理",
        "online操作": "オンライン操作",
        "amortized": "償却",
        "algorithm": "アルゴリズム",
        "cost scaling": "コストスケーリング",
        "Euclid path": "ユークリッド法の反復回数",
        "iteration依存": "反復回数に依存",
        "min-cut": "最小カット",
        "oracle依存": "オラクル呼び出し回数に依存",
        "polylogarithmic": "多重対数",
        "query": "問い合わせ",
        "source参照": "実装依存",
        "subset": "部分集合",
        "sweep": "走査",
        "heap": "ヒープ",
        "find": "検索",
        "unite": "併合",
        "sigma": "σ",
        "64-bit": "64ビット",
    }
    for before, after in translations.items():
        value = re.sub(re.escape(before), after, value, flags=re.IGNORECASE)
    return re.sub(r"\\([A-Za-z]+)", r"\1", value).strip()


def big_o_terms(value):
    terms = []
    index = 0
    while True:
        start = value.find("O(", index)
        if start < 0:
            break
        depth = 0
        end = start
        for end in range(start + 1, len(value)):
            if value[end] == "(":
                depth += 1
            elif value[end] == ")":
                depth -= 1
                if depth == 0:
                    end += 1
                    break
        term = clean_complexity(value[start:end])
        if term and term not in terms:
            terms.append(term)
        index = max(end, start + 2)
    return terms


def concise_complexity(value):
    terms = big_o_terms(value)
    return " / ".join(terms) if terms else clean_complexity(value)


def documented_complexity(docstring):
    if not docstring:
        return ""
    terms = big_o_terms(docstring)
    if terms:
        return " / ".join(terms)
    for sentence in re.split(r"(?<=[.!?。])\s+|\n+", docstring):
        if re.search(r"constant time", sentence, re.IGNORECASE):
            return "O(1)"
        if re.search(r"linear time", sentence, re.IGNORECASE):
            return "O(N)"
    return ""


def source_complexities(source_path):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    symbols = {}
    classes = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            value = documented_complexity(ast.get_docstring(node, clean=True))
            if value:
                symbols[(None, node.name)] = value
        elif isinstance(node, ast.ClassDef):
            class_value = documented_complexity(ast.get_docstring(node, clean=True))
            if class_value:
                classes[node.name] = class_value
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    value = documented_complexity(ast.get_docstring(item, clean=True))
                    if value:
                        symbols[(node.name, item.name)] = value
    return symbols, classes


def _expression_atom_format(node, assignments, owner):
    if node is None:
        return "None"
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        return type(node.value).__name__
    if isinstance(node, (ast.List, ast.ListComp)):
        return "list"
    if isinstance(node, (ast.Dict, ast.DictComp)):
        return "dict"
    if isinstance(node, (ast.Set, ast.SetComp)):
        return "set"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, (ast.GeneratorExp, ast.Yield, ast.YieldFrom)):
        return "iterator"
    if isinstance(node, (ast.Compare, ast.BoolOp)):
        return "bool"
    if isinstance(node, ast.Name):
        if node.id == "self" and owner:
            return f"{owner} instance"
        return assignments.get(node.id, "")
    if isinstance(node, (ast.BinOp, ast.UnaryOp)):
        return "int / float"
    if isinstance(node, ast.Call):
        function = node.func
        name = ""
        if isinstance(function, ast.Name):
            name = function.id
        elif isinstance(function, ast.Attribute):
            name = function.attr
        lower = name.lower()
        builtins = {
            "bool": "bool",
            "dict": "dict",
            "enumerate": "iterator",
            "float": "float",
            "int": "int",
            "iter": "iterator",
            "len": "int",
            "list": "list",
            "reversed": "iterator",
            "set": "set",
            "sorted": "list",
            "str": "str",
            "sum": "int / float",
            "tuple": "tuple",
            "zip": "iterator",
        }
        if lower in builtins:
            return builtins[lower]
        if name and (name[0].isupper() or name.endswith("Iterator")):
            return f"{name} instance"
    return ""


def expression_format(node, assignments, owner):
    if not isinstance(node, ast.IfExp):
        return _expression_atom_format(node, assignments, owner)
    values = set()
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, ast.IfExp):
            stack.append(current.orelse)
            stack.append(current.body)
            continue
        value = _expression_atom_format(current, assignments, owner)
        if value:
            values.add(value)
    return " / ".join(sorted(values))


def function_return_format(node, owner):
    if node.returns is not None:
        try:
            annotation = ast.unparse(node.returns)
            if annotation not in ("Any", "None"):
                return annotation
        except Exception:
            pass
    assignments = {}
    for child in ast.walk(node):
        if isinstance(child, ast.Assign):
            value_format = expression_format(child.value, assignments, owner)
            for target in child.targets:
                if isinstance(target, ast.Name) and value_format:
                    assignments[target.id] = value_format
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            try:
                assignments[child.target.id] = ast.unparse(child.annotation)
            except Exception:
                pass
    formats = []
    has_yield = False
    for child in ast.walk(node):
        if isinstance(child, (ast.Yield, ast.YieldFrom)):
            has_yield = True
        elif isinstance(child, ast.Return):
            value_format = expression_format(child.value, assignments, owner)
            if value_format and value_format not in formats:
                formats.append(value_format)
    if has_yield:
        return "iterator"
    if not formats:
        return "None"
    return " / ".join(formats)


def source_return_formats(source_path):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    result = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result[(None, node.name)] = function_return_format(node, None)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[(node.name, item.name)] = function_return_format(item, node.name)
    return result


def module_name_for(source_path, library_root):
    relative = source_path.relative_to(library_root).with_suffix("")
    return ".".join(("library_codex", *relative.parts))


def internal_dependencies(source_path, library_root):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    result = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        for module_name in names:
            parts = module_name.split(".")
            if parts[0] == "library_codex":
                parts = parts[1:]
            elif parts[0] not in CATEGORY_LABELS:
                continue
            relative = Path(*parts).with_suffix(".py")
            dependency = library_root / relative
            if dependency.is_file() and dependency not in result:
                result.append(dependency)
    return result


def internal_module_path(module_name, library_root):
    parts = module_name.split(".")
    if parts[0] == "library_codex":
        parts = parts[1:]
    elif parts[0] not in CATEGORY_LABELS:
        return None
    candidate = library_root.joinpath(*parts).with_suffix(".py")
    return candidate if candidate.is_file() else None


def bound_target_names(target):
    result = set()
    stack = [target]
    while stack:
        current = stack.pop()
        if isinstance(current, ast.Name):
            result.add(current.id)
        elif isinstance(current, (ast.Tuple, ast.List)):
            stack.extend(current.elts)
        elif isinstance(current, ast.Starred):
            stack.append(current.value)
    return result


class ScopeBindings(ast.NodeVisitor):
    """Collect bindings in one lexical scope without entering child scopes."""

    def __init__(self):
        self.names = set()
        self.globals = set()
        self.nonlocals = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names.add(node.id)

    def visit_FunctionDef(self, node):
        self.names.add(node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.names.add(node.name)

    def visit_Lambda(self, node):
        return

    def visit_ListComp(self, node):
        return

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_Import(self, node):
        for item in node.names:
            self.names.add(item.asname or item.name.split(".", 1)[0])

    def visit_ImportFrom(self, node):
        if node.module == "__future__":
            return
        for item in node.names:
            if item.name != "*":
                self.names.add(item.asname or item.name)

    def visit_ExceptHandler(self, node):
        if node.name:
            self.names.add(node.name)
        for item in node.body:
            self.visit(item)

    def visit_Global(self, node):
        self.globals.update(node.names)

    def visit_Nonlocal(self, node):
        self.nonlocals.update(node.names)


def scope_bindings(body, arguments=None):
    collector = ScopeBindings()
    for node in body:
        collector.visit(node)
    if arguments is not None:
        for arg in (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        ):
            collector.names.add(arg.arg)
        if arguments.vararg:
            collector.names.add(arguments.vararg.arg)
        if arguments.kwarg:
            collector.names.add(arguments.kwarg.arg)
    collector.names.difference_update(collector.globals)
    collector.names.difference_update(collector.nonlocals)
    return collector


class DirectInternalImports(ast.NodeVisitor):
    """Find internal imports belonging to one lexical scope."""

    def __init__(self, library_root, symbol_maps):
        self.library_root = library_root
        self.symbol_maps = symbol_maps
        self.aliases = {}

    def visit_FunctionDef(self, node):
        return

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef
    visit_ListComp = visit_FunctionDef
    visit_SetComp = visit_FunctionDef
    visit_DictComp = visit_FunctionDef
    visit_GeneratorExp = visit_FunctionDef

    def visit_Import(self, node):
        for item in node.names:
            if internal_module_path(item.name, self.library_root):
                raise ValueError(
                    "standalone bundles require 'from ... import ...' for internal modules: "
                    f"{item.name}"
                )

    def visit_ImportFrom(self, node):
        if not node.module:
            return
        target = internal_module_path(node.module, self.library_root)
        if target is None:
            return
        exports = self.symbol_maps[target]
        for item in node.names:
            if item.name == "*":
                raise ValueError(f"star import is not supported in bundles: {node.module}")
            local_name = item.asname or item.name
            try:
                self.aliases[local_name] = exports[item.name]
            except KeyError as error:
                raise ValueError(
                    f"{node.module} does not define imported name {item.name!r}"
                ) from error


def direct_internal_aliases(body, library_root, symbol_maps):
    collector = DirectInternalImports(library_root, symbol_maps)
    for node in body:
        collector.visit(node)
    return collector.aliases


def direct_internal_import_names(body, library_root):
    """Return names bound by internal imports in one lexical scope."""

    class Collector(ast.NodeVisitor):
        def __init__(self):
            self.names = set()

        def visit_FunctionDef(self, node):
            return

        visit_AsyncFunctionDef = visit_FunctionDef
        visit_ClassDef = visit_FunctionDef
        visit_Lambda = visit_FunctionDef
        visit_ListComp = visit_FunctionDef
        visit_SetComp = visit_FunctionDef
        visit_DictComp = visit_FunctionDef
        visit_GeneratorExp = visit_FunctionDef

        def visit_ImportFrom(self, node):
            if not node.module or not internal_module_path(node.module, library_root):
                return
            for item in node.names:
                if item.name != "*":
                    self.names.add(item.asname or item.name)

    collector = Collector()
    for node in body:
        collector.visit(node)
    return collector.names


def module_prefix(source_path, library_root):
    relative = source_path.relative_to(library_root).with_suffix("")
    words = []
    for part in relative.parts:
        part = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", part)
        part = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", part)
        words.append(part.lower())
    slug = "_".join(words)
    slug = re.sub(r"[^a-z0-9_]+", "_", slug).strip("_")
    return f"_{slug}_"


class FlatBundleTransformer(ast.NodeTransformer):
    """Remove internal imports and rewrite their globals as ordinary private names."""

    def __init__(self, library_root, symbol_maps, module_symbols):
        self.library_root = library_root
        self.symbol_maps = symbol_maps
        self.module_symbols = module_symbols
        self.scopes = []

    def push_scope(self, kind, body, arguments=None):
        bindings = scope_bindings(body, arguments)
        aliases = direct_internal_aliases(body, self.library_root, self.symbol_maps)
        self.scopes.append({
            "kind": kind,
            "locals": bindings.names,
            "globals": bindings.globals,
            "nonlocals": bindings.nonlocals,
            "aliases": aliases,
        })

    def mapped_name(self, name):
        current_kind = self.scopes[-1]["kind"]
        for scope in reversed(self.scopes):
            if scope["kind"] == "class" and current_kind in {"function", "lambda", "comprehension"}:
                continue
            if name in scope["aliases"]:
                return scope["aliases"][name]
            if name in scope["globals"]:
                return self.module_symbols.get(name, name)
            if name in scope["locals"] and scope["kind"] != "module":
                return name
        return self.module_symbols.get(name, name)

    def visit_Name(self, node):
        mapped = self.mapped_name(node.id)
        return ast.copy_location(ast.Name(id=mapped, ctx=node.ctx), node)

    def visit_Global(self, node):
        return ast.copy_location(
            ast.Global(names=[self.module_symbols.get(name, name) for name in node.names]),
            node,
        )

    def visit_Import(self, node):
        for item in node.names:
            if internal_module_path(item.name, self.library_root):
                return None
        if self.scopes[-1]["kind"] != "module":
            return node
        names = []
        for item in node.names:
            bound_name = item.asname or item.name.split(".", 1)[0]
            mapped = self.module_symbols.get(bound_name, bound_name)
            names.append(ast.alias(name=item.name, asname=mapped if mapped != bound_name else item.asname))
        return ast.copy_location(ast.Import(names=names), node)

    def visit_ImportFrom(self, node):
        if node.module == "__future__":
            return None
        if node.module and internal_module_path(node.module, self.library_root):
            return None
        if self.scopes[-1]["kind"] != "module":
            return node
        names = []
        for item in node.names:
            bound_name = item.asname or item.name
            mapped = self.module_symbols.get(bound_name, bound_name)
            names.append(ast.alias(name=item.name, asname=mapped if mapped != bound_name else item.asname))
        return ast.copy_location(
            ast.ImportFrom(module=node.module, names=names, level=node.level),
            node,
        )

    def visit_FunctionDef(self, node):
        parent_kind = self.scopes[-1]["kind"]
        if parent_kind == "module":
            node.name = self.module_symbols.get(node.name, node.name)
        node.decorator_list = [self.visit(item) for item in node.decorator_list]
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            if arg.annotation:
                arg.annotation = self.visit(arg.annotation)
        if node.args.vararg and node.args.vararg.annotation:
            node.args.vararg.annotation = self.visit(node.args.vararg.annotation)
        if node.args.kwarg and node.args.kwarg.annotation:
            node.args.kwarg.annotation = self.visit(node.args.kwarg.annotation)
        node.args.defaults = [self.visit(item) for item in node.args.defaults]
        node.args.kw_defaults = [self.visit(item) if item else None for item in node.args.kw_defaults]
        if node.returns:
            node.returns = self.visit(node.returns)
        self.push_scope("function", node.body, node.args)
        node.body = self.visit_statements(node.body)
        self.scopes.pop()
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        if self.scopes[-1]["kind"] == "module":
            node.name = self.module_symbols.get(node.name, node.name)
        node.decorator_list = [self.visit(item) for item in node.decorator_list]
        node.bases = [self.visit(item) for item in node.bases]
        for keyword in node.keywords:
            keyword.value = self.visit(keyword.value)
        self.push_scope("class", node.body)
        node.body = self.visit_statements(node.body)
        self.scopes.pop()
        return node

    def visit_Lambda(self, node):
        node.args.defaults = [self.visit(item) for item in node.args.defaults]
        node.args.kw_defaults = [self.visit(item) if item else None for item in node.args.kw_defaults]
        self.scopes.append({
            "kind": "lambda",
            "locals": scope_bindings([], node.args).names,
            "globals": set(),
            "nonlocals": set(),
            "aliases": {},
        })
        node.body = self.visit(node.body)
        self.scopes.pop()
        return node

    def visit_comprehension_expression(self, node, value_fields):
        first, *rest = node.generators
        first.iter = self.visit(first.iter)
        locals_ = set().union(*(bound_target_names(item.target) for item in node.generators))
        self.scopes.append({
            "kind": "comprehension",
            "locals": locals_,
            "globals": set(),
            "nonlocals": set(),
            "aliases": {},
        })
        first.target = self.visit(first.target)
        first.ifs = [self.visit(item) for item in first.ifs]
        for item in rest:
            item.iter = self.visit(item.iter)
            item.target = self.visit(item.target)
            item.ifs = [self.visit(condition) for condition in item.ifs]
        for field in value_fields:
            setattr(node, field, self.visit(getattr(node, field)))
        self.scopes.pop()
        return node

    def visit_ListComp(self, node):
        return self.visit_comprehension_expression(node, ("elt",))

    visit_SetComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_DictComp(self, node):
        return self.visit_comprehension_expression(node, ("key", "value"))

    def visit_statements(self, body):
        result = []
        for node in body:
            transformed = self.visit(node)
            if transformed is None:
                continue
            if isinstance(transformed, list):
                result.extend(transformed)
            else:
                result.append(transformed)
        return result

    def transform(self, tree):
        self.push_scope("module", tree.body)
        tree.body = self.visit_statements(tree.body)
        self.scopes.pop()
        return ast.fix_missing_locations(tree)


def build_standalone_code(source_path, library_root):
    order = []
    visited = set()
    active = set()
    stack = [(source_path, False)]
    while stack:
        path, expanded = stack.pop()
        if path in visited:
            continue
        if expanded:
            active.remove(path)
            visited.add(path)
            if path != source_path:
                order.append(path)
            continue
        if path in active:
            raise ValueError(f"cyclic internal import while bundling {source_path}: {path}")
        active.add(path)
        stack.append((path, True))
        dependencies = internal_dependencies(path, library_root)
        for dependency in reversed(dependencies):
            if dependency in active:
                raise ValueError(
                    f"cyclic internal import while bundling {source_path}: {dependency}"
                )
            if dependency not in visited:
                stack.append((dependency, False))
    source = source_path.read_text(encoding="utf-8").rstrip() + "\n"
    if not order:
        return source, []

    paths = [*order, source_path]
    trees = {
        path: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for path in paths
    }
    bindings_by_path = {
        path: scope_bindings(trees[path].body)
        for path in paths
    }
    own_names_by_path = {
        path: bindings_by_path[path].names
        - direct_internal_import_names(trees[path].body, library_root)
        for path in paths
    }

    # The code shown on the site should still look like code a person would
    # normally write.  Keep public dependency names (SegmentTree, UnionFind,
    # and so on) whenever they do not collide with another top-level name.
    # Private names and actual collisions retain a module-derived prefix.
    claimed_names = set(own_names_by_path[source_path])
    symbol_maps = {}
    for path in paths:
        own_names = own_names_by_path[path]
        if path == source_path:
            symbols = {name: name for name in own_names}
        else:
            prefix = module_prefix(path, library_root)
            stripped_counts = Counter(name.lstrip("_") for name in own_names)
            symbols = {}
            for name in sorted(own_names):
                if not name.startswith("_") and name not in claimed_names:
                    mapped = name
                else:
                    suffix = (
                        name.lstrip("_")
                        if stripped_counts[name.lstrip("_")] == 1
                        else name
                    )
                    mapped = f"{prefix}{suffix}"
                    serial = 2
                    while mapped in claimed_names:
                        mapped = f"{prefix}{suffix}_{serial}"
                        serial += 1
                symbols[name] = mapped
                claimed_names.add(mapped)
        aliases = direct_internal_aliases(trees[path].body, library_root, symbol_maps)
        symbols.update(aliases)
        symbol_maps[path] = symbols

    future_features = []
    sections = []
    for path in paths:
        tree = trees[path]
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                for item in node.names:
                    if item.name not in future_features:
                        future_features.append(item.name)
        transformed = FlatBundleTransformer(
            library_root,
            symbol_maps,
            symbol_maps[path],
        ).transform(tree)
        label = "本体" if path == source_path else (
            f"依存: {path.relative_to(library_root).as_posix()}"
        )
        sections.append(f"# {label}\n{ast.unparse(transformed).rstrip()}")

    lines = [
        "# harurun's library（依存を含む貼り付け用コード）",
    ]
    if future_features:
        lines.extend(["", f"from __future__ import {', '.join(future_features)}"])
    lines.extend(["", "\n\n".join(sections), ""])
    names = [module_name_for(path, library_root) for path in order]
    return "\n".join(lines), names


def validate_standalone_code(code, source_path):
    """Fail the data sync instead of publishing a broken standalone bundle."""
    filename = f"<standalone {source_path.name}>"
    namespace = {"__name__": "__bundle_validation__"}
    exec(compile(code, filename, "exec"), namespace)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    expected = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    missing = [name for name in expected if name not in namespace]
    if missing:
        raise ValueError(
            f"standalone bundle for {source_path} is missing symbols: {', '.join(missing)}"
        )


FRIENDLY_ARGUMENTS = {
    "*shape": "各次元の大きさ",
    "*indices_and_value": "末尾を設定値、その前を各次元の位置番号として渡す列",
    "a_or_n": "係数 a または要素数 n",
    "adjacency": "隣接リスト",
    "add": "要素を追加するときに呼ぶ関数",
    "add_edge": "辺を追加するときに呼ぶ関数",
    "add_left": "区間の左側へ要素を追加するときに呼ぶ関数",
    "add_right": "区間の右側へ要素を追加するときに呼ぶ関数",
    "add_vertex": "頂点を追加するときに呼ぶ関数",
    "bases": "各桁の基数を並べた列",
    "bit_length": "扱うビット数",
    "block_size": "1ブロックに含める要素数",
    "board": "盤面を表す2次元列",
    "boards": "盤面を並べた列",
    "build_dag": "縮約後のDAGも作るか",
    "bottom": "矩形の下端（この行は含まない）",
    "column": "列番号（0始まり）",
    "columns": "列数",
    "count": "処理する個数",
    "calculate": "必要な値を計算して返す関数",
    "characteristic": "特性多項式の係数列",
    "check_nonnegative": "負の値がないか検査するか",
    "check_weights": "辺の重みを検査するか",
    "coefficient_degree": "係数として使う次数",
    "combine": "2つの情報をまとめる関数",
    "complete_transitions": "遷移を最後まで適用するか",
    "compress": "座標や状態を圧縮するか",
    "difference": "加える差分値",
    "default_factory": "初期値を生成する関数",
    "derivatives": "導関数の値を並べた列",
    "direct_threshold": "直接計算へ切り替える大きさの上限",
    "down": "子方向から受け取る情報またはその計算関数",
    "duration": "処理を続ける時間",
    "d": "次数・距離などを表す整数",
    "element": "処理対象の要素",
    "end_temperature": "探索終了時の温度",
    "exact": "厳密な条件で処理するか",
    "exponential": "指数関数として使う係数列",
    "extra": "追加で渡す情報",
    "f": "評価または変換に使う関数",
    "fill_frequency": "値の出現回数を補完するか",
    "first_variable": "1つ目の変数番号",
    "first_value": "1つ目の変数へ設定する値",
    "flow": "流量",
    "flow_class": "使用するフロー実装のクラス",
    "force_size_n": "結果の長さを n に揃えるか",
    "from_left": "左側から進む情報またはその計算関数",
    "from_right": "右側から進む情報またはその計算関数",
    "edge": "辺",
    "edges": "辺の列",
    "graph": "隣接リスト",
    "groups": "グループ分けを表す列",
    "grid": "グリッドを表す2次元列",
    "height": "行数",
    "index": "操作する位置（0始まり）",
    "indices": "位置番号の列（0始まり）",
    "initialize": "初期状態を作る関数",
    "inverse": "逆変換を行うか",
    "imaginary_angle": "虚部方向の回転角",
    "include_left": "左端を結果に含めるか",
    "include_right": "右端を結果に含めるか",
    "items": "処理する要素の列",
    "k": "選ぶ個数・順位などを表す整数",
    "left1": "1つ目の範囲の左端（この位置を含む）",
    "left2": "2つ目の範囲の左端（この位置を含む）",
    "left_options": "左側で選べる候補の列",
    "lexicographical": "辞書順で処理するか",
    "largest": "大きい側から選ぶか",
    "lazy_identity": "遅延操作の単位元",
    "lst": "処理対象の列",
    "lower_bound": "探索範囲の下限",
    "maximum": "許可する最大値",
    "maximize": "最大化問題として扱うか",
    "merge": "2つの情報を併合する関数",
    "merge_adjacent": "接している区間も結合するか",
    "minimum": "許可する最小値",
    "multiplicity": "同じ要素を数える重複度",
    "naive_threshold": "単純計算へ切り替える大きさの上限",
    "normalize": "結果を正規化するか",
    "left": "範囲の左端（この位置を含む）",
    "mod": "剰余計算に使う法",
    "modulus": "剰余計算に使う法",
    "n": "要素数",
    "op": "2つの値をまとめる関数",
    "one": "乗算に対する単位元",
    "p": "位置・法など、このAPIで基準にする整数",
    "passable": "そのマスを通れるか判定する関数",
    "pivot_end": "ピボットとして扱う範囲の終端",
    "prefix_end": "接頭部分として扱う終端",
    "prime_prefix": "素数の累積情報を持つ列",
    "previous": "直前の状態または値",
    "put_edge": "辺の情報を書き込む関数",
    "put_vertex": "頂点の情報を書き込む関数",
    "ql": "問い合わせ範囲の左端（この位置を含む）",
    "qr": "問い合わせ範囲の右端（この位置は含まない）",
    "query": "現在の答えを返す関数",
    "query_count": "予定している問い合わせ数",
    "rake": "部分木の情報を併合する関数",
    "remove": "要素を取り除くときに呼ぶ関数",
    "remove_left": "区間の左側から要素を外すときに呼ぶ関数",
    "remove_right": "区間の右側から要素を外すときに呼ぶ関数",
    "reversible": "順序を反転できる情報として扱うか",
    "real_angle": "実部方向の回転角",
    "roots": "根として使う頂点番号の列",
    "right": "範囲の右端（この位置は含まない）",
    "right1": "1つ目の範囲の右端（この位置は含まない）",
    "right2": "2つ目の範囲の右端（この位置は含まない）",
    "right_options": "右側で選べる候補の列",
    "row": "行番号（0始まり）",
    "rows": "行数",
    "size": "要素数",
    "source": "始点の頂点番号",
    "start": "開始位置または始点",
    "start_temperature": "探索開始時の温度",
    "star": "スター変換を適用するか",
    "starts": "開始位置を並べた列",
    "splittable": "途中で分割できる対象として扱うか",
    "signed_bits": "符号付き整数として使うビット数",
    "successor": "各頂点の次の行き先を並べた列",
    "target_depth": "移動先として指定する深さ",
    "to": "行き先の頂点番号",
    "to_left": "左方向へ進む情報またはその計算関数",
    "to_right": "右方向へ処理するか",
    "toward_root": "根の方向へ処理するか",
    "top": "矩形の上端（この行を含む）",
    "top_tree": "操作対象のTop Tree",
    "tree1": "1つ目の木の隣接リスト",
    "tree2": "2つ目の木の隣接リスト",
    "transpose": "転置した向きで計算するか",
    "true_value": "条件を満たすことが分かっている境界値",
    "false_value": "条件を満たさないことが分かっている境界値",
    "update": "値を更新するときに呼ぶ関数",
    "up": "親方向から受け取る情報またはその計算関数",
    "variable_count": "変数の個数",
    "second_variable": "2つ目の変数番号",
    "second_value": "2つ目の変数へ設定する値",
    "weight0": "状態0に対応する重み",
    "weight1": "状態1に対応する重み",
    "with_distance": "距離も一緒に返すか",
    "values": "初期値の列",
    "vertex": "頂点番号（0始まり）",
    "vertex_count": "頂点数",
    "width": "列数",
    "xs": "処理対象の値を並べた列",
    "ys": "処理対象の値を並べた列",
}

FRIENDLY_ARGUMENTS.update({
    "apply": "状態へ操作を適用する関数",
    "block_bits": "1ブロックに含めるビット数",
    "build": "前処理を実行するか、または前処理用の関数",
    "column_base": "列番号に加える基準値",
    "constant": "定数項",
    "container_type": "結果を格納するコンテナの型",
    "convolution": "畳み込みを計算する関数",
    "cost_one": "状態1を選ぶコスト",
    "cost_zero": "状態0を選ぶコスト",
    "edge_leaf": "辺を葉として扱うか",
    "elimination_band": "消去計算を行う帯の幅",
    "endpoint": "端点の頂点番号",
    "hash_function": "値のハッシュを計算する関数",
    "heavy": "重い辺・子として扱う対象",
    "imag": "複素数の虚部",
    "include_same": "同じ値も結果に含めるか",
    "increasing_slopes": "傾きを昇順で追加するか",
    "insert": "要素を挿入するときに呼ぶ関数",
    "internal": "内部表現のまま扱うか",
    "interner": "同じ構造へ同じ番号を割り当てる管理オブジェクト",
    "inward": "内向きの辺として処理するか",
    "layer": "対象の層番号",
    "mask": "ビットマスク",
    "limits": "各変数・次元の上限を並べた列",
    "one_indexed": "1始まりの番号として扱うか",
    "parts": "分割した各部分を並べた列",
    "path": "頂点または辺を順に並べた経路",
    "postorder": "帰りがけ順で返すか",
    "prefix_g": "関数 g の接頭部分を並べた列",
    "prefix_h": "関数 h の接頭部分を並べた列",
    "primitive_root": "法に対する原始根",
    "profit_one": "状態1を選ぶ利益",
    "profit_zero": "状態0を選ぶ利益",
    "profits": "各選択肢の利益を並べた列",
    "propose": "次の候補状態を作る関数",
    "rake_backward": "逆向きに部分木情報を併合する関数",
    "rake_forward": "順向きに部分木情報を併合する関数",
    "real": "複素数の実部",
    "reduced": "簡約した形まで計算するか",
    "reset": "状態を初期状態へ戻す関数",
    "return_argmax": "最大値の位置も返すか",
    "return_argmin": "最小値の位置も返すか",
    "rollback": "直前の状態へ戻す関数",
    "root1": "1つ目の木の根の頂点番号",
    "root2": "2つ目の木の根の頂点番号",
    "row_base": "行番号に加える基準値",
    "shape": "各次元の大きさ",
    "signature": "子構造の種類を並べた識別用の列",
    "sizes": "各グループ・次元の大きさを並べた列",
    "snapshot": "復元先を示すスナップショット番号",
    "sort_edges": "辺を並べ替えてから処理するか",
    "state_max": "状態番号の上限",
    "turns": "繰り返す手数・回数",
    "x_limit": "x方向の上限",
    "y_limit": "y方向の上限",
    "zero_indexed": "0始まりの番号として扱うか",
})


def friendly_argument_description(name, description, symbol_name):
    plain = name.lstrip("*")
    default = ""
    default_match = re.search(r"。省略時: (.+)$", description)
    if default_match:
        default = f"。省略時は {default_match.group(1)}"
        description = description[: default_match.start()]
    if plain == "value":
        if re.search(r"add|append|push", symbol_name):
            description = "加える値"
        elif re.search(r"set|update|assign", symbol_name):
            description = "新しく設定する値"
        else:
            description = "処理対象の値"
    elif plain == "target":
        if re.search(r"bound|search|bisect", symbol_name):
            description = "探す基準値"
        else:
            description = "処理の対象"
    elif plain in ("identity", "e"):
        description = "まとめる関数の単位元"
    elif plain in FRIENDLY_ARGUMENTS:
        description = FRIENDLY_ARGUMENTS[plain]
    elif "APIの文脈に従う" in description:
        if plain.endswith(("_count", "_length")):
            description = "処理対象の個数"
        elif plain.endswith(("_index", "_position")):
            description = "位置番号（0始まり）"
        elif plain.startswith(("is_", "has_", "use_", "with_")):
            description = "この機能を有効にするか"
        elif re.search(r"(?:add|remove|merge|query|update|calculate|get|put)", plain):
            description = "処理時に呼び出す関数"
        elif plain.endswith(("values", "options", "groups")):
            description = "処理対象を並べた列"
        elif plain.endswith("value"):
            description = "処理対象の値"
        elif plain.endswith(("size", "width", "height")):
            description = "処理対象の大きさ"
        else:
            description = f"{plain} として使う値"
    return localize_prose(description.rstrip("。") + default)


def parse_argument_details(raw_value, symbol_name):
    cleaned = clean_markdown(raw_value)
    if cleaned in ("", "なし", "同じ"):
        return []
    result = []
    for part in re.split(r"<br\s*/?>", html.unescape(raw_value)):
        part = clean_markdown(part)
        match = re.match(r"([^:]+):\s*(.+)", part)
        if match:
            name, description = match.groups()
            result.append(
                {
                    "name": name,
                    "description": friendly_argument_description(name, description, symbol_name),
                }
            )
        elif part:
            result.append({"name": "値", "description": localize_prose(part)})
    return result


def friendly_purpose(symbol_name, description, argument_details):
    description = clean_markdown(description).replace(
        "詳細はclass/moduleの説明に従う。", ""
    ).strip()
    names = {item["name"].lstrip("*") for item in argument_details}
    if symbol_name in ("add", "range_add") and {"left", "right", "value"} <= names:
        return "範囲 [left, right) の各要素に value を加える。"
    if symbol_name == "add" and {"index", "value"} <= names:
        return "index の値に value を加える。"
    if symbol_name in ("sum", "prod") and {"left", "right"} <= names:
        return "範囲 [left, right) を集計して返す。"
    if symbol_name in ("prefix_sum", "sum0") and "right" in names:
        return "範囲 [0, right) の総和を返す。"
    if symbol_name == "get" and "index" in names:
        return "index にある値を返す。"
    if symbol_name in ("set", "update") and {"index", "value"} <= names:
        return "index の値を value に置き換える。"
    if symbol_name in ("lower_bound", "bisect_left") and "target" in names:
        return "累積値が target 以上になる最初の位置を返す。"
    protocol_purposes = {
        "__add__": "加算した結果を返す。",
        "__radd__": "左右を入れ替えて加算した結果を返す。",
        "__sub__": "減算した結果を返す。",
        "__rsub__": "左右を入れ替えて減算した結果を返す。",
        "__mul__": "乗算した結果を返す。",
        "__rmul__": "左右を入れ替えて乗算した結果を返す。",
        "__truediv__": "除算した結果を返す。",
        "__floordiv__": "切り捨て除算した結果を返す。",
        "__mod__": "剰余を返す。",
        "__pow__": "累乗した結果を返す。",
        "__neg__": "符号を反転した結果を返す。",
        "__eq__": "2つの値が等しいか判定する。",
        "__lt__": "大小関係を判定する。",
        "__le__": "大小関係を判定する。",
        "__hash__": "ハッシュ値を返す。",
        "__repr__": "デバッグ表示用の文字列を返す。",
        "__str__": "文字列表現を返す。",
        "__iter__": "要素を順に走査するイテレータを返す。",
        "__next__": "次の要素を返す。",
        "__getitem__": "指定した位置の値を返す。",
        "__setitem__": "指定した位置の値を更新する。",
        "__contains__": "指定した値が含まれるか判定する。",
        "__len__": "要素数を返す。",
        "__bool__": "真偽値へ変換する。",
    }
    if symbol_name in protocol_purposes:
        return protocol_purposes[symbol_name]
    return localize_prose(description)


def infer_return_format(value, symbol_name, owner, source_formats):
    exact = source_formats.get((owner, symbol_name), "")
    cleaned = clean_markdown(value)
    lower = symbol_name.lower()
    if lower in ("__len__", "length", "size", "count"):
        return "int"
    if lower in ("lower_bound", "upper_bound", "bisect_left", "bisect_right", "rank", "kth"):
        return "int"
    if lower in ("__bool__", "same", "connected", "empty", "contains") or lower.startswith(("is_", "has_", "can_")):
        return "bool"
    if lower == "__iter__" or "iterator" in cleaned.lower():
        return "iterator"
    if exact and exact != "None":
        parts = [part.strip() for part in exact.split("/") if part.strip()]
        if "int" in parts and "float" in parts:
            parts = [part for part in parts if part not in ("int", "float")]
            parts.insert(0, "int / float")
        return " / ".join(dict.fromkeys(parts))
    checks = (
        (r"None", "None"),
        (r"bool", "bool"),
        (r"dict", "dict"),
        (r"set", "set"),
        (r"iterator", "iterator"),
        (r"list|列（list", "list"),
        (r"tuple", "tuple"),
        (r"float", "float"),
        (r"int|整数", "int"),
        (r"\.join\(", "str"),
        (r"instance", "class instance"),
        (r"入力要素型", "入力要素と同じ型"),
    )
    formats = [label for pattern, label in checks if re.search(pattern, cleaned, re.IGNORECASE)]
    if formats:
        return " / ".join(dict.fromkeys(formats))
    if lower in ("get", "__getitem__", "kth", "min", "max", "pop", "top", "peek", "front", "next"):
        return "格納値と同じ型"
    if re.search(r"(?:convolution|polynomial|fps_|series|transform|bucket_sort|row$)", lower):
        return "list"
    if re.search(r"(?:fibonacci|popcount|power|leader|root|components|position|index)", lower):
        return "int"
    if re.search(r"(?:sum|prod|fold|query|min|max)", lower):
        return "集計値（要素型と演算に依存）"
    return "計算結果（入力型に依存）"


def friendly_return_description(symbol_name, value, return_format):
    cleaned = clean_markdown(value)
    lower = symbol_name.lower()
    words = set(lower.strip("_").split("_"))
    instance_match = re.fullmatch(r"([A-Za-z_]\w*) instance(?:\s*/\s*None)?", cleaned)
    if instance_match:
        description = f"{instance_match.group(1)} のインスタンス。"
        if cleaned.endswith("None"):
            description += "該当する結果がない場合は None。"
        return description
    if return_format.startswith("list["):
        if {"sort", "order", "permutation", "indices"} & words:
            return "要素または元の添字を、結果の順序に並べたリスト。"
        if {"transform", "zeta", "mobius", "butterfly"} & words:
            return "入力と同じ添字に対応する、変換後の値を格納したリスト。"
        if {"convolution", "polynomial", "fps", "series"} & words:
            return "定数項から昇冪順に係数を格納したリスト。"
        if {"path", "vertices"} & words:
            return "経路上の頂点番号を順に格納したリスト。"
        if "edges" in words:
            return "条件を満たす辺を格納したリスト。"
        if "components" in words:
            return "連結成分ごとの頂点または成分IDを格納したリスト。"
        if cleaned not in ("list", "値のlist", "上記の処理結果。") and not re.search(r"[()\[\]]", cleaned):
            return cleaned
        return "このAPIの結果を呼び出し順・添字順に格納したリスト。"
    if return_format.startswith("dict["):
        if {"count", "frequency", "factor"} & words:
            return "keyが対象値、valueがその個数または指数の辞書。"
        return "keyが入力中の識別対象、valueが対応する計算結果の辞書。"
    if return_format.startswith("set["):
        return "条件を満たす重複のない要素集合。"
    if return_format.startswith("iterator["):
        if {"mask", "submasks", "supermasks"} & words:
            return "条件を満たすビットマスクを1つずつ返すiterator。"
        return "このAPIの結果要素を1つずつ返すiterator。"
    if return_format == "None":
        return "値は返さない。対象を直接更新する。"
    if lower in ("__len__", "size", "length"):
        return "要素数。"
    if lower in ("same", "connected", "empty", "contains") or lower.startswith(("is_", "has_", "can_")):
        return "条件を満たすかどうか。"
    if lower in ("sum", "prod", "prefix_sum", "fold", "query"):
        return "指定した範囲の集計結果。"
    if lower in ("get", "__getitem__"):
        return "指定した位置または対象に格納されている値。"
    if lower in ("lower_bound", "upper_bound", "bisect_left", "bisect_right"):
        return "条件を満たす最初の位置。見つからない場合はデータ構造の末尾（要素数）。"
    if "encode" in lower:
        return "エンコードした結果。"
    if "decode" in lower:
        return "復元した結果。"
    if "convolution" in lower or re.search(r"(?:^|_)fps(?:_|$)|polynomial|series", lower):
        return "計算後の係数列。"
    if lower == "fibonacci":
        return "index 番目のフィボナッチ数。"
    if lower == "popcount":
        return "2進表現で 1 になっているビットの個数。"
    if lower in ("leader", "root", "find"):
        return "所属する成分の代表番号。"
    if cleaned == "同じ":
        return "別名になっているAPIと同じ値。"
    if re.search(r"\bself\.|\bcls\(|\w+\([^)]*\)|\[[^]]*\]", cleaned):
        return "上記の処理結果。"
    ascii_letters = sum(character.isascii() and character.isalpha() for character in cleaned)
    japanese = sum("ぁ" <= character <= "ん" or "ァ" <= character <= "ン" or "一" <= character <= "龯" for character in cleaned)
    if ascii_letters > japanese * 2 and len(cleaned) > 24:
        return "上記の処理結果。"
    if cleaned in ("値", "計算結果", "結果"):
        return "上記の処理結果。"
    return cleaned


def enrich_container_format(return_format, symbol_name):
    if return_format not in ("list", "dict", "set", "iterator"):
        return return_format
    words = set(symbol_name.lower().strip("_").split("_"))
    if return_format == "list":
        if {"index", "indices", "order", "permutation", "vertices", "path"} & words:
            return "list[int]"
        if {"transform", "zeta", "mobius", "butterfly", "convolution", "polynomial", "fps", "series"} & words:
            return "list[number]"
        return "list[object]"
    if return_format == "dict":
        return "dict[object, object]"
    if return_format == "set":
        return "set[object]"
    return "iterator[object]"


def normalize_return_format(return_format):
    """Keep the format column type-like instead of mixing in English prose."""
    match = re.fullmatch(r"([A-Za-z_]\w*) instance(?:\s*/\s*None)?", return_format)
    if match:
        return f"{match.group(1)} | None" if return_format.endswith("None") else match.group(1)
    return "object" if return_format == "class instance" else return_format


CONSTANT_TIME_NAMES = {
    "__bool__",
    "__enter__",
    "__exit__",
    "__len__",
    "all_prod",
    "empty",
}

LINEAR_TIME_NAMES = {
    "__iter__",
    "dump",
    "items",
    "keys",
    "to_list",
    "tolist",
    "values",
}

QUERY_NAMES = re.compile(
    r"(?:get|query|prod|sum|find|same|connected|kth|rank|count|lcp|distance|jump|"
    r"lower_bound|upper_bound|contains|search|minimum|maximum|argmin|argmax|fold)"
)
UPDATE_NAMES = re.compile(
    r"(?:add|set|update|apply|insert|erase|remove|delete|unite|merge|link|cut|"
    r"push|pop|append|assign|affine|chmin|chmax)"
)


def complexity_clauses(value):
    return [part.strip() for part in re.split(r"\s*[、/]\s*", value) if part.strip()]


def infer_complexity(
    name,
    owner,
    module_complexity,
    documented,
    class_documented,
    module_key,
    complexity_overrides,
):
    override_key = f"{owner}.{name}" if owner else name
    exact_override = complexity_overrides.get(module_key, {}).get(override_key)
    if exact_override:
        return exact_override
    exact = documented.get((owner, name))
    if exact:
        return exact
    if name in CONSTANT_TIME_NAMES:
        return "O(1)"
    if name in LINEAR_TIME_NAMES or name.startswith(("to_list", "enumerate_")):
        return "O(N) または出力サイズに線形"

    hint = class_documented.get(owner, "") if owner else ""
    if not hint:
        hint = module_complexity
    clauses = complexity_clauses(hint)

    preferences = []
    lowered = name.lower()
    if name == "__init__":
        preferences = ["構築", "前計算", "初期化"]
    elif lowered in ("undo", "rollback"):
        preferences = ["undo", "rollback"]
    elif owner and "2D" in owner:
        preferences = ["2D", "HW", "H", "W"]
    elif QUERY_NAMES.search(lowered):
        preferences = ["クエリ", "query", "取得", "検索", "比較", "距離", "移動", "LCP"]
    elif UPDATE_NAMES.search(lowered):
        preferences = ["更新", "追加", "編集", "併合", "unite", "操作"]

    for preference in preferences:
        for clause in clauses:
            if preference.lower() in clause.lower():
                return concise_complexity(clause)
    return concise_complexity(hint) if hint else "実装依存"


def apply_api_detail(item, module_key, owner):
    detail = api_detail(module_key, owner, item["name"])
    description = detail.get("description")
    if description:
        description = clean_markdown(description)
        item["summary"] = description
        item["description"] = description
    return_format = detail.get("returnFormat")
    if return_format:
        item["returnFormat"] = clean_markdown(return_format)
    return_description = detail.get("returnDescription")
    if return_description:
        item["returnDescription"] = clean_markdown(return_description)
    if return_format or return_description:
        item["returns"] = " — ".join(
            value
            for value in (
                item["returnFormat"],
                item["returnDescription"],
            )
            if value
        )
    parts = detail.get("returnParts")
    if parts:
        item["returnParts"] = [
            {
                "name": clean_markdown(part["name"]),
                "format": clean_markdown(part["format"]),
                "description": clean_markdown(part["description"]),
            }
            for part in parts
        ]
    return item


def table_symbols(
    section,
    kind,
    owner,
    module_complexity,
    documented,
    class_documented,
    source_formats,
    module_key,
    complexity_overrides,
):
    result = []
    for line in section.splitlines():
        if not line.startswith("| [`"):
            continue
        signature_match = re.search(r"\[`([^`]+)`\]", line)
        if signature_match is None:
            continue
        cells = split_markdown_row(line)
        if kind == "function":
            row_kind = "function"
            description_index, arguments_index, returns_index = 1, 2, 3
        else:
            row_kind = clean_markdown(cells[1]) if len(cells) > 1 else "method"
            description_index, arguments_index, returns_index = 2, 3, 4
        signature = signature_match.group(1)
        symbol_name = signature.split("(", 1)[0]
        source_line_match = re.search(r"#L(\d+)", cells[0])
        arguments_value = cells[arguments_index] if len(cells) > arguments_index else ""
        returns_value = cells[returns_index] if len(cells) > returns_index else ""
        argument_details = parse_argument_details(arguments_value, symbol_name)
        structured_return = clean_markdown(returns_value).split(" — ", 1)
        return_format = (
            structured_return[0]
            if len(structured_return) == 2
            else infer_return_format(
                returns_value,
                symbol_name,
                owner,
                source_formats,
            )
        )
        return_format = normalize_return_format(
            enrich_container_format(return_format, symbol_name)
        )
        return_description = (
            structured_return[1]
            if len(structured_return) == 2
            else friendly_return_description(symbol_name, returns_value, return_format)
        )
        return_description = re.sub(
            r"\s*/\s*(?:list|dict|set|iterator)\[[^]]+\]\s*—\s*計算結果$",
            "",
            return_description,
        )
        return_description = localize_prose(return_description)
        description = friendly_purpose(
            symbol_name,
            cells[description_index] if len(cells) > description_index else "",
            argument_details,
        )
        item = {
                "name": symbol_name,
                "kind": row_kind,
                "signature": signature,
                "summary": description,
                "description": description,
                "searchTerms": symbol_search_terms(
                    module_key,
                    symbol_name,
                    signature,
                    description,
                ),
                "arguments": clean_markdown(arguments_value),
                "argumentDetails": argument_details,
                "returns": clean_markdown(returns_value),
                "returnFormat": return_format,
                "returnDescription": return_description,
                "complexity": infer_complexity(
                    symbol_name,
                    owner,
                    module_complexity,
                    documented,
                    class_documented,
                    module_key,
                    complexity_overrides,
                ),
                "sourceLine": int(source_line_match.group(1)) if source_line_match else None,
            }
        result.append(apply_api_detail(item, module_key, owner))
    return result


def resolve_alias_complexities(symbols):
    by_name = {
        item["signature"].split("(", 1)[0]: item
        for item in symbols
        if item["kind"] != "alias"
    }
    for item in symbols:
        if item["kind"] != "alias":
            continue
        match = re.search(r"([^ ]+) の別名", item["description"])
        if match and match.group(1) in by_name:
            target = by_name[match.group(1)]
            item["complexity"] = target["complexity"]
            item["argumentDetails"] = target["argumentDetails"]
            item["arguments"] = target["arguments"]
            item["returns"] = target["returns"]
            item["returnFormat"] = target["returnFormat"]
            item["returnDescription"] = target["returnDescription"]


def section_after(text, heading):
    marker = f"## {heading}\n"
    if marker not in text:
        return ""
    section = text.split(marker, 1)[1]
    return re.split(r"\n## ", section, maxsplit=1)[0]


def parse_module(path, category, library_root, complexity_overrides):
    text = path.read_text(encoding="utf-8")
    module_match = re.search(r"^# `([^`]+)`", text, re.MULTILINE)
    if module_match is None:
        raise ValueError(f"missing module title: {path}")
    module_path = module_match.group(1)
    name = module_path.rsplit(".", 1)[-1]
    relative_key = f"{category}/{name}.py"
    after_title = text[module_match.end() :].strip()
    summary = next(
        line.strip()
        for line in after_title.splitlines()
        if line.strip() and not line.startswith("-")
    )
    complexity_match = re.search(r"^- 計算量の目安: (.+)$", text, re.MULTILINE)
    count_match = re.search(
        r"^- 公開API: function (\d+)、class (\d+)、method/property (\d+)",
        text,
        re.MULTILINE,
    )
    import_match = re.search(r"## Import\n\n```python\n(.*?)\n```", text, re.DOTALL)
    capabilities = [
        clean_markdown(line[2:])
        for line in section_after(text, "できること").splitlines()
        if line.startswith("- ")
    ]

    module_complexity = clean_complexity(complexity_match.group(1)) if complexity_match else "実装依存"
    source_path = library_root / category / f"{name}.py"
    standalone_code, bundled_dependencies = build_standalone_code(source_path, library_root)
    validate_standalone_code(standalone_code, source_path)
    documented, class_documented = source_complexities(source_path)
    source_formats = source_return_formats(source_path)
    symbols = table_symbols(
        section_after(text, "Functions"),
        "function",
        None,
        module_complexity,
        documented,
        class_documented,
        source_formats,
        relative_key,
        complexity_overrides,
    )
    classes = []
    class_matches = list(re.finditer(r"^## Class `([^`]+)`\n", text, re.MULTILINE))
    for index, match in enumerate(class_matches):
        end = class_matches[index + 1].start() if index + 1 < len(class_matches) else len(text)
        segment = text[match.end() : end]
        segment = re.split(r"\n## Module aliases", segment, maxsplit=1)[0]
        description = next(
            (
                line.strip()
                for line in segment.splitlines()
                if line.strip() and not line.startswith("-") and not line.startswith("|")
            ),
            "",
        )
        constructor_match = re.search(r"^- constructor: \[`([^`]+)`\]", segment, re.MULTILINE)
        constructor_line_match = re.search(r"^- constructor: .*?#L(\d+)\)", segment, re.MULTILINE)
        arguments_match = re.search(r"^- 引数: (.+)$", segment, re.MULTILINE)
        returns_match = re.search(r"^- 返り値: (.+)$", segment, re.MULTILINE)
        creates_match = re.search(r"^- 作成後: (.+)$", segment, re.MULTILINE)
        methods = table_symbols(
            segment,
            "method",
            match.group(1),
            module_complexity,
            documented,
            class_documented,
            source_formats,
            relative_key,
            complexity_overrides,
        )
        resolve_alias_complexities(methods)
        configured_class = class_detail(relative_key, match.group(1))
        configured_description = configured_class.get("description")
        class_description = (
            clean_markdown(configured_description)
            if configured_description
            else localize_class_description(match.group(1), description)
        )
        constructor_creates = configured_class.get("constructorCreates") or (
            clean_markdown(creates_match.group(1))
            if creates_match
            else class_description
        )
        constructor_creates = clean_markdown(constructor_creates)
        classes.append(
            {
                "name": match.group(1),
                "summary": class_description,
                "description": class_description,
                "searchTerms": symbol_search_terms(
                    relative_key,
                    match.group(1),
                    constructor_match.group(1) if constructor_match else match.group(1),
                    class_description,
                ),
                "constructor": constructor_match.group(1) if constructor_match else match.group(1),
                "constructorArguments": clean_markdown(arguments_match.group(1)) if arguments_match else "なし",
                "constructorArgumentDetails": parse_argument_details(
                    arguments_match.group(1) if arguments_match else "なし",
                    "__init__",
                ),
                "constructorReturns": clean_markdown(returns_match.group(1)) if returns_match else f"{match.group(1)} のインスタンス",
                "constructorReturnFormat": match.group(1),
                "constructorReturnDescription": constructor_creates,
                "constructorCreates": constructor_creates,
                "constructorComplexity": infer_complexity(
                    "__init__",
                    match.group(1),
                    module_complexity,
                    documented,
                    class_documented,
                    relative_key,
                    complexity_overrides,
                ),
                "constructorSourceLine": int(constructor_line_match.group(1)) if constructor_line_match else None,
                "methods": methods,
            }
        )

    localized_summary = localize_prose(summary)
    localized_capabilities = [localize_capability(item) for item in capabilities]
    if not localized_capabilities:
        localized_capabilities = [localized_summary]
    module_search_terms = unique_search_terms(
        identifier_search_terms(name),
        identifier_search_terms(module_path),
        (relative_key, CATEGORY_LABELS[category]),
        SEARCH_TERMS_BY_MODULE.get(relative_key, ()),
    )
    return {
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "domain": CATEGORY_DOMAINS[category],
        "domainLabel": DOMAIN_LABELS[CATEGORY_DOMAINS[category]],
        "name": name,
        "modulePath": module_path,
        "summary": localized_summary,
        "capabilities": localized_capabilities,
        "searchTerms": module_search_terms,
        "complexity": module_complexity,
        "sourcePath": f"library_codex/{category}/{name}.py",
        "inputFingerprint": module_input_fingerprint(source_path, path, library_root),
        "importCode": import_match.group(1).strip() if import_match else f"from {module_path} import *",
        "sourceCode": source_path.read_text(encoding="utf-8").rstrip() + "\n",
        "standaloneCode": standalone_code,
        "bundledDependencies": bundled_dependencies,
        "counts": {
            "functions": int(count_match.group(1)) if count_match else len(symbols),
            "classes": int(count_match.group(2)) if count_match else len(classes),
            "methods": int(count_match.group(3)) if count_match else sum(len(item["methods"]) for item in classes),
        },
        "functions": symbols,
        "classes": classes,
    }


def module_key_from_changed_path(value):
    parts = str(value).replace("\\", "/").split("/")
    if parts and parts[0] == ".":
        parts = parts[1:]
    if parts and parts[0] == "library_codex":
        parts = parts[1:]
    if len(parts) == 2 and parts[0] in CATEGORY_LABELS and parts[1].endswith(".py"):
        if not parts[1].startswith("_"):
            return (parts[0], parts[1][:-3])
    if (
        len(parts) == 4
        and parts[:2] == ["docs", "api"]
        and parts[2] in CATEGORY_LABELS
        and parts[3].endswith(".md")
        and parts[3] != "README.md"
    ):
        return (parts[2], parts[3][:-3])
    if (
        len(parts) == 5
        and parts[0] == "library_codex"
        and parts[1:3] == ["docs", "api"]
        and parts[3] in CATEGORY_LABELS
        and parts[4].endswith(".md")
        and parts[4] != "README.md"
    ):
        return (parts[3], parts[4][:-3])
    return None


def imported_module_keys(source_path):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    result = set()
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        for module_name in names:
            parts = module_name.split(".")
            if parts and parts[0] == "library_codex":
                parts = parts[1:]
            if len(parts) >= 2 and parts[0] in CATEGORY_LABELS:
                result.add((parts[0], parts[1]))
    return result


def source_module_paths(library_root):
    return {
        (category, path.stem): path
        for category in CATEGORY_LABELS
        for path in sorted((library_root / category).glob("*.py"))
        if not path.name.startswith("_")
        and f"{category}/{path.name}" not in COMPATIBILITY_MODULES
    }


def hash_paths(paths, base):
    digest = hashlib.sha256()
    for path in sorted(set(paths), key=lambda item: item.as_posix()):
        relative = path.resolve().relative_to(base.resolve()).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def catalog_input_stamp(paths, base):
    digest = hashlib.sha256()
    for path in sorted(set(paths), key=lambda item: item.as_posix()):
        relative = path.resolve().relative_to(base.resolve()).as_posix()
        stat = path.stat()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(b":")
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def module_metadata_payload(module_key):
    return {
        "searchTerms": SEARCH_TERMS_BY_MODULE.get(module_key, ()),
        "symbolSearchTerms": [
            [symbol_name, terms]
            for (path, symbol_name), terms in sorted(
                SEARCH_TERMS_BY_SYMBOL.items()
            )
            if path == module_key
        ],
        "apiDetails": [
            [owner, symbol_name, detail]
            for (path, owner, symbol_name), detail in sorted(
                API_DETAILS_BY_SYMBOL.items(),
                key=lambda item: (
                    item[0][0], item[0][1] or "", item[0][2]
                ),
            )
            if path == module_key
        ],
        "classDetails": [
            [class_name, detail]
            for (path, class_name), detail in sorted(
                CLASS_DETAILS_BY_SYMBOL.items()
            )
            if path == module_key
        ],
        "complexity": COMPLEXITY_BY_MODULE.get(module_key, {}),
    }


def module_input_fingerprint(source_path, document_path, library_root):
    module_key = source_path.relative_to(library_root).as_posix()
    digest = hashlib.sha256()
    digest.update(
        hash_paths((source_path, document_path), library_root.parent).encode(
            "ascii"
        )
    )
    digest.update(b"\0")
    digest.update(
        json.dumps(
            module_metadata_payload(module_key),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    return digest.hexdigest()


def generator_input_paths(library_root):
    return (
        Path(__file__).resolve(),
        library_root / "tools" / "category_config.py",
    )


def metadata_input_paths(library_root):
    return (library_root / "tools" / "api_metadata.py",)


def catalog_input_paths(library_root, documents=None):
    documents = documents or api_documents(library_root / "docs" / "api")
    return (
        tuple(source_module_paths(library_root).values())
        + tuple(documents.values())
        + generator_input_paths(library_root)
        + metadata_input_paths(library_root)
        + (library_root / "README.md",)
    )


def public_symbol_names(source_path):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    result = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                result.add(node.name)
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not child.name.startswith("_") or child.name in {
                        "__call__", "__contains__", "__getitem__", "__iter__",
                        "__len__", "__repr__", "__setitem__", "__str__",
                    }:
                        result.add(child.name)
    return result


def validate_term_sequence(owner, terms):
    if not isinstance(terms, (tuple, list)):
        raise ValueError(f"search terms for {owner} must be a tuple or list")
    normalized = []
    for term in terms:
        if not isinstance(term, str) or not term.strip():
            raise ValueError(f"empty search term for {owner}")
        normalized.append(term.strip().casefold())
    duplicates = sorted(term for term, count in Counter(normalized).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate search terms for {owner}: {duplicates}")


def validate_search_metadata(library_root):
    paths = source_module_paths(library_root)
    known_modules = {f"{category}/{name}.py" for category, name in paths}
    paths_by_module = {
        f"{category}/{name}.py": path
        for (category, name), path in paths.items()
    }
    symbols = {}
    for module_key, terms in SEARCH_TERMS_BY_MODULE.items():
        if module_key not in known_modules:
            raise ValueError(f"unknown module in SEARCH_TERMS_BY_MODULE: {module_key}")
        validate_term_sequence(module_key, terms)
    for key, terms in SEARCH_TERMS_BY_SYMBOL.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError(f"invalid SEARCH_TERMS_BY_SYMBOL key: {key!r}")
        module_key, symbol_name = key
        if module_key not in known_modules:
            raise ValueError(f"unknown module in SEARCH_TERMS_BY_SYMBOL: {module_key}")
        if module_key not in symbols:
            symbols[module_key] = public_symbol_names(paths_by_module[module_key])
        if symbol_name not in symbols[module_key]:
            raise ValueError(
                f"unknown symbol in SEARCH_TERMS_BY_SYMBOL: {module_key}:{symbol_name}"
            )
        validate_term_sequence(f"{module_key}:{symbol_name}", terms)


def public_api_structure(source_path):
    tree = ast.parse(
        source_path.read_text(encoding="utf-8"), filename=str(source_path)
    )
    functions = set()
    classes = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.add(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            methods = set()
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not child.name.startswith("_") or child.name in {
                        "__call__", "__contains__", "__getitem__", "__iter__",
                        "__len__", "__repr__", "__setitem__", "__str__",
                    }:
                        methods.add(child.name)
            classes[node.name] = methods
    return functions, classes


def validate_nonempty_text(owner, field, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"empty {field} for {owner}")


def validate_api_details_metadata(library_root):
    paths = source_module_paths(library_root)
    paths_by_module = {
        f"{category}/{name}.py": path
        for (category, name), path in paths.items()
    }
    structures = {}

    def structure(module_key, dictionary_name):
        if module_key not in paths_by_module:
            raise ValueError(
                f"unknown module in {dictionary_name}: {module_key}"
            )
        if module_key not in structures:
            structures[module_key] = public_api_structure(
                paths_by_module[module_key]
            )
        return structures[module_key]

    allowed_api_fields = {
        "description", "returnFormat", "returnDescription", "returnParts",
    }
    for key, detail in API_DETAILS_BY_SYMBOL.items():
        if not isinstance(key, tuple) or len(key) != 3:
            raise ValueError(f"invalid API_DETAILS_BY_SYMBOL key: {key!r}")
        module_key, owner, symbol_name = key
        functions, classes = structure(module_key, "API_DETAILS_BY_SYMBOL")
        known = functions if owner is None else classes.get(owner)
        if known is None or symbol_name not in known:
            raise ValueError(
                "unknown symbol in API_DETAILS_BY_SYMBOL: "
                f"{module_key}:{owner}.{symbol_name}"
            )
        if not isinstance(detail, dict):
            raise ValueError(f"API details must be a dict: {key!r}")
        unknown = set(detail) - allowed_api_fields
        if unknown:
            raise ValueError(f"unknown API detail fields for {key!r}: {sorted(unknown)}")
        for field in ("description", "returnFormat", "returnDescription"):
            if field in detail:
                validate_nonempty_text(key, field, detail[field])
        parts = detail.get("returnParts", ())
        if not isinstance(parts, (tuple, list)):
            raise ValueError(f"returnParts must be a tuple or list: {key!r}")
        names = []
        for part in parts:
            if not isinstance(part, dict):
                raise ValueError(f"return part must be a dict: {key!r}")
            if set(part) != {"name", "format", "description"}:
                raise ValueError(f"invalid return part fields: {key!r}")
            for field in ("name", "format", "description"):
                validate_nonempty_text(key, f"returnParts.{field}", part[field])
            names.append(part["name"].strip().casefold())
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate return part names: {key!r}")

    allowed_class_fields = {"description", "constructorCreates"}
    for key, detail in CLASS_DETAILS_BY_SYMBOL.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError(f"invalid CLASS_DETAILS_BY_SYMBOL key: {key!r}")
        module_key, class_name = key
        _, classes = structure(module_key, "CLASS_DETAILS_BY_SYMBOL")
        if class_name not in classes:
            raise ValueError(
                "unknown class in CLASS_DETAILS_BY_SYMBOL: "
                f"{module_key}:{class_name}"
            )
        if not isinstance(detail, dict):
            raise ValueError(f"class details must be a dict: {key!r}")
        unknown = set(detail) - allowed_class_fields
        if unknown:
            raise ValueError(
                f"unknown class detail fields for {key!r}: {sorted(unknown)}"
            )
        for field, value in detail.items():
            validate_nonempty_text(key, field, value)


SYMBOL_REQUIRED_FIELDS = {
    "name", "signature", "summary", "description", "searchTerms",
    "arguments", "returns", "returnFormat", "returnDescription",
    "complexity", "sourceLine",
}


def validate_catalog_return_details(owner, symbol):
    validate_nonempty_text(owner, "returnFormat", symbol["returnFormat"])
    validate_nonempty_text(
        owner, "returnDescription", symbol["returnDescription"]
    )
    parts = symbol.get("returnParts")
    if parts is None:
        return
    if not isinstance(parts, list):
        raise ValueError(f"catalog returnParts must be a list: {owner}")
    names = []
    for part in parts:
        if not isinstance(part, dict):
            raise ValueError(f"catalog return part must be a dict: {owner}")
        if set(part) != {"name", "format", "description"}:
            raise ValueError(f"invalid catalog return part fields: {owner}")
        for field in ("name", "format", "description"):
            validate_nonempty_text(owner, f"returnParts.{field}", part[field])
        names.append(part["name"].strip().casefold())
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate catalog return part names: {owner}")


def validate_catalog(data, library_root):
    if data.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"unsupported catalog schemaVersion: {data.get('schemaVersion')!r}")
    for key in (
        "generatedAt", "sourceRevision", "sourceFingerprint", "inputStamp", "stats",
        "categories", "modules",
    ):
        if key not in data:
            raise ValueError(f"catalog is missing {key}")
    modules = data["modules"]
    if not isinstance(modules, list):
        raise ValueError("catalog modules must be a list")
    expected_paths = {
        f"library_codex/{category}/{name}.py"
        for category, name in source_module_paths(library_root)
    }
    actual_paths = {module.get("sourcePath") for module in modules}
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        raise ValueError(f"catalog module mismatch; missing={missing[:3]}, extra={extra[:3]}")
    for module in modules:
        for key in (
            "name", "modulePath", "sourcePath", "category", "categoryLabel",
            "summary", "capabilities", "searchTerms", "importCode",
            "bundledDependencies", "sourceCode", "standaloneCode", "functions",
            "classes", "inputFingerprint",
        ):
            if key not in module:
                raise ValueError(f"catalog module {module.get('name')} is missing {key}")
        validate_term_sequence(module["modulePath"], module["searchTerms"])
        for symbol in module["functions"]:
            missing = SYMBOL_REQUIRED_FIELDS - set(symbol)
            if missing:
                raise ValueError(
                    f"catalog function {module['modulePath']}:{symbol.get('name')} "
                    f"is missing {sorted(missing)}"
                )
            validate_term_sequence(
                f"{module['modulePath']}:{symbol['name']}", symbol["searchTerms"]
            )
            validate_catalog_return_details(
                f"{module['modulePath']}:{symbol['name']}", symbol
            )
        for class_item in module["classes"]:
            for key in (
                "name", "summary", "description", "searchTerms", "constructor",
                "constructorArgumentDetails", "constructorReturns",
                "constructorReturnFormat", "constructorReturnDescription",
                "constructorCreates", "constructorComplexity",
                "constructorSourceLine", "methods",
            ):
                if key not in class_item:
                    raise ValueError(
                        f"catalog class {module['modulePath']}:{class_item.get('name')} "
                        f"is missing {key}"
                    )
            validate_term_sequence(
                f"{module['modulePath']}:{class_item['name']}",
                class_item["searchTerms"],
            )
            validate_nonempty_text(
                f"{module['modulePath']}:{class_item['name']}",
                "constructorCreates",
                class_item["constructorCreates"],
            )
            for method in class_item["methods"]:
                missing = SYMBOL_REQUIRED_FIELDS - set(method)
                if missing:
                    raise ValueError(
                        f"catalog method {module['modulePath']}:{class_item['name']}."
                        f"{method.get('name')} is missing {sorted(missing)}"
                    )
                validate_term_sequence(
                    f"{module['modulePath']}:{class_item['name']}.{method['name']}",
                    method["searchTerms"],
                )
                validate_catalog_return_details(
                    f"{module['modulePath']}:{class_item['name']}."
                    f"{method['name']}",
                    method,
                )
    return data


def write_catalog_atomic(output, data, library_root):
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        parsed = json.loads(temporary.read_text(encoding="utf-8"))
        validate_catalog(parsed, library_root)
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()


def affected_module_keys(library_root, direct):
    paths = source_module_paths(library_root)
    dependencies = {
        key: imported_module_keys(path)
        for key, path in paths.items()
    }
    affected = set(direct)
    while True:
        added = {
            key for key, imported in dependencies.items()
            if key not in affected and imported & affected
        }
        if not added:
            return affected
        affected.update(added)


def api_documents(api_root):
    return {
        (category, path.stem): path
        for category in CATEGORY_LABELS
        for path in sorted((api_root / category).glob("*.md"))
        if path.name != "README.md"
    }


def changed_files_since(library_root, revision):
    completed = subprocess.run(
        ["git", "-C", str(library_root.parent), "diff", "--name-only", revision, "--"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or f"cannot diff {revision}")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def parse_selected_modules(documents, keys, library_root, complexity_overrides):
    return {
        key: parse_module(
            documents[key],
            key[0],
            library_root,
            complexity_overrides,
        )
        for key in sorted(keys)
        if key in documents
    }


def module_sort_key(module):
    category_order = {name: index for index, name in enumerate(CATEGORY_LABELS)}
    return (category_order[module["category"]], module["name"])


def category_rows(modules):
    result = []
    for category, label in CATEGORY_LABELS.items():
        selected = [module for module in modules if module["category"] == category]
        result.append(
            {
                "slug": category,
                "label": label,
                "domain": CATEGORY_DOMAINS[category],
                "domainLabel": DOMAIN_LABELS[CATEGORY_DOMAINS[category]],
                "modules": len(selected),
                "functions": sum(module["counts"]["functions"] for module in selected),
                "classes": sum(module["counts"]["classes"] for module in selected),
                "methods": sum(module["counts"]["methods"] for module in selected),
            }
        )
    return result


def load_configuration(library_root):
    global CATEGORY_LABELS, CATEGORY_DOMAINS, DOMAIN_LABELS
    global SEARCH_TERMS_BY_MODULE, SEARCH_TERMS_BY_SYMBOL
    global API_DETAILS_BY_SYMBOL, CLASS_DETAILS_BY_SYMBOL
    global COMPLEXITY_BY_MODULE
    category_config = runpy.run_path(
        str(library_root / "tools" / "category_config.py")
    )
    CATEGORY_LABELS = category_config["CATEGORY_LABELS"]
    CATEGORY_DOMAINS = category_config["CATEGORY_DOMAINS"]
    DOMAIN_LABELS = category_config["DOMAIN_LABELS"]
    metadata = runpy.run_path(str(library_root / "tools" / "api_metadata.py"))
    SEARCH_TERMS_BY_MODULE = metadata.get("SEARCH_TERMS_BY_MODULE", {})
    SEARCH_TERMS_BY_SYMBOL = metadata.get("SEARCH_TERMS_BY_SYMBOL", {})
    API_DETAILS_BY_SYMBOL = metadata.get("API_DETAILS_BY_SYMBOL", {})
    CLASS_DETAILS_BY_SYMBOL = metadata.get("CLASS_DETAILS_BY_SYMBOL", {})
    COMPLEXITY_BY_MODULE = metadata.get("COMPLEXITY_BY_MODULE", {})
    validate_search_metadata(library_root)
    validate_api_details_metadata(library_root)
    return COMPLEXITY_BY_MODULE


def catalog_fingerprints(library_root, documents):
    base = library_root.parent
    return (
        hash_paths(catalog_input_paths(library_root, documents), base),
        hash_paths(generator_input_paths(library_root), base),
    )


def build_catalog(library_root=ROOT, output=DEFAULT_OUTPUT, force_full=False):
    complexity_overrides = load_configuration(library_root)
    documents = api_documents(library_root / "docs" / "api")
    source_paths = source_module_paths(library_root)
    if set(documents) != set(source_paths):
        missing_docs = sorted(set(source_paths) - set(documents))
        stale_docs = sorted(set(documents) - set(source_paths))
        raise ValueError(
            f"API documents do not match source; missing={missing_docs[:3]}, "
            f"stale={stale_docs[:3]}"
        )
    previous = None
    if output.is_file():
        try:
            previous = json.loads(output.read_text(encoding="utf-8"))
            validate_catalog(previous, library_root)
        except (json.JSONDecodeError, ValueError):
            previous = None
    input_paths = catalog_input_paths(library_root, documents)
    input_stamp = catalog_input_stamp(input_paths, library_root.parent)
    if (
        previous is not None
        and not force_full
        and previous.get("inputStamp") == input_stamp
    ):
        return previous, 0
    source_fingerprint, generator_fingerprint = catalog_fingerprints(
        library_root, documents
    )

    previous_modules = {
        (module["category"], module["name"]): module
        for module in (previous or {}).get("modules", [])
    }
    full_invalidation = (
        force_full
        or previous is None
        or previous.get("generatorFingerprint") != generator_fingerprint
    )
    if full_invalidation:
        reparsed = set(documents)
    else:
        direct = set(documents) ^ set(previous_modules)
        for key in set(documents) & set(previous_modules):
            current = module_input_fingerprint(
                source_paths[key], documents[key], library_root
            )
            if previous_modules[key].get("inputFingerprint") != current:
                direct.add(key)
        reparsed = affected_module_keys(library_root, direct)

    modules_by_key = {
        key: module
        for key, module in previous_modules.items()
        if key in documents and key not in reparsed
    }
    modules_by_key.update(
        parse_selected_modules(
            documents,
            reparsed,
            library_root,
            complexity_overrides,
        )
    )
    if set(modules_by_key) != set(documents):
        missing = sorted(set(documents) - set(modules_by_key))
        raise ValueError(f"catalog generation is missing modules: {missing[:5]}")
    modules = sorted(modules_by_key.values(), key=module_sort_key)
    categories = category_rows(modules)
    domains = [
        {
            "slug": slug,
            "label": label,
            "modules": sum(
                category["modules"]
                for category in categories
                if category["domain"] == slug
            ),
        }
        for slug, label in DOMAIN_LABELS.items()
        if any(category["domain"] == slug for category in categories)
    ]
    data = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repository": "https://github.com/lif4635/harurun-s-library",
        "sourceRevision": source_revision(library_root),
        "sourceFingerprint": source_fingerprint,
        "inputStamp": input_stamp,
        "generatorFingerprint": generator_fingerprint,
        "stats": {
            "modules": len(modules),
            "functions": sum(module["counts"]["functions"] for module in modules),
            "classes": sum(module["counts"]["classes"] for module in modules),
            "methods": sum(module["counts"]["methods"] for module in modules),
            "tests": verified_test_count(library_root),
        },
        "categories": categories,
        "domains": domains,
        "modules": modules,
    }
    validate_catalog(data, library_root)
    return data, len(reparsed)


def check_catalog(library_root=ROOT, output=DEFAULT_OUTPUT):
    load_configuration(library_root)
    if not output.is_file():
        raise ValueError(f"catalog does not exist: {output}")
    data = json.loads(output.read_text(encoding="utf-8"))
    validate_catalog(data, library_root)
    documents = api_documents(library_root / "docs" / "api")
    input_stamp = catalog_input_stamp(
        catalog_input_paths(library_root, documents), library_root.parent
    )
    if data.get("inputStamp") == input_stamp:
        return data
    source_fingerprint, generator_fingerprint = catalog_fingerprints(
        library_root, documents
    )
    if data.get("sourceFingerprint") != source_fingerprint:
        raise ValueError(
            "library catalog is stale; run "
            "pypy3 library_codex/tools/build_library_catalog.py"
        )
    if data.get("generatorFingerprint") != generator_fingerprint:
        raise ValueError("library catalog was generated by an older generator")
    return data


GENERIC_RETURN_DESCRIPTIONS = {
    "上記の処理結果。",
    "指定した位置または対象に格納されている値。",
    "指定した範囲の集計結果。",
    "このAPIの結果を呼び出し順・添字順に格納したリスト。",
    "keyが入力中の識別対象、valueが対応する計算結果の辞書。",
    "このAPIの結果要素を1つずつ返すiterator。",
}


def description_quality_issues(data):
    issues = []

    def add(path, reason, text):
        issues.append({"path": path, "reason": reason, "text": text})

    def inspect_symbol(path, symbol):
        description = symbol.get("description", "")
        returned = symbol.get("returnDescription", "")
        if description in {
            "指定した対象への問い合わせ結果を返す。",
            "指定位置・辺・状態の値を取得する。",
            "処理を実行する。",
        }:
            add(path, "generic-purpose", description)
        if returned in GENERIC_RETURN_DESCRIPTIONS:
            add(path, "generic-return", returned)
        return_format = symbol.get("returnFormat", "")
        if (
            (return_format == "tuple" or return_format.startswith("tuple["))
            and not symbol.get("returnParts")
            and returned in GENERIC_RETURN_DESCRIPTIONS
        ):
            add(path, "tuple-parts-missing", return_format)

    for module in data.get("modules", []):
        module_path = module.get("modulePath", "unknown")
        for symbol in module.get("functions", []):
            inspect_symbol(f"{module_path}:{symbol['name']}", symbol)
        for class_item in module.get("classes", []):
            class_path = f"{module_path}:{class_item['name']}"
            creates = class_item.get("constructorCreates", "")
            if re.fullmatch(r"初期化した .+ オブジェクト。", creates):
                add(class_path, "generic-constructor", creates)
            if class_item.get("description", "").endswith("を扱う。"):
                add(
                    class_path,
                    "generic-class-purpose",
                    class_item["description"],
                )
            for method in class_item.get("methods", []):
                inspect_symbol(f"{class_path}.{method['name']}", method)
    return issues


def print_description_audit(data):
    issues = description_quality_issues(data)
    counts = Counter(issue["reason"] for issue in issues)
    print(f"description audit: {len(issues)} issues")
    for reason, count in sorted(counts.items()):
        print(f"  {reason}: {count}")
    for issue in issues:
        print(f"{issue['reason']}\t{issue['path']}\t{issue['text']}")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--audit-descriptions",
        action="store_true",
        help="list vague API purposes and return descriptions without writing",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="regenerate every module instead of reusing unchanged catalog entries",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.audit_descriptions:
        data = check_catalog(ROOT, args.output)
        print_description_audit(data)
        return
    if args.check:
        data = check_catalog(ROOT, args.output)
        print(
            f"library catalog is current: {data['stats']['modules']} modules, "
            f"{data['stats']['functions']} functions, "
            f"{data['stats']['classes']} classes, "
            f"{data['stats']['methods']} methods"
        )
        return
    previous_fingerprints = None
    if args.output.is_file():
        try:
            previous_data = json.loads(args.output.read_text(encoding="utf-8"))
            previous_fingerprints = (
                previous_data.get("sourceFingerprint"),
                previous_data.get("generatorFingerprint"),
            )
        except json.JSONDecodeError:
            pass
    data, reparsed = build_catalog(ROOT, args.output, force_full=args.full)
    current_fingerprints = (
        data["sourceFingerprint"],
        data["generatorFingerprint"],
    )
    if previous_fingerprints != current_fingerprints:
        write_catalog_atomic(args.output, data, ROOT)
        print(f"updated {reparsed} of {len(data['modules'])} modules in {args.output}")
    else:
        print(f"library catalog is already current: {args.output}")


if __name__ == "__main__":
    main()
