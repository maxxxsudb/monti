"""r55: question dominance and cost-sensitive identification.

Partitions of the four host-type hypotheses by five questions; pair coverage;
joint partition of target+price; brute-force minimum-cost identifying battery.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

sys.dont_write_bytecode = True

HYPS = ("correct", "prior", "equal", "classic")


def q_target(h):
    return F(1, 2) if h in ("correct", "prior", "equal") else F(2, 3)


def q_price(h):
    return "buy" if h in ("correct", "classic") else "refuse"


def q_protocol(h, alpha):
    if h == "correct":
        return 2 * alpha / (1 + alpha)
    if h == "prior":
        return alpha
    if h == "equal":
        return F(1, 2)
    if h == "classic":
        return F(2, 3)
    raise ValueError(h)


QUESTIONS = {
    "target": lambda h: q_target(h),
    "price": lambda h: q_price(h),
    "protocol(1/4)": lambda h: q_protocol(h, F(1, 4)),
    "protocol(1/3)": lambda h: q_protocol(h, F(1, 3)),
    "protocol(1/2)": lambda h: q_protocol(h, F(1, 2)),
}

COSTS = {
    "target": F(3, 10),
    "price": F(3, 10),
    "protocol(1/4)": F(1),
    "protocol(1/3)": F(8, 10),
    "protocol(1/2)": F(7, 10),
}


def partition(q):
    groups = {}
    for h in HYPS:
        groups.setdefault(q(h), []).append(h)
    return tuple(tuple(v) for v in groups.values())


def refines(p1, p2):
    return all(any(set(c1) <= set(c2) for c2 in p2) for c1 in p1)


def separated(q):
    out = set()
    for i in range(len(HYPS)):
        for j in range(i + 1, len(HYPS)):
            h1, h2 = HYPS[i], HYPS[j]
            if q(h1) != q(h2):
                out.add(frozenset((h1, h2)))
    return out


ALL_PAIRS = {frozenset((HYPS[i], HYPS[j]))
             for i in range(len(HYPS)) for j in range(i + 1, len(HYPS))}


def joint_partition(qs):
    groups = {}
    for h in HYPS:
        key = tuple(q(h) for q in qs)
        groups.setdefault(key, []).append(h)
    return tuple(tuple(v) for v in groups.values())


def min_cost_battery():
    names = list(QUESTIONS)
    best = None
    for r in range(1, len(names) + 1):
        for combo in combinations(names, r):
            covered = set()
            for name in combo:
                covered |= separated(QUESTIONS[name])
            if covered == ALL_PAIRS:
                cost = sum((COSTS[name] for name in combo), F(0))
                if best is None or cost < best[0]:
                    best = (cost, combo)
    return best


def main():
    print("=== r55 question dominance ===")
    checks = 0
    print("\nPartitions:")
    parts = {}
    for name, q in QUESTIONS.items():
        parts[name] = partition(q)
        print(f"  {name:>15}: {parts[name]}")
        checks += 1

    print("\nRefinement relations:")
    for a in parts:
        for b in parts:
            if a != b and refines(parts[a], parts[b]):
                print(f"  {a} refines {b}")
                checks += 1

    print("\nPair coverage:")
    coverage = {}
    for name, q in QUESTIONS.items():
        coverage[name] = separated(q)
        print(f"  {name:>15}: {len(coverage[name])}/6 pairs")
        checks += 1

    print("\nJoint partition target+price:")
    joint = joint_partition([QUESTIONS["target"], QUESTIONS["price"]])
    print(f"  {joint}")
    assert joint == (("correct",), ("prior", "equal"), ("classic",)), joint
    assert frozenset(("prior", "equal")) not in coverage["target"]
    assert frozenset(("prior", "equal")) not in coverage["price"]
    print("  prior and equal are not separated by either question")
    checks += 4

    print("\nMinimum-cost identifying battery (brute force):")
    cost, combo = min_cost_battery()
    print(f"  {combo}, cost={cost}")
    # the protocol(1/4) alone covers all six
    assert coverage["protocol(1/4)"] == ALL_PAIRS
    # target+price is cheaper but not identifying
    assert coverage["target"] | coverage["price"] != ALL_PAIRS
    # the found battery is identifying
    covered = set()
    for name in combo:
        covered |= coverage[name]
    assert covered == ALL_PAIRS
    checks += 3
    print("  protocol(1/4) covers all six; target+price covers only five")
    print(f"\nAll checks passed; total: {checks}")


if __name__ == "__main__":
    main()
