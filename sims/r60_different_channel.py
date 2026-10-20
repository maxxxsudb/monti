"""r60: a different channel that actually reduces Bayes risk.

First question Q2(1/4), symmetric 4-ary noise epsilon.  Second question: a
perfect binary test of the group A={correct,classic} vs B={prior,equal}.
A perfect group test is a different channel (asymmetric, informative), not
just a recoding; it reduces the Bayes risk below epsilon.  A noisy binary
group test is also computed for comparison.
"""
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True

HYPS = ("correct", "prior", "equal", "classic")
KEYS = {"correct": F(2, 5), "prior": F(1, 4), "equal": F(1, 2), "classic": F(2, 3)}
GROUP = {"correct": "A", "classic": "A", "prior": "B", "equal": "B"}


def ary_prob(obs, true, eps, m):
    return 1 - eps if obs == true else eps / (m - 1)


def risk_first(eps):
    vals = list(KEYS.values())
    total = sum(max(ary_prob(obs, KEYS[h], eps, 4) for h in HYPS) for obs in vals)
    return 1 - total / len(HYPS)


def risk_group(eps, p, q):
    """Second answer A/B with P(A|A)=1-p, P(B|A)=p, P(A|B)=q, P(B|B)=1-q."""
    total = F(0)
    for obs1 in KEYS.values():
        for obs2 in ("A", "B"):
            best = F(0)
            for h in HYPS:
                if GROUP[h] == "A":
                    p2 = (1 - p) if obs2 == "A" else p
                else:
                    p2 = q if obs2 == "A" else (1 - q)
                lik = ary_prob(obs1, KEYS[h], eps, 4) * p2
                if lik > best:
                    best = lik
            total += best
    return 1 - total / len(HYPS)


def main():
    print("=== r60 different channel: group test ===")
    print(f"{'eps':>6} {'R1':>10} {'R2 perfect':>12} {'gain':>10}")
    checks = 0
    for eps in (F(1, 20), F(1, 10), F(1, 5), F(3, 10), F(1, 2)):
        r1 = risk_first(eps)
        r2 = risk_group(eps, F(0), F(0))  # perfect group test
        assert r2 < r1, (eps, r1, r2)
        assert r2 == 2 * eps / 3, (eps, r2, 2 * eps / 3)
        print(f"{float(eps):>6.2f} {float(r1):>10.6f} {float(r2):>12.6f} "
              f"{float(r1-r2):>10.6f}")
        checks += 1
    print("perfect group test: R2 = 2*eps/3 exactly")
    # noisy group test: a few asymmetric examples
    print("\nnoisy group test at eps=1/10:")
    for p, q in ((F(0), F(0)), (F(1, 20), F(1, 20)), (F(1, 10), F(1, 10)),
                 (F(1, 20), F(1, 10))):
        rr = risk_group(F(1, 10), p, q)
        print(f"  p={p}, q={q}: R2={float(rr):.6f}")
        checks += 1
    # the perfect test is the best on this small grid
    best = (1.0, None, None)
    for i in range(0, 11):
        p = F(i, 20)
        for j in range(0, 11):
            q = F(j, 20)
            rr = risk_group(F(1, 10), p, q)
            if float(rr) < best[0]:
                best = (float(rr), p, q)
    print(f"grid best: R2={best[0]:.6f} at p={best[1]}, q={best[2]}")
    assert best[0] < float(risk_first(F(1, 10)))
    print(f"All checks passed; total: {checks + 1}")


if __name__ == "__main__":
    main()
