"""r57: second channel — bijection vs coarsening.

First question Q2(1/4) has four keys.  Coarsening Q2(1/2) has two keys;
bijection Q2(2/9) has four.  Symmetric answer noise; exact Bayes risks for
one question, first+coarsening, first+bijection.
"""
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True

HYPS = ("correct", "prior", "equal", "classic")

KEYS1 = {
    "correct": F(2, 5),
    "prior": F(1, 4),
    "equal": F(1, 2),
    "classic": F(2, 3),
}
KEYS_COARSE = {
    "correct": F(2, 3),
    "prior": F(1, 2),
    "equal": F(1, 2),
    "classic": F(2, 3),
}
KEYS_BIJ = {
    "correct": F(4, 11),
    "prior": F(2, 9),
    "equal": F(1, 2),
    "classic": F(2, 3),
}


def ary_prob(obs, true, eps, m):
    if obs == true:
        return 1 - eps
    return eps / (m - 1)


def risk_one(eps):
    vals = list(KEYS1.values())
    total = sum(max(ary_prob(obs, KEYS1[h], eps, 4) for h in HYPS) for obs in vals)
    return 1 - total / len(HYPS)


def risk_joint(second_keys, eps, m2):
    vals2 = sorted(set(second_keys.values()))
    total = F(0)
    for obs1 in KEYS1.values():
        for obs2 in vals2:
            best = max(
                ary_prob(obs1, KEYS1[h], eps, 4) * ary_prob(obs2, second_keys[h], eps, m2)
                for h in HYPS
            )
            total += best
    return 1 - total / len(HYPS)


def main():
    print("=== r57 second channel ===")
    print(f"{'eps':>6} {'R1':>10} {'R2 coarse':>12} {'R2 bij':>10} "
          f"{'gain coarse':>12} {'gain bij':>10}")
    checks = 0
    for eps in (F(0), F(1, 20), F(1, 10), F(1, 5), F(3, 10), F(2, 5), F(1, 2)):
        r1 = risk_one(eps)
        rc = risk_joint(KEYS_COARSE, eps, 2)
        rb = risk_joint(KEYS_BIJ, eps, 4)
        assert rb <= rc <= r1, (eps, r1, rc, rb)
        print(f"{float(eps):>6.2f} {float(r1):>10.6f} {float(rc):>12.6f} {float(rb):>10.6f} "
              f"{float(r1-rc):>12.6f} {float(r1-rb):>10.6f}")
        checks += 3
    # endpoint checks
    assert risk_one(F(0)) == 0
    assert risk_joint(KEYS_COARSE, F(0), 2) == 0
    assert risk_joint(KEYS_BIJ, F(0), 4) == 0
    checks += 3
    print("All checks passed; total:", checks)


if __name__ == "__main__":
    main()
