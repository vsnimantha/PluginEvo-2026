import os
import subprocess
import angr
import claripy
import tempfile

def symbolic_paths(binary_path, max_steps=200):
    proj = angr.Project(binary_path, auto_load_libs=False)

    # Symbolic stdin: 3 digits + newline
    sym_bytes = [claripy.BVS(f'byte{i}', 8) for i in range(4)]
    sym_stdin = claripy.Concat(*sym_bytes)

    state = proj.factory.full_init_state(stdin=sym_stdin)

    # Constrain first 3 bytes to be ASCII digits
    for b in sym_bytes[:3]:
        state.solver.add(b >= ord('0'))
        state.solver.add(b <= ord('9'))
    # Last byte is newline
    state.solver.add(sym_bytes[3] == ord('\n'))

    simgr = proj.factory.simgr(state)
    simgr.explore(n=max_steps)

    results = []
    for s in simgr.deadended:
        output = s.posix.dumps(1)
        try:
            example_input = s.solver.eval(sym_stdin, cast_to=bytes)
        except Exception:
            example_input = b"<symbolic>"
        results.append((example_input, output))
    return results


def symbolic_compare(baseline_path, variant_path):
    print(f"Symbolic compare with baseline_path: {baseline_path} and variant_path: {variant_path}")
    base_results = symbolic_paths(baseline_path)
    var_results = symbolic_paths(variant_path)

    # Map output -> set of example inputs
    base_map = {}
    for inp, out in base_results:
        base_map.setdefault(out, set()).add(inp)

    var_map = {}
    for inp, out in var_results:
        var_map.setdefault(out, set()).add(inp)

    # Find outputs present in both but with different input sets
    differing_outputs = {}
    for out in set(base_map.keys()).union(var_map.keys()):
        base_inputs = base_map.get(out, set())
        var_inputs = var_map.get(out, set())
        if base_inputs != var_inputs:
            differing_outputs[out] = {
                "baseline_inputs": sorted(base_inputs),
                "variant_inputs": sorted(var_inputs)
            }

    return {
        "baseline": {k: sorted(v) for k, v in base_map.items()},
        "variant": {k: sorted(v) for k, v in var_map.items()},
        "differences": differing_outputs
    }


"""
This is the demo functions to execute the script
For demo and testing purpose
"""
def build_demo_binaries(tmpdir):
    baseline_c = r"""
    #include <stdio.h>
    int main() {
        char c;
        scanf("%c", &c);
        if (c == 'A') {
            printf("Alpha\n");
        } else {
            printf("Other\n");
        }
        return 0;
    }
    """

    variant_c = r"""
    #include <stdio.h>
    int main() {
        char c;
        scanf("%c", &c);
        if (c == 'B') { // changed condition
            printf("Beta\n");
        } else {
            printf("Other\n");
        }
        return 0;
    }
    """

    baseline_path = os.path.join(tmpdir, "baseline")
    variant_path = os.path.join(tmpdir, "variant")

    with open(os.path.join(tmpdir, "baseline.c"), "w") as f:
        f.write(baseline_c)
    with open(os.path.join(tmpdir, "variant.c"), "w") as f:
        f.write(variant_c)

    subprocess.run(["gcc", os.path.join(tmpdir, "baseline.c"), "-o", baseline_path], check=True)
    subprocess.run(["gcc", os.path.join(tmpdir, "variant.c"), "-o", variant_path], check=True)

    return baseline_path, variant_path

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        baseline_bin, variant_bin = build_demo_binaries(tmpdir)
        result = symbolic_compare(baseline_bin, variant_bin)

        print("\n=== Symbolic Execution Comparison ===")
        print("\n--- Baseline mapping (output -> example inputs) ---")
        for out, inputs in result["baseline"].items():
            print(f"{out!r}: {inputs}")

        print("\n--- Variant mapping (output -> example inputs) ---")
        for out, inputs in result["variant"].items():
            print(f"{out!r}: {inputs}")

        print("\n--- Differences ---")
        for out, diff in result["differences"].items():
            print(f"Output: {out!r}")
            print(f"  Baseline inputs: {diff['baseline_inputs']}")
            print(f"  Variant inputs:  {diff['variant_inputs']}")
