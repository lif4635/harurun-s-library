import argparse
import ast
import copy
import os
from pathlib import Path
import sys
import tempfile

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from build_library_catalog import build_standalone_code


SUPPORTED = (
    "union_find/UnionFind",
    "fenwick_tree/BIT",
    "segment_tree/SegTree",
    "convolution/NTT998",
    "fps998/FPS",
)
HEADER = ROOT / "templates" / "codon_header.codon"


def assigns(node, name):
    return isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == name for target in node.targets
    )


REDUCTIONS = {
    "_multiply_naive": {"left * right": "left * (right % MOD)"},
    "multiply": {"left * right": "left * (right % MOD)"},
    "square": {"2 * left * series[offset]": "2 * left * (series[offset] % MOD)"},
    "fps_add": {"first[index] + second[index]": "first[index] % mod + second[index] % mod"},
    "fps_sub": {
        "first[index] - second[index]": "first[index] % mod - second[index] % mod",
        "-second[index]": "-(second[index] % mod)",
    },
    "fps_neg": {"-value": "-(value % MOD)"},
    "fps_diff": {"index * series[index]": "index * (series[index] % mod)"},
    "fps_integral": {"value * inverse[index]": "(value % mod) * inverse[index]"},
    "fps_eval": {"result * value + coefficient": "result * value + coefficient % mod"},
    "_fps_log_sparse": {"(index + 1) * series[index + 1]": "(index + 1) * (series[index + 1] % MOD)"},
    "_fps_power_unit_sparse": {
        "exponent + 1": "exponent % MOD + 1",
        "factor * offset * coefficient": "(factor * offset % MOD) * coefficient",
    },
    "_fps_exp_ntt": {"x[index] + series[index]": "x[index] + series[index] % mod"},
    "fps_pow": {
        "value * inverse_coefficient": "(value % MOD) * inverse_coefficient",
        "logarithm[index] * exponent": "logarithm[index] * (exponent % MOD)",
    },
    "fps_sqrt": {
        "(source_frequency[index] - value * value) * inverse_frequency[index]":
            "((source_frequency[index] - value * value) % MOD) * inverse_frequency[index]",
    },
    "taylor_shift": {"series[index] * factorial[index]": "(series[index] % MOD) * factorial[index]"},
}


class CodonTransformer(ast.NodeTransformer):
    def __init__(self, modular):
        self.modular = modular
        self.array_names = set()
        self.reductions = {}
        self.reduced = {}

    def visit_FunctionDef(self, node):
        previous = self.reductions, self.reduced
        name = node.name.removeprefix("_convolution_ntt998")
        self.reductions = REDUCTIONS.get(name, {}) if self.modular else {}
        self.reduced = {key: 0 for key in self.reductions}
        if self.modular:
            if node.name == "fps_sqrt":
                node.returns = ast.parse("Optional[list[int]]", mode="eval").body
                for index, statement in enumerate(node.body):
                    if assigns(statement, "inverse_frequency") and len(statement.targets) == 1:
                        if isinstance(statement.value, ast.Constant) and statement.value.value is None:
                            node.body[index] = ast.AnnAssign(statement.targets[0], ast.parse("Optional[list[int]]", mode="eval").body, statement.value, 1)
            for argument in node.args.args:
                if argument.arg in {"first", "second", "series", "numerator", "denominator", "values"}:
                    argument.annotation = ast.Subscript(ast.Name("list", ast.Load()), ast.Name("int", ast.Load()), ast.Load())
                if argument.arg == "polynomials":
                    argument.annotation = ast.parse("list[list[int]]", mode="eval").body
        node = self.generic_visit(node)
        if any(count != 1 for count in self.reduced.values()):
            raise ValueError(node.name + " arithmetic changed; review Codon conversion")
        self.reductions, self.reduced = previous
        return node

    def visit_ImportFrom(self, node):
        if node.module == "array":
            for name in node.names:
                if name.name != "array":
                    raise ValueError("unsupported array import")
                self.array_names.add(name.asname or name.name)
            return None
        return node

    def visit_ClassDef(self, node):
        if node.name == "SegTree":
            initializer = next(item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == "__init__")
            first = initializer.body[0]
            if (not isinstance(first, ast.If)
                    or ast.unparse(first.test) != "isinstance(values, int)"
                    or any(not any(assigns(statement, "values") for statement in branch)
                           for branch in (first.body, first.orelse))):
                raise ValueError("SegTree constructor changed; review Codon conversion")
            for branch in (first.body, first.orelse):
                assigned = False
                for statement in branch:
                    for child in ast.walk(statement):
                        if isinstance(child, ast.Name) and child.id == "values" and (assigned or isinstance(child.ctx, ast.Store)):
                            child.id = "_codon_values"
                    if assigns(statement, "_codon_values"):
                        assigned = True
            for statement in initializer.body[1:]:
                for child in ast.walk(statement):
                    if isinstance(child, ast.Name) and child.id == "values":
                        child.id = "_codon_values"
        methods = {item.name: item for item in node.body if isinstance(item, ast.FunctionDef)}
        body = []
        for item in node.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                name = item.targets[0].id
                if name == "__slots__":
                    continue
                if isinstance(item.value, ast.Name) and item.value.id in methods:
                    original = methods[item.value.id]
                    if original.args.vararg or original.args.kwarg or original.args.kwonlyargs:
                        raise ValueError("unsupported method alias signature")
                    args = copy.deepcopy(original.args)
                    positional = args.posonlyargs + args.args
                    call = ast.Call(ast.Attribute(ast.Name(positional[0].arg, ast.Load()), original.name, ast.Load()),
                                    [ast.Name(arg.arg, ast.Load()) for arg in positional[1:]], [])
                    item = ast.FunctionDef(name, args, [ast.Return(call)], [], original.returns)
            body.append(item)
        node.body = body
        return self.generic_visit(node)

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.array_names:
            node.func.id = "_codon_array"
        if isinstance(node.func, ast.Name) and node.func.id == "pow" and len(node.args) == 3 and not node.keywords:
            node.func.id = "_codon_pow"
        if (isinstance(node.func, ast.Attribute) and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name) and node.func.value.id.endswith("INVERSE_SIZE")
                and len(node.args) == 1 and not node.keywords):
            key = node.args[0]
            owner = node.func.value
            return ast.IfExp(ast.Compare(copy.deepcopy(key), [ast.In()], [copy.deepcopy(owner)]),
                             ast.Subscript(owner, key, ast.Load()), ast.Constant(None))
        return node

    def visit_BinOp(self, node):
        key = ast.unparse(node)
        if key in self.reductions:
            self.reduced[key] += 1
            return ast.parse(self.reductions[key], mode="eval").body
        node = self.generic_visit(node)
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            text = node.left.value
            if text.count("%") == 1 and "%r" in text:
                first, last = text.split("%r")
                return ast.JoinedStr([ast.Constant(first), ast.FormattedValue(node.right, 114, None), ast.Constant(last)])
        return node

    def visit_UnaryOp(self, node):
        key = ast.unparse(node)
        if key in self.reductions:
            self.reduced[key] += 1
            return ast.parse(self.reductions[key], mode="eval").body
        return self.generic_visit(node)

    def visit_AugAssign(self, node):
        node = self.generic_visit(node)
        accumulation = isinstance(node.target, ast.Subscript) or isinstance(node.target, ast.Name) and node.target.id == "total"
        if self.modular and accumulation and isinstance(node.op, (ast.Add, ast.Sub)):
            target = copy.deepcopy(node.target)
            target.ctx = ast.Load()
            value = ast.BinOp(target, node.op, node.value)
            reduced = ast.BinOp(value, ast.Mod(), ast.Name("MOD", ast.Load()))
            return ast.Assign([node.target], reduced)
        return node


def generate(module):
    module = module.removesuffix(".py").replace("\\", "/")
    if module not in SUPPORTED:
        raise ValueError("not verified for Codon: " + module)
    source, _ = build_standalone_code(ROOT / (module + ".py"), ROOT)
    tree = ast.parse(source)
    transformed = CodonTransformer(module in ("convolution/NTT998", "fps998/FPS")).visit(tree)
    transformed = ast.fix_missing_locations(transformed)
    return HEADER.read_text(encoding="utf-8").rstrip() + "\n\n" + ast.unparse(transformed) + "\n"


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as file:
            name = file.name
            file.write(text)
        os.replace(name, path)
        name = None
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


def validate_output(path, solution=None):
    path = Path(path).resolve()
    if solution is not None and path == Path(solution).resolve():
        raise ValueError("output must not overwrite the solution")
    try:
        relative = path.relative_to(ROOT.resolve())
    except ValueError:
        return
    if not relative.parts or relative.parts[0] != "generated":
        raise ValueError("output inside library_codex must be under generated/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("module", nargs="?", choices=SUPPORTED)
    parser.add_argument("--solution", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        print("\n".join(SUPPORTED))
        return
    if args.module is None:
        parser.error("choose a module or --list")
    if args.output:
        try:
            validate_output(args.output, args.solution)
        except ValueError as error:
            parser.error(str(error))
    result = generate(args.module)
    if args.solution:
        result += "\n" + args.solution.read_text(encoding="utf-8") + "\n"
    if args.output:
        atomic_write(args.output, result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
