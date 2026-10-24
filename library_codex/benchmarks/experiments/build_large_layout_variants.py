import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from library_codex.benchmarks.experiments.build_large_arithmetic_variants import (
    PREFIX, ROOT, function, replace_function,
)


REVISION = "de26b0e2d356a372123fba93e0f2d961acafd076"
MODES = ("current", "lanes4", "lanes8", "lanes32", "lanes8_packed",
         "quarters", "quarters_list", "quarters_fused", "quarters_small",
         "quarters_late", "quarters_fold", "quarters_fold_small", "quarters_fold_list", "quarters_radix4", "quarters_radix4_mod",
         "input_text", "input_digits")


def current():
    return subprocess.check_output([
        "git", "-C", str(ROOT), "show",
        REVISION + ":verify/library_checker/solutions/convolution_mod_large.py",
    ]).decode().replace("\r\n", "\n")


def product_loop(lanes, offset="0", first="0", last="size"):
    shift = lanes.bit_length() - 1
    lines = [f"    for i in range({first}, {last}):", f"        pos = (i << {shift}) - {offset}"]
    for j in range(lanes):
        lines.append(f"        x{j}, y{j} = a[pos + {j}], b[pos + {j}]")
    for k in range(2 * lanes - 1):
        terms = [f"x{j} * y{k-j}" for j in range(max(0, k-lanes+1), min(lanes, k+1))]
        lines.append(f"        c{k} = " + " + ".join(terms))
    for j in range(lanes):
        value = f"c{j}" if j == lanes - 1 else f"c{j} + weight * (c{j+lanes} % MOD)"
        lines.append(f"        a[pos + {j}] = ({value}) % MOD")
    lines.append("        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD")
    return "\n".join(lines) + "\n"


def lanes_product(source, lanes, packed):
    name = PREFIX + "multiply_sixteen_lanes"
    code = function(source, name)
    code = code.replace("    count =", f"    size = size * 16 // {lanes}\n    count =", 1)
    code = code.replace("packed = size == 1 << 20", f"packed = {packed}")
    code = code.replace(", 16, size, packed)", f", {lanes}, size, packed)")
    start = code.index("    for i in range(size):")
    end = code.index("    del b", start)
    code = code[:start] + product_loop(lanes) + code[end:]
    code = code.replace("butterfly8_inv(a, 16)", f"butterfly8_inv(a, {lanes})")
    return replace_function(source, name, code)


def quarters_product(source, packed, fused, tile):
    helpers = []
    for suffix in ("butterfly8_range", "butterfly8_inv_range"):
        name = PREFIX + suffix
        helper = function(source, name)
        helper = helper.replace(name + "(", name + "_quarter(", 1)
        helper = helper.replace("begin, end):", "begin, end, size, base):")
        helper = helper.replace("    size = len(values) // stride\n", "")
        helper = helper.replace("if level < 3:", "if level - stop < 3:")
        helper = helper.replace("if height - level < 3:", "if stop - level < 3:")
        lines = helper.splitlines()
        helper = "\n".join(line + " - base" if line.strip().startswith("offset = ") else line for line in lines)
        helpers.append(helper)
    loop = product_loop(8, "base", "begin >> 3", "end >> 3")
    loop = "".join("        " + line + "\n" for line in loop.splitlines())
    code = f'''def {PREFIX}multiply_sixteen_lanes(first, second, size, packed=None):
    size *= 2
    total = size * 8
    width = total // 4
    count = len(first) + len(second) - 1
    height = size.bit_length() - 1
    inverse = pow(size, MOD - 2, MOD)
    root = pow(3, (MOD - 1) // size, MOD)
    rates = [pow(root, (size >> j + 1) - (size - (size >> j)), MOD) for j in range(size.bit_length())]
    images = []
    cut = 2 + max(0, (height - 2 - {tile}) // 3) * 3
    span = 8 << (height - cut)
    for branch, factor in enumerate((1, MOD - 1, _convolution_ntt998_IMAG, _convolution_ntt998_IIMAG)):
        base = branch * width
        def fold(values, scale):
            result = array("I", [0]) * width if {packed} else [0] * width
            for j in range(width):
                value = values[j] if j < len(values) else 0
                if j + width < len(values):
                    value += factor * values[j + width]
                if j + 2 * width < len(values):
                    value += (factor * factor % MOD) * values[j + 2 * width]
                if j + 3 * width < len(values):
                    value += (factor * factor % MOD * factor % MOD) * values[j + 3 * width]
                result[j] = value * scale % MOD
            return result
        a = fold(first, 1)
        b = a if first is second else fold(second, inverse)
        weight = pow(root, (branch & 1) * 2 + (branch >> 1), MOD)
        {PREFIX}butterfly8_range_quarter(a, 8, 2, cut, base, base + width, size, base)
        if a is not b:
            {PREFIX}butterfly8_range_quarter(b, 8, 2, cut, base, base + width, size, base)
        for begin in range(base, base + width, span):
            end = begin + span
            {PREFIX}butterfly8_range_quarter(a, 8, cut, height, begin, end, size, base)
            if a is not b:
                {PREFIX}butterfly8_range_quarter(b, 8, cut, height, begin, end, size, base)
{loop}            {PREFIX}butterfly8_inv_range_quarter(a, 8, height, cut, begin, end, size, base)
        del b
        {PREFIX}butterfly8_inv_range_quarter(a, 8, cut, 2, base, base + width, size, base)
        images.append(a)
    result = [0] * count
    a, b, c, d = images
    imag = _convolution_ntt998_IIMAG
    scale = inverse if first is second else 1
    for j in range(width):
        u = a[j] + b[j]
        v = a[j] - b[j]
        w = c[j] + d[j]
        z = (c[j] - d[j]) * imag
        if j < count:
            result[j] = (u + w) * scale % MOD
        if j + width < count:
            result[j + width] = (v + z) * scale % MOD
        if j + 2 * width < count:
            result[j + 2 * width] = (u - w) * scale % MOD
        if j + 3 * width < count:
            result[j + 3 * width] = (v - z) * scale % MOD
    return result'''
    if not fused:
        code = code.replace("    cut = 2 + max(0, (height - 2 - " + str(tile) + ") // 3) * 3", "    cut = 2")
    return replace_function(source, PREFIX + "multiply_sixteen_lanes", "\n\n".join(helpers) + "\n\n" + code)


def radix4_helpers(source):
    for inverse in (False, True):
        suffix = "butterfly8_inv_range" if inverse else "butterfly8_range"
        name = PREFIX + suffix + "_quarter"
        old = function(source, name)
        begin = old.index("        else:\n")
        code = old[:begin].replace("< 3:", "< 2:")
        remaining = "level - 2" if inverse else "level"
        width = "height - level" if inverse else "height - level - 2"
        code += f'''        else:
            width = stride << ({width})
            first = begin // (width << 2)
            last = end // (width << 2)
            rotation = {PREFIX}tile_rotation(first, {remaining}, 2, {inverse})
            for block in range(first, last):
                r2 = rotation * rotation % mod
                r3 = r2 * rotation % mod
                s1 = rotation * imag % mod
                s3 = r3 * imag % mod
                offset = block * (width << 2) - base
                for index in range(width):
                    pos = offset + index
                    x0 = values[pos]
                    x1 = values[pos + width]
                    x2 = values[pos + 2 * width]
                    x3 = values[pos + 3 * width]
'''
        if inverse:
            code += '''                    u = x0 + x1
                    v = x2 + x3
                    w = x0 - x1
                    z = x2 - x3
                    values[pos] = (u + v) % mod
                    values[pos + width] = (w * rotation + z * s1) % mod
                    values[pos + 2 * width] = (u - v) * r2 % mod
                    values[pos + 3 * width] = (w * r3 - z * s3) % mod
                rotation = rotation * _convolution_ntt998_IRATE3[(~block & -~block).bit_length()] % mod
            level -= 2
'''
        else:
            code += '''                    u = x0 + x2 * r2
                    v = x1 * rotation + x3 * r3
                    w = x0 - x2 * r2
                    z = x1 * s1 - x3 * s3
                    values[pos] = (u + v) % mod
                    values[pos + width] = (u - v) % mod
                    values[pos + 2 * width] = (w + z) % mod
                    values[pos + 3 * width] = (w - z) % mod
                rotation = rotation * _convolution_ntt998_RATE3[(~block & -~block).bit_length()] % mod
            level += 2
'''
        code += "    return values"
        source = replace_function(source, name, code)
    return source


def build(mode):
    if mode not in MODES:
        raise ValueError(mode)
    source = current()
    if mode.startswith("lanes"):
        lanes = int(mode.removeprefix("lanes").split("_")[0])
        source = lanes_product(source, lanes, mode.endswith("packed"))
    elif mode.startswith("quarters"):
        source = quarters_product(source, not mode.endswith("list"), mode not in ("quarters", "quarters_list"), 6 if mode.endswith("small") else 9)
        if mode in ("quarters_late", "quarters_fold", "quarters_fold_small", "quarters_fold_list") or mode.startswith("quarters_radix4"):
            name = PREFIX + "multiply_sixteen_lanes"
            code = function(source, name)
            code = code.replace("fold(second, inverse)", "fold(second, 1)")
            code = code.replace("    imag = _convolution_ntt998_IIMAG", "    imag = _convolution_ntt998_IIMAG * inverse % MOD")
            code = code.replace("    scale = inverse if first is second else 1", "    scale = inverse")
            code = code.replace("v = a[j] - b[j]", "v = (a[j] - b[j]) * inverse")
            code = code.replace("(v + z) * scale", "(v + z)").replace("(v - z) * scale", "(v - z)")
            if "fold" in mode or mode.startswith("quarters_radix4"):
                start = code.index("            for j in range(width):")
                code = code[:start] + '''            if width <= len(values) <= 2 * width:
                count = len(values) - width
                if factor == 1:
                    for j in range(count):
                        result[j] = (values[j] + values[j + width]) % MOD
                elif factor == MOD - 1:
                    for j in range(count):
                        result[j] = (values[j] - values[j + width]) % MOD
                else:
                    for j in range(count):
                        result[j] = (values[j] + factor * values[j + width]) % MOD
                for j in range(count, width):
                    result[j] = values[j] % MOD
                return result
''' + code[start:]
            source = replace_function(source, name, code)
        if mode.startswith("quarters_radix4"):
            source = source.replace("(height - 2 - 9) // 3) * 3", "(height - 2 - 8) // 2) * 2")
            source = radix4_helpers(source)
            if mode.endswith("mod"):
                name = PREFIX + "butterfly8_range_quarter"
                code = function(source, name).replace("z = x1 * s1 - x3 * s3", "z = (x1 * rotation - x3 * r3) % mod * imag")
                source = replace_function(source, name, code)
                name = PREFIX + "butterfly8_inv_range_quarter"
                code = function(source, name).replace("z = x2 - x3", "z = (x2 - x3) * imag % mod")
                code = code.replace("w * rotation + z * s1", "(w + z) * rotation")
                code = code.replace("w * r3 - z * s3", "(w - z) * r3")
                source = replace_function(source, name, code)
    elif mode == "input_text":
        source = source.replace("map(int, chunk[:end].split())", "map(int, chunk[:end].decode('ascii').split())")
    elif mode == "input_digits":
        source = replace_function(source, "read_coefficients", '''def read_coefficients(stream, n):
    result = array("I", [0]) * n
    count = 0
    value = 0
    active = False
    while True:
        chunk = stream.read(1 << 16)
        if not chunk:
            if active:
                if count >= n:
                    raise ValueError("unexpected number of coefficients")
                result[count] = value
                count += 1
            if count != n:
                raise ValueError("unexpected number of coefficients")
            return result
        for digit in chunk:
            if 48 <= digit <= 57:
                value = value * 10 + digit - 48
                active = True
            elif digit <= 32:
                if active:
                    if count >= n:
                        raise ValueError("unexpected number of coefficients")
                    result[count] = value
                    count += 1
                    value = 0
                    active = False
            else:
                raise ValueError("invalid coefficient")''')
    compile(source, mode, "exec")
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".cache/large-layout-variants"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"revision": REVISION, "variants": {}}
    for mode in MODES:
        data = build(mode).encode()
        (args.output / (mode + ".py")).write_bytes(data)
        manifest["variants"][mode] = hashlib.sha256(data).hexdigest()
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
