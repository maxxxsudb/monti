"""r51: partition/information duality checks.

Exact partitions for the host-type item; entropy loss and Bayes error for
the full four hypotheses and for the diagnostic pairs.  Refinement checks
and monotonicity checks.  The entropy values are printed as decimals; the
partition structures and probabilities are exact Fractions.
"""
import sys
import os
import math
import random
from fractions import Fraction as F

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HYPS = ("correct", "prior", "equal", "classic")


def q1_partition():
    return (("correct", "prior", "equal"), ("classic",))


def q2_answer(h, alpha):
    if h == "correct":
        return 2 * alpha / (1 + alpha)
    if h == "prior":
        return alpha
    if h == "equal":
        return F(1, 2)
    if h == "classic":
        return F(2, 3)
    raise ValueError(h)


def q2_partition(alpha):
    groups = {}
    for h in HYPS:
        groups.setdefault(q2_answer(h, alpha), []).append(h)
    return tuple(tuple(v) for v in groups.values())


def prior_uniform(hyps=HYPS):
    return {h: F(1, len(hyps)) for h in hyps}


def entropy_loss(partition, prior):
    total = 0.0
    for cell in partition:
        p = sum(prior[h] for h in cell)
        if p == 0:
            continue
        cond = [prior[h] / p for h in cell if prior[h] > 0]
        hcell = -sum(q * math.log2(q) for q in cond)
        total += float(p) * hcell
    return total


def bayes_error(partition, prior):
    total = 0.0
    for cell in partition:
        p = sum(prior[h] for h in cell)
        if p == 0:
            continue
        maxp = max(prior[h] / p for h in cell)
        total += float(p) * (1 - float(maxp))
    return total


def refines(p1, p2):
    """Every cell of p1 is contained in a cell of p2."""
    for c1 in p1:
        if not any(set(c1) <= set(c2) for c2 in p2):
            return False
    return True


def pair_partition(pair, alpha, question):
    """Restrict a question to a pair of hypotheses; group by answer."""
    if question == "q1":
        ans = {"correct": F(1, 2), "prior": F(1, 2), "equal": F(1, 2), "classic": F(2, 3)}
    else:
        ans = {h: q2_answer(h, alpha) for h in HYPS}
    groups = {}
    for h in pair:
        groups.setdefault(ans[h], []).append(h)
    return tuple(tuple(v) for v in groups.values())


def print_table():
    print("=== Full four hypotheses, uniform prior ===")
    print(f"{'partition':<22} {'H(loss), bits':>14} {'Bayes error':>12}")
    rows = [
        ("Q1 target", q1_partition()),
        ("Q2 alpha=1/4", q2_partition(F(1, 4))),
        ("Q2 alpha=1/3", q2_partition(F(1, 3))),
        ("Q2 alpha=1/2", q2_partition(F(1, 2))),
    ]
    prior = prior_uniform()
    for name, part in rows:
        print(f"{name:<22} {entropy_loss(part, prior):>14.4f} {bayes_error(part, prior):>12.4f}")
    print()

    print("=== Pair losses (entropy, bits; uniform on the pair) ===")
    pairs = [("correct", "blind"), ("correct", "equal"), ("correct", "classic")]
    # 'blind' is not one of the four names; use prior for the protocol-blind hypothesis
    pairs = [("correct", "prior"), ("correct", "equal"), ("correct", "classic")]
    header = f"{'pair':<22} {'Q1':>5} {'Q2(1/4)':>8} {'Q2(1/3)':>8} {'Q2(1/2)':>8}"
    print(header)
    for pair in pairs:
        vals = []
        for question, alpha in (("q1", None), ("q2", F(1, 4)), ("q2", F(1, 3)), ("q2", F(1, 2))):
            part = pair_partition(pair, alpha, question)
            vals.append(entropy_loss(part, prior_uniform(pair)))
        print(f"{pair[0]+'/'+pair[1]:<22} " + " ".join(f"{v:>8.3f}" for v in vals))
    print()


def check_refinement():
    checks = 0
    p_discrete = tuple((h,) for h in HYPS)
    p1 = q1_partition()
    p13 = q2_partition(F(1, 3))
    p12 = q2_partition(F(1, 2))
    p14 = q2_partition(F(1, 4))

    assert p14 == p_discrete
    checks += 1
    assert refines(p14, p13) and refines(p14, p12) and refines(p14, p1)
    checks += 3
    assert refines(p13, p1), "Q2(1/3) should refine Q1"
    checks += 1
    assert not refines(p1, p13)
    checks += 1
    assert not refines(p1, p12) and not refines(p12, p1), "Q1 and Q2(1/2) should be incomparable"
    checks += 2
    print(f"Refinement: {checks} exact structure checks passed")
    print("  Q2(1/4) discrete; Q2(1/3) refines Q1; Q1 and Q2(1/2) incomparable")
    return checks


def check_monotonicity():
    prior = prior_uniform()
    p1 = q1_partition()
    p13 = q2_partition(F(1, 3))
    h1 = entropy_loss(p1, prior)
    h13 = entropy_loss(p13, prior)
    r1 = bayes_error(p1, prior)
    r13 = bayes_error(p13, prior)
    assert h13 <= h1 + 1e-12, (h13, h1)
    assert r13 <= r1 + 1e-12, (r13, r1)
    print("Monotonicity: Q2(1/3) refines Q1; both losses decrease")
    print(f"  entropy {h1:.4f} -> {h13:.4f}; Bayes {r1:.4f} -> {r13:.4f}")
    return 2


def check_pairs():
    prior = prior_uniform(("correct", "prior"))
    assert entropy_loss(pair_partition(("correct", "prior"), None, "q1"), prior) == 1.0
    assert entropy_loss(pair_partition(("correct", "prior"), F(1, 4), "q2"), prior) == 0.0
    prior = prior_uniform(("correct", "equal"))
    assert entropy_loss(pair_partition(("correct", "equal"), F(1, 3), "q2"), prior) == 1.0
    assert entropy_loss(pair_partition(("correct", "equal"), F(1, 4), "q2"), prior) == 0.0
    prior = prior_uniform(("correct", "classic"))
    assert entropy_loss(pair_partition(("correct", "classic"), F(1, 2), "q2"), prior) == 1.0
    assert entropy_loss(pair_partition(("correct", "classic"), F(1, 4), "q2"), prior) == 0.0
    print("Pair losses: exact 0/1 checks passed")
    return 6


def find_reversal():
    """Search for incomparable partitions where entropy and Bayes rank differently."""
    rng = random.Random(0)
    # all set partitions of 4 elements via restricted growth strings
    def partitions(n):
        out = []
        def rec(i, labels, maxlab):
            if i == n:
                cells = {}
                for j, lab in enumerate(labels):
                    cells.setdefault(lab, []).append(j)
                out.append(tuple(tuple(v) for v in cells.values()))
                return
            for lab in range(maxlab + 2):
                rec(i + 1, labels + [lab], max(maxlab, lab))
        rec(0, [], 0)
        return out
    parts = partitions(4)
    parts = [tuple(tuple(HYPS[i] for i in cell) for cell in part) for part in parts]
    for trial in range(2000):
        w = [F(rng.randint(1, 10), 1) for _ in range(4)]
        s = sum(w)
        prior = {HYPS[i]: w[i] / s for i in range(4)}
        for a in range(len(parts)):
            for b in range(a + 1, len(parts)):
                pa, pb = parts[a], parts[b]
                if refines(pa, pb) or refines(pb, pa):
                    continue
                ha, hb = entropy_loss(pa, prior), entropy_loss(pb, prior)
                ra, rb = bayes_error(pa, prior), bayes_error(pb, prior)
                if (ha < hb and ra > rb) or (hb < ha and rb > ra):
                    print("Reversal example found:")
                    print(f"  prior={[str(prior[h]) for h in HYPS]}")
                    print(f"  A={pa}: entropy={ha:.4f}, Bayes={ra:.4f}")
                    print(f"  B={pb}: entropy={hb:.4f}, Bayes={rb:.4f}")
                    return 1
    print("Reversal example: none found in the sample (the functionals are still different)")
    return 0


def main():
    print("=== r51 partition/information duality ===")
    print_table()
    total = 0
    total += check_refinement()
    total += check_monotonicity()
    total += check_pairs()
    total += find_reversal()
    print(f"All checks passed; total: {total}")


if __name__ == "__main__":
    main()
