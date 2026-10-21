import argparse
import ast
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).with_name("large_radix8_medium.py")
PREFIX = "_convolution_large_convolution_"
BASE_SHA256 = "48fe02ac5b36b8958052e50a83b2e5a4011fb1e956c28e2a28d0f8713b498687"


def baseline_data():
    data = BASE.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(data).hexdigest() == BASE_SHA256, "baseline changed"
    return data


def function(source, name):
    tree = ast.parse(source)
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])


def replace_function(source, name, replacement):
    old = function(source, name)
    assert source.count(old) == 1
    return source.replace(old, replacement)


def lane_product(source, lanes):
    old = function(source, PREFIX + "multiply_sixteen_lanes")
    begin, tail = old.split("    for i in range(size):\n", 1)
    _, end = tail.split("    del b\n", 1)
    begin = begin.replace("16 * size", str(lanes) + " * size")
    begin = begin.replace("butterfly8(a)", f"butterfly8(a, {lanes})")
    begin = begin.replace("butterfly8(b)", f"butterfly8(b, {lanes})")
    end = end.replace("butterfly8_inv(a)", f"butterfly8_inv(a, {lanes})")
    lines = ["    for i in range(size):", f"        pos = i << {lanes.bit_length() - 1}"]
    for i in range(lanes):
        lines.append(f"        x{i}, y{i} = a[pos + {i}], b[pos + {i}]")
    for k in range(2 * lanes - 1):
        terms = [f"x{i} * y{k - i}" for i in range(max(0, k - lanes + 1), min(lanes, k + 1))]
        lines.append(f"        c{k} = " + " + ".join(terms))
    for k in range(lanes):
        expr = f"c{k} + weight * (c{k + lanes} % MOD)" if k + 1 < lanes else f"c{k}"
        lines.append(f"        a[pos + {k}] = ({expr}) % MOD")
    lines.append("        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD")
    source = replace_function(source, PREFIX + "multiply_sixteen_lanes", begin + "\n".join(lines) + "\n    del b\n" + end)
    dispatch = function(source, PREFIX + "multiply")
    log = lanes.bit_length() - 1
    dispatch = dispatch.replace("first, second, 1 << 20)", "first, second, MEDIUM_SIZE)")
    dispatch = dispatch.replace("first, second, 1 << 21)", f"first, second, 1 << {25 - log})")
    dispatch = dispatch.replace("MEDIUM_SIZE", f"1 << {24 - log}")
    return replace_function(source, PREFIX + "multiply", dispatch)


def tiled_transform(source, inverse, tile_bits):
    name = PREFIX + ("butterfly8_inv" if inverse else "butterfly8")
    original = function(source, name)
    helper = name + "_range"
    code = original.replace(f"def {name}(values, stride=16):", f"def {helper}(values, stride, start, stop, begin, end):")
    if inverse:
        code = code.replace("    level = height\n    while level:", "    level = start\n    while level > stop:")
        for step in (1, 3):
            header = f"            rotation = 1\n            for block in range(1 << level - {step}):"
            if header not in code:
                header = f"            rotation = 1\n            for block in range(1 << (level - {step})):"
            assert header in code
            replacement = f"            first = begin // (width << {step})\n            last = end // (width << {step})\n            rotation = _tile_rotation(first, level - {step}, {step}, True)\n            for block in range(first, last):"
            code = code.replace(header, replacement)
        cut = f"max(0, height - {tile_bits // 3 * 3})"
        calls = f"    for begin in range(0, len(values), span):\n        {helper}(values, stride, height, cut, begin, begin + span)\n    {helper}(values, stride, cut, 0, 0, len(values))"
    else:
        code = code.replace("    level = 0\n    while level < height:", "    level = start\n    while level < stop:")
        header = "            rotation = 1\n            for block in range(1 << level):"
        assert code.count(header) == 2
        for step in (1, 3):
            replacement = f"            first = begin // (width << {step})\n            last = end // (width << {step})\n            rotation = _tile_rotation(first, level, {step}, False)\n            for block in range(first, last):"
            code = code.replace(header, replacement, 1)
        cut = f"max(0, (height - {tile_bits}) // 3 * 3)"
        calls = f"    {helper}(values, stride, 0, cut, 0, len(values))\n    for begin in range(0, len(values), span):\n        {helper}(values, stride, cut, height, begin, begin + span)"
    wrapper = f"def {name}(values, stride=16):\n    height = (len(values) // stride).bit_length() - 1\n    cut = {cut}\n    if cut == 0:\n        return {helper}(values, stride, {'height, 0' if inverse else '0, height'}, 0, len(values))\n    span = stride << (height - cut)\n{calls}\n    return values"
    return replace_function(source, name, code + "\n\n" + wrapper)


ROTATION = """def _tile_rotation(block, bits, extra, inverse):
    exponent = 0
    for _ in range(bits):
        exponent = (exponent << 1) | (block & 1)
        block >>= 1
    exponent *= (MOD - 1) >> (bits + extra)
    return pow(3, -exponent % (MOD - 1) if inverse else exponent, MOD)
"""


PAD_FORWARD = """def _pad_forward(values, scale, stride, size):
    total = stride * size
    result = [0] * total
    n = len(values)
    if size < 8 or n > total // 2:
        for i in range(n):
            result[i] = values[i] * scale % MOD
        return _convolution_large_convolution_butterfly8(result, stride)
    width = total // 8
    imag = _convolution_ntt998_IMAG
    eighth = pow(3, (MOD - 1) // 8, MOD)
    third = pow(eighth, 3, MOD)
    for i in range(width):
        x0 = values[i] * scale % MOD if i < n else 0
        x1 = values[i + width] * scale % MOD if i + width < n else 0
        x2 = values[i + 2 * width] * scale % MOD if i + 2 * width < n else 0
        x3 = values[i + 3 * width] * scale % MOD if i + 3 * width < n else 0
        v1 = x1 * eighth
        v2 = x2 * imag
        v3 = x3 * third
        d0 = (x1 - x3) * imag
        d1 = x1 * third + x3 * eighth
        result[i] = (x0 + x2 + x1 + x3) % MOD
        result[i + width] = (x0 + x2 - x1 - x3) % MOD
        result[i + 2 * width] = (x0 - x2 + d0) % MOD
        result[i + 3 * width] = (x0 - x2 - d0) % MOD
        result[i + 4 * width] = (x0 + v2 + v1 + v3) % MOD
        result[i + 5 * width] = (x0 + v2 - v1 - v3) % MOD
        result[i + 6 * width] = (x0 - v2 + d1) % MOD
        result[i + 7 * width] = (x0 - v2 - d1) % MOD
    return _convolution_large_convolution_butterfly8(result, stride, 3)
"""


def zero_padded(source, lanes):
    forward = function(source, PREFIX + "butterfly8")
    forward = forward.replace("values, stride=16):", "values, stride=16, start=0):")
    forward = forward.replace("    level = 0", "    level = start")
    forward = forward.replace("cut = max(0,", "cut = max(start,")
    forward = forward.replace("values, stride, 0, cut,", "values, stride, start, cut,")
    forward = forward.replace("values, stride, 0, height,", "values, stride, start, height,")
    source = replace_function(source, PREFIX + "butterfly8", forward)
    product = function(source, PREFIX + "multiply_sixteen_lanes")
    astart = product.index("    a = [0]")
    aend = product.index("    root = ")
    product = product[:astart] + f"    a = _pad_forward(first, 1, {lanes}, size)\n    if first is second:\n        b = a\n    else:\n        b = _pad_forward(second, inverse, {lanes}, size)\n" + product[aend:]
    return PAD_FORWARD + "\n" + replace_function(source, PREFIX + "multiply_sixteen_lanes", product)


def cached_constants(source):
    prelude = ""
    for inverse in (False, True):
        name = PREFIX + ("butterfly8_inv_range" if inverse else "butterfly8_range")
        code = function(source, name)
        tag = "_TILE_INVERSE" if inverse else "_TILE_FORWARD"
        lines = code.splitlines()
        for i, line in enumerate(lines):
            for variable in ("eighth", "third", "rates"):
                if line.startswith("    " + variable + " = "):
                    expr = line.split(" = ", 1)[1]
                    expr = expr.replace("mod", "MOD").replace("max(0, height - 3)", "21")
                    expr = expr.replace("eighth", tag + "_EIGHTH")
                    prelude += tag + "_" + variable.upper() + " = " + expr + "\n"
                    lines[i] = "    " + variable + " = " + tag + "_" + variable.upper()
        source = replace_function(source, name, "\n".join(lines))
    at = source.index("MOD = 998244353") + len("MOD = 998244353")
    return source[:at] + "\n" + prelude + source[at:]


def fused_product(source, lanes, tile_bits):
    name = PREFIX + "multiply_sixteen_lanes"
    original = function(source, name)
    backup = original.replace(name, "_unfused_product", 1)
    pre, rest = original.split("    root = ", 1)
    product, post = rest.split("    del b\n", 1)
    product = "    root = " + product
    parameters, product = product.split("    weight = 1", 1)
    product = "    weight = 1" + product
    product = product.replace("    weight = 1", f"    weight = _tile_rotation(begin // {lanes}, size.bit_length() - 1, 0, False)")
    product = product.replace("    for i in range(size):", f"    for i in range(begin // {lanes}, end // {lanes}):")
    helper = "def _tile_product(a, b, size, begin, end, rates):\n" + product
    setup = f"    height = size.bit_length() - 1\n    if height % 3 or height <= {tile_bits}:\n        return _unfused_product(first, second, size)\n    cut = (height - {tile_bits}) // 3 * 3\n    span = {lanes} << (height - cut)\n"
    pre = pre.replace("    count = ", setup + "    count = ", 1)
    forward = PREFIX + "butterfly8_range"
    inverse = PREFIX + "butterfly8_inv_range"
    for array in ("a", "b"):
        pre = pre.replace(f"{PREFIX}butterfly8({array}, {lanes})", f"{forward}({array}, {lanes}, 0, cut, 0, len({array}))")
    loop = parameters + f"    for begin in range(0, len(a), span):\n        end = begin + span\n        {forward}(a, {lanes}, cut, height, begin, end)\n        if first is not second:\n            {forward}(b, {lanes}, cut, height, begin, end)\n        _tile_product(a, b, size, begin, end, rates)\n        {inverse}(a, {lanes}, height, cut, begin, end)\n"
    post = post.replace(f"{PREFIX}butterfly8_inv(a, {lanes})", f"{inverse}(a, {lanes}, cut, 0, 0, len(a))")
    return replace_function(source, name, backup + "\n\n" + helper + "\n\n" + pre + loop + "    del b\n" + post)


def build(lanes=16, tile_bits=None, zero=False, cached=False, fused=False):
    data = baseline_data()
    source = lane_product(data.decode(), lanes)
    if tile_bits is not None:
        source = ROTATION + "\n" + source
        source = tiled_transform(source, False, tile_bits)
        source = tiled_transform(source, True, tile_bits)
        if cached:
            source = cached_constants(source)
        if fused:
            source = fused_product(source, lanes, tile_bits)
    if zero:
        assert not fused
        source = zero_padded(source, lanes)
    compile(source, "candidate", "exec")
    return source


def initial_screen_source():
    data = build(8).replace("first, second, 1 << 21)", "first, second, 1 << 22)").encode()
    assert hashlib.sha256(data).hexdigest() == "0b632c99e45afad5d72443fd21003e51901979ecb700ff881b7cb411861109c8"
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".cache/large-transform-variants"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    configs = [("lanes8", 8, None), ("lanes16", 16, None), ("lanes32", 32, None)]
    configs += [(f"tile{bits}", 16, bits) for bits in (9, 12, 15)]
    manifest = dict(baselineSha256=BASE_SHA256, variants={})
    for name, lanes, tile_bits in configs:
        data = build(lanes, tile_bits).encode()
        (args.output / (name + ".py")).write_bytes(data)
        manifest["variants"][name] = dict(lanes=lanes, tileBits=tile_bits, sha256=hashlib.sha256(data).hexdigest())
    for lanes in (8, 16):
        name = f"zero{lanes}"
        data = build(lanes, zero=True).encode()
        (args.output / (name + ".py")).write_bytes(data)
        manifest["variants"][name] = dict(lanes=lanes, zero=True, sha256=hashlib.sha256(data).hexdigest())
    for fused in (False, True):
        name = "fused9" if fused else "cached9"
        data = build(16, 9, cached=True, fused=fused).encode()
        (args.output / (name + ".py")).write_bytes(data)
        manifest["variants"][name] = dict(lanes=16, tileBits=9, cached=True, fused=fused, sha256=hashlib.sha256(data).hexdigest())
    data = build(16, 9, zero=True, cached=True).encode()
    (args.output / "cached_zero9.py").write_bytes(data)
    manifest["variants"]["cached_zero9"] = dict(lanes=16, tileBits=9, cached=True, zero=True, sha256=hashlib.sha256(data).hexdigest())
    (args.output / "lanes8_initial_screen.py").write_bytes(initial_screen_source())
    (args.output / "baseline.py").write_bytes(baseline_data())
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
