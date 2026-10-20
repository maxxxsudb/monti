"""r62: exact finite-horizon POMDP for the host-type item, deterministic probes.

State = a cell (subset of the four hypotheses) with a uniform belief.  Probes
are deterministic; after a probe the cell splits by the answer.  The DP is
exact over the 16 subsets.  With a positive probe cost c and terminal loss in
[0,1], no optimal policy needs more than ceil(1/c) probes: the cost alone
exceeds the maximum possible loss.  The script computes the optimal policy for
horizons 1..10 and two probe families:
  A: target, price, protocol(1/3)  (no single identifying probe);
  B: A plus protocol(1/4)          (one identifying probe).
"""
import sys
from fractions import Fraction as F
from functools import lru_cache

sys.dont_write_bytecode = True

HYPS = ("correct", "prior", "equal", "classic")
COST = F(1, 10)


def q_target(h):
    return F(1, 2) if h in ("correct", "prior", "equal") else F(2, 3)


def q_price(h):
    return "buy" if h in ("correct", "classic") else "refuse"


def q_protocol13(h):
    if h == "correct" or h == "equal":
        return F(1, 2)
    if h == "prior":
        return F(1, 3)
    return F(2, 3)


def q_protocol14(h):
    if h == "correct":
        return F(2, 5)
    if h == "prior":
        return F(1, 4)
    if h == "equal":
        return F(1, 2)
    return F(2, 3)


PROBES_A = {
    "target": q_target,
    "price": q_price,
    "protocol(1/3)": q_protocol13,
}
PROBES_B = dict(PROBES_A)
PROBES_B["protocol(1/4)"] = q_protocol14


def split(cell, probe):
    groups = {}
    for h in cell:
        groups.setdefault(probe(h), []).append(h)
    return tuple(tuple(sorted(v)) for v in groups.values())


def stop_risk(cell):
    return 1 - F(1, len(cell))


def solve(probes, horizon):
    """Return (value, first_action) for the full hypothesis set."""

    @lru_cache(maxsize=None)
    def value(cell, t):
        cell = tuple(sorted(cell))
        if t == 0:
            return stop_risk(cell), ("stop",)
        best = (stop_risk(cell), ("stop",))
        for name, probe in probes.items():
            subs = split(cell, probe)
            if len(subs) == 1:
                continue  # no information, only cost
            total = COST
            for sub in subs:
                total += F(len(sub), len(cell)) * value(tuple(sorted(sub)), t - 1)[0]
            if total < best[0]:
                best = (total, (name,))
        return best

    return value(tuple(sorted(HYPS)), horizon)


def trace(probes, horizon, cell, limit=10):
    """Follow the optimal policy, printing actions and cells."""
    out = []
    t = horizon
    cell = tuple(sorted(cell))
    while t > 0:
        val, act = solve_cell(probes, cell, t)
        if act[0] == "stop":
            out.append((t, act[0], cell, val))
            break
        probe = probes[act[0]]
        subs = split(cell, probe)
        out.append((t, act[0], cell, val, subs))
        # follow the largest subcell for display
        cell = max(subs, key=len)
        t -= 1
        if len(out) >= limit:
            break
    return out


def solve_cell(probes, cell, t):
    @lru_cache(maxsize=None)
    def value(c, tt):
        c = tuple(sorted(c))
        if tt == 0:
            return stop_risk(c), ("stop",)
        best = (stop_risk(c), ("stop",))
        for name, probe in probes.items():
            subs = split(c, probe)
            if len(subs) == 1:
                continue
            total = COST
            for sub in subs:
                total += F(len(sub), len(c)) * value(tuple(sorted(sub)), tt - 1)[0]
            if total < best[0]:
                best = (total, (name,))
        return best

    return value(tuple(sorted(cell)), t)


def main():
    print("=== r62 exact POMDP, deterministic probes ===")
    print(f"cost per probe = {COST}; terminal 0-1 loss")
    print(f"horizon bound ceil(1/c) = {int(1/float(COST))}")
    for name, probes in (("A: no single identifier", PROBES_A),
                         ("B: with protocol(1/4)", PROBES_B)):
        print(f"\n{name}")
        print(f"{'T':>3} {'value':>10} {'first action':>18}")
        vals = []
        for T in range(1, 11):
            val, act = solve(probes, T)
            vals.append(float(val))
            print(f"{T:>3} {float(val):>10.6f} {act[0]:>18}")
        # the value is non-increasing and stabilizes
        assert all(vals[i] >= vals[i + 1] - 1e-12 for i in range(len(vals) - 1))
        print(f"  stabilized value: {vals[-1]:.6f}")
    print("\nOptimal policy trace for family A, T=10, starting from all four:")
    for row in trace(PROBES_A, 10, HYPS, limit=5):
        print(" ", row)
    print("All checks passed")


if __name__ == "__main__":
    main()
