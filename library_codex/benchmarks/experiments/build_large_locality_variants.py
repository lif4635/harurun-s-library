import argparse
import hashlib
import json
from pathlib import Path

from library_codex.benchmarks.experiments.build_large_arithmetic_variants import (
    PREFIX, REVISION, baseline, function, replace_function,
)


MODES = ("baseline", "packed_second", "packed_both", "fused", "fused_second", "fused_both", "fused_compact", "fused_all", "fused_output", "fused_local")


def build(mode):
    if mode not in MODES:
        raise ValueError(mode)
    source = baseline()
    if mode == "baseline":
        return source
    packed = "packed" in mode or mode.endswith(("second", "both", "compact", "all", "output", "local"))
    both = mode.endswith(("both", "compact", "all", "output", "local"))
    fused = mode.startswith("fused")
    pad_name = PREFIX + "pad_forward"
    pad = function(source, pad_name)
    pad = pad.replace("stride, size):", "stride, size, packed=False, stop=None):")
    pad = pad.replace("result = [0] * total", 'result = array("I", [0]) * total if packed else [0] * total')
    pad = pad.replace("        return " + PREFIX + "butterfly8(result, stride)",
                      "        if stop is not None:\n            return " + PREFIX + "butterfly8_range(result, stride, 0, stop, 0, total)\n        return " + PREFIX + "butterfly8(result, stride)")
    pad = pad.replace("    return " + PREFIX + "butterfly8(result, stride, 3)",
                      "    if stop is not None:\n        return " + PREFIX + "butterfly8_range(result, stride, 3, stop, 0, total)\n    return " + PREFIX + "butterfly8(result, stride, 3)")
    source = replace_function(source, pad_name, pad)
    name = PREFIX + "multiply_sixteen_lanes"
    product = function(source, name)
    settings = "    height = size.bit_length() - 1\n    fused = height >= 6 and height % 3 == 0\n    cut = max(3, height - 9) if fused else None\n" if fused else "    cut = None\n"
    if mode == "fused_compact":
        settings = settings.replace("height - 9", "height - 6")
    if mode == "fused_all":
        settings = settings.replace("height >= 6 and height % 3 == 0", "height >= 12")
        range_name = PREFIX + "butterfly8_range"
        ranged = function(source, range_name).replace("if height - level < 3:", "if stop - level < 3:")
        source = replace_function(source, range_name, ranged)
    product = product.replace("    a = ", settings + "    a = ", 1)
    product = product.replace("(first, 1, 16, size)", f"(first, 1, 16, size, {both}, cut)")
    product = product.replace("(second, inverse, 16, size)", f"(second, inverse, 16, size, {packed}, cut)")
    if fused:
        begin = product.index("    for i in range(size):")
        end = product.index("    del b", begin)
        loop = product[begin:end].replace("range(size)", "range(begin >> 4, end >> 4)", 1)
        loop = "".join("    " + line + "\n" for line in loop.splitlines())
        before = f"""    span = 16 << (height - cut) if fused else 16 * size
    for begin in range(0, 16 * size, span):
        end = begin + span
        if fused:
            {PREFIX}butterfly8_range(a, 16, cut, height, begin, end)
            if a is not b:
                {PREFIX}butterfly8_range(b, 16, cut, height, begin, end)
"""
        after = f"""        if fused:
            {PREFIX}butterfly8_inv_range(a, 16, height, cut, begin, end)
"""
        product = product[:begin] + before + loop + after + product[end:]
        product = product.replace("    " + PREFIX + "butterfly8_inv(a, 16)",
                                  f"    if fused:\n        {PREFIX}butterfly8_inv_range(a, 16, cut, 0, 0, len(a))\n    else:\n        {PREFIX}butterfly8_inv(a, 16)")
    if both:
        product = product.replace("    return a", "    return list(a)")
    if mode == "fused_local":
        helpers = []
        for suffix in ("butterfly8_range", "butterfly8_inv_range"):
            old_name = PREFIX + suffix
            helper = function(source, old_name)
            helper = helper.replace(old_name + "(", old_name + "_local(", 1)
            helper = helper.replace("begin, end):", "begin, end, size):")
            helper = helper.replace("    size = len(values) // stride\n", "")
            lines = helper.splitlines()
            helper = "\n".join(line + " - begin" if line.strip().startswith("offset = ") else line for line in lines)
            helpers.append(helper)
        first = product.index("        if fused:\n")
        last = product.index("    del b", first)
        block = product[first:last]
        block = block.replace(f"        if fused:\n            {PREFIX}butterfly8_range", f"        if fused:\n            local_a = list(a[begin:end])\n            local_b = local_a if a is b else list(b[begin:end])\n            {PREFIX}butterfly8_range", 1)
        for suffix in ("butterfly8_range", "butterfly8_inv_range"):
            for variable in ("a", "b"):
                block = block.replace(PREFIX + suffix + "(" + variable + ",", PREFIX + suffix + "_local(local_" + variable + ",")
        block = block.replace("height, begin, end)", "height, begin, end, size)").replace("cut, begin, end)", "cut, begin, end, size)")
        block = block.replace("        for i in range(begin >> 4, end >> 4):", "        else:\n            local_a, local_b = a, b\n        for i in range(begin >> 4, end >> 4):")
        block = block.replace("pos = i << 4", "pos = (i << 4) - begin")
        block = block.replace("a[pos", "local_a[pos").replace("b[pos", "local_b[pos")
        block += '            a[begin:end] = array("I", local_a)\n        del local_a, local_b\n'
        product = "\n\n".join(helpers) + "\n\n" + product[:first] + block + product[last:]
    if mode == "fused_output":
        product = product.replace(f"{PREFIX}butterfly8_inv_range(a, 16, cut, 0, 0, len(a))",
                                  f"{PREFIX}butterfly8_inv_range(a, 16, cut, 3, 0, len(a))\n        a = {PREFIX}finish_inverse(a)")
        product = product.replace("return list(a)", "return a if fused else list(a)")
        helper = f"""def {PREFIX}finish_inverse(values):
    width = len(values) // 8
    result = [0] * len(values)
    imag = _convolution_ntt998_IIMAG
    eighth = {PREFIX}TILE_INVERSE_EIGHTH
    third = {PREFIX}TILE_INVERSE_THIRD
    mod = MOD
    for pos in range(width):
        x0 = values[pos]
        x1 = values[pos + width]
        x2 = values[pos + 2 * width]
        x3 = values[pos + 3 * width]
        x4 = values[pos + 4 * width]
        x5 = values[pos + 5 * width]
        x6 = values[pos + 6 * width]
        x7 = values[pos + 7 * width]
        u0 = x0 + x1 + x2 + x3
        u1 = x0 - x1
        u2 = x0 + x1 - x2 - x3
        u3 = (x2 - x3) * imag
        v0 = x4 + x5 + x6 + x7
        v1 = x4 - x5
        v2 = (x4 + x5 - x6 - x7) * imag
        v3 = x6 - x7
        p = v1 * eighth + v3 * third
        q = v1 * third + v3 * eighth
        result[pos] = (u0 + v0) % mod
        result[pos + width] = (u1 + u3 + p) % mod
        result[pos + 2 * width] = (u2 + v2) % mod
        result[pos + 3 * width] = (u1 - u3 + q) % mod
        result[pos + 4 * width] = (u0 - v0) % mod
        result[pos + 5 * width] = (u1 + u3 - p) % mod
        result[pos + 6 * width] = (u2 - v2) % mod
        result[pos + 7 * width] = (u1 - u3 - q) % mod
    return result


"""
        product = helper + product
    source = replace_function(source, name, product)
    compile(source, mode, "exec")
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".cache/large-locality-variants"))
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
