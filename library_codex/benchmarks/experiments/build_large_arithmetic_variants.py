import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
REVISION = "1182679615027a260b0889a02eeafe53274792c1"
BASE_SHA256 = "f4426d361647f3f7da95398646f5d0b811bfe9d6f293e0d30d0fffc222d01e9e"
PREFIX = "_convolution_large_convolution_"


def baseline():
    data = subprocess.check_output([
        "git", "-C", str(ROOT), "show",
        REVISION + ":verify/library_checker/solutions/convolution_mod_large.py",
    ]).replace(b"\r\n", b"\n")
    assert hashlib.sha256(data).hexdigest() == BASE_SHA256
    return data.decode()


def function(source, name):
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    return "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])


def replace_function(source, name, replacement):
    old = function(source, name)
    assert source.count(old) == 1
    return source.replace(old, replacement)


def unit_inverse(source):
    name = PREFIX + "butterfly8_inv_range"
    code = function(source, name)
    start = code.rindex("                for index in range(width):")
    end = code.index("                if block + 1", start)
    old = code[start:end]
    body = old[:old.index("                    values[pos] =")]
    extra = """                p1 = u3 * imag
                p2 = v2 * imag
                p3 = v1 * eighth + v3 * third
                p4 = v1 * third + v3 * eighth
                values[pos] = (u0 + v0) % mod
                values[pos + width] = (u1 + p1 + p3) % mod
                values[pos + 2 * width] = (u2 + p2) % mod
                values[pos + 3 * width] = (u1 - p1 + p4) % mod
                values[pos + 4 * width] = (u0 - v0) % mod
                values[pos + 5 * width] = (u1 + p1 - p3) % mod
                values[pos + 6 * width] = (u2 - p2) % mod
                values[pos + 7 * width] = (u1 - p1 - p4) % mod
"""
    indent = lambda text: "".join("    " + line + "\n" for line in text.splitlines())
    body += indent(extra)
    replacement = "                if block == 0:\n" + indent(body)
    replacement += "                else:\n" + indent(old)
    return replace_function(source, name, code[:start] + replacement + code[end:])


def product(source, mode):
    name = PREFIX + "multiply_sixteen_lanes"
    code = function(source, name)
    if mode == "balanced":
        marker = "        c0 ="
        index = code.index(marker)
        extra = "".join(f"        x{i} -= (x{i} > 499122176) * MOD\n" for i in range(16))
        code = code[:index] + extra + code[index:]
    elif mode == "chunked":
        for k in range(8, 23):
            terms = [f"x{i} * y{k - i}" for i in range(max(0, k - 15), min(16, k + 1))]
            if len(terms) <= 8:
                continue
            old = "        c" + str(k) + " = " + " + ".join(terms)
            new = "        c" + str(k) + " = (" + " + ".join(terms[:8]) + ") % MOD + " + " + ".join(terms[8:])
            assert old in code
            code = code.replace(old, new)
    return replace_function(source, name, code)


def approximate_reduction(source):
    for suffix in ("butterfly8_range", "butterfly8_inv_range"):
        name = PREFIX + suffix
        code = function(source, name)
        lines = []
        for line in code.splitlines():
            if line.lstrip().startswith("values[") and line.endswith(" % mod"):
                indent = line[:len(line) - len(line.lstrip())]
                target, expression = line.strip().split(" = ", 1)
                expression = expression[:-6]
                lines += [
                    indent + "reduced = " + expression,
                    indent + "reduced -= (int(reduced * 1.0017587347173304e-09) - (reduced < 0)) * mod",
                    indent + "reduced += (reduced < 0) * mod",
                    indent + target + " = reduced - (reduced >= mod) * mod",
                ]
            else:
                lines.append(line)
        source = replace_function(source, name, "\n".join(lines))
    return source


def input_digits(source):
    name = "read_coefficients"
    code = function(source, name)
    marker = "        result.extend(map(int, chunk[:end].split()))"
    lines = ["        for word in chunk[:end].split():", "            if len(word) == 9 and word.isdigit():"]
    expression = "word[0]"
    for i in range(1, 9):
        expression = "(" + expression + " * 10 + word[" + str(i) + "])"
    lines += ["                result.append(" + expression + " - 5333333328)",
              "            else:", "                result.append(int(word))"]
    assert marker in code
    return replace_function(source, name, code.replace(marker, "\n".join(lines)))


def unscaled_pad(source):
    name = PREFIX + "pad_forward"
    code = function(source, name)
    code = code.replace("values[i] * scale % MOD", "(values[i] if scale == 1 else values[i] * scale % MOD)")
    for k in (1, 2, 3):
        index = "i + width" if k == 1 else f"i + {k} * width"
        expr = f"values[{index}] * scale % MOD"
        code = code.replace(expr, f"(values[{index}] if scale == 1 else {expr})")
    return replace_function(source, name, code)


def pair_forward(source):
    name = PREFIX + "butterfly8_range"
    code = function(source, name)
    tree = ast.parse(code)
    lines = code.splitlines()
    loops = [node for node in ast.walk(tree) if isinstance(node, ast.For)
             and isinstance(node.target, ast.Name) and node.target.id == "index"]
    for node in sorted(loops, key=lambda n: n.lineno, reverse=True):
        body = lines[node.lineno:node.end_lineno]
        lines[node.end_lineno:node.end_lineno] = [line.replace("values[", "other[") for line in body]
    helper = "\n".join(lines).replace(name + "(values,", name + "_pair(values, other,")
    wrapper_name = PREFIX + "butterfly8"
    wrapper = function(source, wrapper_name)
    wrapper = wrapper.replace(wrapper_name + "(values,", wrapper_name + "_pair(values, other,")
    wrapper = wrapper.replace(name + "(values,", name + "_pair(values, other,")
    pad_name = PREFIX + "pad_forward"
    pad = function(source, pad_name)
    pad = pad.replace(pad_name + "(values,", pad_name + "_pair(values,")
    pad = pad.replace("return " + wrapper_name + "(result, stride, 3)", "return result")
    product_name = PREFIX + "multiply_sixteen_lanes"
    old = function(source, product_name)
    paired = old.replace(product_name + "(first,", product_name + "_pair(first,")
    begin = paired.index("    a = ")
    end = paired.index("    root = ", begin)
    paired = paired[:begin] + f"    a = {pad_name}_pair(first, 1, 16, size)\n    b = {pad_name}_pair(second, inverse, 16, size)\n    {wrapper_name}_pair(a, b, 16, 3)\n" + paired[end:]
    header = f"    if size >= 8 and first is not second and max(len(first), len(second)) <= 8 * size:\n        return {product_name}_pair(first, second, size)\n"
    main = old.replace("    count =", header + "    count =", 1)
    return replace_function(source, product_name, helper + "\n\n" + wrapper + "\n\n" + pad + "\n\n" + paired + "\n\n" + main)


def four_lanes(source, tail):
    name = PREFIX + "multiply_sixteen_lanes"
    code = function(source, name)
    start = code.index("    for i in range(size):")
    end = code.index("    del b", start)
    lines = ["    for i in range(size):", "        pos = i << 2"]
    for i in range(4):
        lines.append(f"        x{i}, y{i} = a[pos + {i}], b[pos + {i}]")
    for k in range(7):
        terms = [f"x{i} * y{k-i}" for i in range(max(0, k-3), min(4, k+1))]
        lines.append(f"        c{k} = " + " + ".join(terms))
    for k in range(4):
        expr = f"c{k} + weight * (c{k+4} % MOD)" if k < 3 else f"c{k}"
        lines.append(f"        a[pos + {k}] = ({expr}) % MOD")
    lines.append("        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD")
    code = code[:start] + "\n".join(lines) + "\n" + code[end:]
    code = code.replace(", 16, size)", ", 4, size)").replace("butterfly8_inv(a, 16)", "butterfly8_inv(a, 4)")
    source = replace_function(source, name, code)
    source = source.replace("first, second, 1 << 21)", "first, second, 1 << 23)")
    source = source.replace("first, second, 1 << 20)", "first, second, 1 << 22)")
    if not tail:
        return source
    forward = f"""        if height - level == 2:
            width = stride
            first = begin // (width << 2)
            last = end // (width << 2)
            rotation = {PREFIX}tile_rotation(first, level, 2, False)
            for block in range(first, last):
                r2 = rotation * rotation % mod
                r3 = r2 * rotation % mod
                s1 = rotation * imag % mod
                s3 = r3 * imag % mod
                offset = block * (width << 2)
                for index in range(width):
                    pos = offset + index
                    x0 = values[pos]
                    x1 = values[pos + width]
                    x2 = values[pos + 2 * width]
                    x3 = values[pos + 3 * width]
                    u = x0 + x2 * r2
                    v = x1 * rotation + x3 * r3
                    w = x0 - x2 * r2
                    z = x1 * s1 - x3 * s3
                    values[pos] = (u + v) % mod
                    values[pos + width] = (u - v) % mod
                    values[pos + 2 * width] = (w + z) % mod
                    values[pos + 3 * width] = (w - z) % mod
                rotation = rotation * _convolution_ntt998_RATE3[(~block & -~block).bit_length()] % mod
            level += 2
        elif height - level < 3:
"""
    inverse = """        if level == 2:
            width = stride << (height - 2)
            for index in range(width):
                x0 = values[index]
                x1 = values[index + width]
                x2 = values[index + 2 * width]
                x3 = values[index + 3 * width]
                u = x0 + x1
                v = x2 + x3
                w = x0 - x1
                z = (x2 - x3) * imag
                values[index] = (u + v) % mod
                values[index + width] = (w + z) % mod
                values[index + 2 * width] = (u - v) % mod
                values[index + 3 * width] = (w - z) % mod
            level -= 2
        elif level < 3:
"""
    name = PREFIX + "butterfly8_range"
    code = function(source, name).replace("        if height - level < 3:\n", forward)
    source = replace_function(source, name, code)
    name = PREFIX + "butterfly8_inv_range"
    code = function(source, name).replace("        if level < 3:\n", inverse)
    return replace_function(source, name, code)


def build(mode):
    source = baseline()
    if mode == "unit_inverse":
        source = unit_inverse(source)
    elif mode in ("balanced", "chunked"):
        source = product(source, mode)
    elif mode == "float_reduction":
        source = approximate_reduction(source)
    elif mode == "input_digits":
        source = input_digits(source)
    elif mode == "input_chunk":
        source = source.replace("stream.read(1 << 16)", "stream.read(1 << 20)")
    elif mode == "unit_chunked":
        source = product(unit_inverse(source), "chunked")
    elif mode == "unscaled_pad":
        source = unscaled_pad(source)
    elif mode == "pair_forward":
        source = pair_forward(source)
    elif mode in ("four_binary", "four_radix4"):
        source = four_lanes(source, mode == "four_radix4")
    elif mode != "baseline":
        raise ValueError(mode)
    compile(source, mode, "exec")
    return source


MODES = ("baseline", "unit_inverse", "balanced", "chunked", "float_reduction", "input_digits", "input_chunk", "unit_chunked", "unscaled_pad", "pair_forward", "four_binary", "four_radix4")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".cache/large-arithmetic-variants"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = dict(revision=REVISION, baselineSha256=BASE_SHA256, variants={})
    for mode in MODES:
        data = build(mode).encode()
        (args.output / (mode + ".py")).write_bytes(data)
        manifest["variants"][mode] = hashlib.sha256(data).hexdigest()
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
