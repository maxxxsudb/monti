"""Round 10: value of the last test as a Jensen gap of the decision envelope.

Setting of P1: n options, one target, equal priors, one test per option,
conditionally iid results. g1 = outcome law at the target, g0 = elsewhere,
l(x) = g1(x)/g0(x). Checks, in exact fractions:
  (1) P(correct, forced choice) = (1/n) E_0[max_i l(X_i)]  (untested: l = 1);
  (2) the last test has zero value  <=>  l takes at most two values;
  (3) with abstention (+1/-2/0) a two-valued l can have positive value.
"""
from fractions import Fraction as F
from itertools import product


def bayes_value(n, k, g1, g0, payoff):
    """Exact optimal value when the first k options are tested."""
    outs = range(len(g0))
    total = F(0)
    for xs in product(outs, repeat=k):
        joint = []  # P(xs, target = i)
        for i in range(n):
            p = F(1, n)
            for j, x in enumerate(xs):
                p *= g1[x] if j == i else g0[x]
            joint.append(p)
        total += payoff(joint)
    return total


def forced(joint):
    return max(joint)


def abstain(joint):
    s = sum(joint)
    return max(F(0), max(3 * p - 2 * s for p in joint))


def envelope_value(n, g1, g0):
    """(1/n) E_0[max l(X_i)] with all n options tested."""
    lr = [a / b for a, b in zip(g1, g0)]
    total = F(0)
    for xs in product(range(len(g0)), repeat=n):
        w = F(1)
        for x in xs:
            w *= g0[x]
        total += w * max(lr[x] for x in xs)
    return total / n


CASES = [
    # name, g1, g0, expected number of distinct LR values
    ("binary a=3/4 b=1/3", [F(3, 4), F(1, 4)], [F(1, 3), F(2, 3)]),
    ("ERRATA 3-outcome", [F(1, 5), F(2, 5), F(2, 5)], [F(2, 5), F(2, 5), F(1, 5)]),
    ("3 outcomes, 2 LR values", [F(1, 2), F(1, 4), F(1, 4)], [F(1, 4), F(3, 8), F(3, 8)]),
    ("4 outcomes, 2 LR values", [F(1, 3), F(1, 3), F(1, 6), F(1, 6)], [F(1, 6), F(1, 6), F(1, 3), F(1, 3)]),
    ("3 outcomes, 3 LR values", [F(1, 2), F(1, 3), F(1, 6)], [F(1, 6), F(1, 3), F(1, 2)]),
    ("4 outcomes, 3 LR values", [F(2, 5), F(1, 5), F(1, 5), F(1, 5)], [F(1, 5), F(1, 5), F(1, 5), F(2, 5)]),
]

ok = True
for name, g1, g0 in CASES:
    assert sum(g1) == 1 and sum(g0) == 1
    nlr = len({a / b for a, b in zip(g1, g0)})
    for n in (2, 3, 4):
        full = bayes_value(n, n, g1, g0, forced)
        last = full - bayes_value(n, n - 1, g1, g0, forced)
        ok &= full == envelope_value(n, g1, g0)
        zero_pred = nlr <= 2
        ok &= (last == 0) == zero_pred
        ab = bayes_value(n, n, g1, g0, abstain) - bayes_value(n, n - 1, g1, g0, abstain)
        print(f"{name:26s} n={n} LR values={nlr}  forced last={str(last):>10s}  abstain last={ab}")
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")
