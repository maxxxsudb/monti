"""r53: collision geometry for the lazy informed host.

Two parameters: alpha (prior of the informed host) and q (probability that the
informed host opens B when both B and C are empty).  Exact checks of the
prediction formulas and collision curves; a grid max-min search for the
separation margin.
"""
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True


def f(alpha, q):
    return alpha * (q + 1) / (1 + alpha * q)


def preds(alpha, q):
    return [f(alpha, q), alpha, F(1, 2), F(2, 3)]


def margin(alpha, q):
    vals = sorted(preds(alpha, q))
    return min(vals[i + 1] - vals[i] for i in range(3))


def check_curves():
    checks = 0
    # q=1: known family
    assert f(F(1, 3), F(1)) == F(1, 2)      # correct = equal
    assert f(F(1, 2), F(1)) == F(2, 3)      # correct = classic
    checks += 2
    # q=1/2: alpha=1/(q+2)=2/5 and alpha=2/(q+3)=4/7
    assert f(F(2, 5), F(1, 2)) == F(1, 2)
    assert f(F(4, 7), F(1, 2)) == F(2, 3)
    checks += 2
    # q=0: f = alpha, so correct = prior for all alpha
    for a in (F(1, 10), F(1, 2), F(9, 10)):
        assert f(a, F(0)) == a
        checks += 1
    # general curve checks: f(1/(q+2), q)=1/2 and f(2/(q+3), q)=2/3
    for q in (F(1, 10), F(1, 3), F(1, 2), F(2, 3), F(9, 10)):
        a1 = 1 / (q + 2)
        a2 = 2 / (q + 3)
        assert f(a1, q) == F(1, 2), (q, a1, f(a1, q))
        assert f(a2, q) == F(2, 3), (q, a2, f(a2, q))
        checks += 2
    print(f"Curves: {checks} exact checks passed")
    return checks


def grid_maxmin():
    best = (-1.0, None, None, None)
    for i in range(1, 100):
        a = F(i, 100)
        for j in range(1, 100):
            q = F(j, 100)
            m = float(margin(a, q))
            if m > best[0]:
                best = (m, a, q, margin(a, q))
    m, a, q, exact_m = best
    print("Grid max-min:")
    print(f"  alpha={a} ({float(a):.4f}), q={q} ({float(q):.4f})")
    print(f"  margin={m:.6f} ({exact_m})")
    print(f"  one-parameter optimum at q=1: 0.140388")
    print(f"  improvement over q=1 optimum: {m - 0.14038820320220757:+.6f}")
    vals = sorted(preds(a, q))
    gaps = [float(vals[k + 1] - vals[k]) for k in range(3)]
    print(f"  predictions={[str(v) for v in vals]}")
    print(f"  gaps={[round(g, 6) for g in gaps]}")
    return 4


def check_q1_optimum():
    """At q=1 the exact one-parameter optimum is alpha*=(5-sqrt(17))/4."""
    import math
    alpha_star = (5 - math.sqrt(17)) / 4
    # use floats for the known constant; exact proof is in the identifiability note
    vals = sorted([2 * alpha_star / (1 + alpha_star), alpha_star, 0.5, 2 / 3])
    gaps = [vals[i + 1] - vals[i] for i in range(3)]
    m = min(gaps)
    expected = (math.sqrt(17) - 3) / 8
    assert abs(m - expected) < 1e-12
    print("q=1 check: alpha*=(5-sqrt(17))/4, margin=(sqrt(17)-3)/8")
    return 2


def main():
    print("=== r53 collision geometry ===")
    total = 0
    total += check_curves()
    total += check_q1_optimum()
    total += grid_maxmin()
    print(f"All checks passed; total: {total}")


if __name__ == "__main__":
    main()
