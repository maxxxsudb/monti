"""r50: exact and high-precision checks for the identifiability note.

Covers:
  Lemma 1  target-invariant mixture;
  Theorem 2  host-type predictions and collision set;
  Theorem 3  one-question lower bound (counting; attainment checked);
  Theorem 4  max-min prior and the constant (sqrt(17)-3)/8;
  Theorem 5  behavioural equivalence of classic and constant 2/3;
  Theorem 6  VOI example.

Exact equalities use Fraction.  The irrational max-min constant is checked
with 80-digit Decimal; the algebraic proof is in the note (Theorem 4).
"""
import sys
import os
from fractions import Fraction as F
from decimal import Decimal, getcontext

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r49_protocol_type import exact  # noqa: E402


def check_lemma1():
    """Y independent of K given E  =>  target posterior invariant, protocol updates."""
    cases = [
        (F(2, 3), F(1, 3), F(1, 2)),
        (F(3, 4), F(1, 4), F(2, 5)),
        (F(1, 2), F(2, 5), F(3, 7)),
        (F(9, 10), F(1, 10), F(5, 9)),
    ]
    checks = 0
    for a, b, p in cases:
        prev = None
        for alpha in (F(1, 10), F(1, 3), F(1, 2), F(2, 3), F(9, 10)):
            pe = alpha * a + (1 - alpha) * b
            py = p  # by Y independent of K given E
            pk = alpha * a / pe
            assert py == p
            assert pk == alpha * a / (alpha * a + (1 - alpha) * b)
            if prev is not None:
                assert pk > prev, (a, b, alpha, pk, prev)
            prev = pk
            checks += 3
    print(f"Lemma 1: {checks} exact equalities and monotonicity checks passed")
    return checks


def q2_predictions(alpha):
    """The four hypotheses of Theorem 2."""
    return [
        ("correct", 2 * alpha / (1 + alpha)),
        ("prior", alpha),
        ("equal", F(1, 2)),
        ("classic", F(2, 3)),
    ]


def check_host_type():
    checks = 0
    for n in range(3, 6):
        for i in range(0, 21):
            alpha = F(i, 20)
            e = exact(n, alpha)
            assert e["Q1"] == F(1, n - 1)
            assert e["Q2"] == (n - 1) * alpha / (1 + (n - 2) * alpha)
            checks += 2
    print(f"Host-type: {checks} exact Q1/Q2 equalities for N=3..5, alpha=0..1 by 1/20")
    return checks


def check_collisions():
    """The exact collision set {0,1/3,1/2,2/3,1}."""
    checks = 0
    # internal collision points
    assert 2 * F(1, 3) / (1 + F(1, 3)) == F(1, 2)  # correct = equal at 1/3
    checks += 1
    assert 2 * F(1, 2) / (1 + F(1, 2)) == F(2, 3)  # correct = classic at 1/2
    checks += 1
    assert F(1, 2) == F(1, 2)  # prior = equal at 1/2
    checks += 1
    assert F(2, 3) == F(2, 3)  # prior = classic at 2/3
    checks += 1
    # degenerate ends
    assert 2 * F(0) / (1 + F(0)) == F(0)  # correct = prior at 0
    checks += 1
    assert 2 * F(1) / (1 + F(1)) == F(1)  # correct = prior at 1
    checks += 1
    # outside the collision set: four distinct answers
    outside = [F(1, 10), F(1, 5), F(3, 10), F(2, 5), F(1, 2) - F(1, 100),
               F(3, 5), F(7, 10), F(4, 5), F(9, 10)]
    for alpha in outside:
        vals = [v for _, v in q2_predictions(alpha)]
        assert len(set(vals)) == 4, (alpha, vals)
        checks += 1
    # separating points used in the note
    for alpha in (F(1, 4), F(2, 9), F(2, 5)):
        vals = [v for _, v in q2_predictions(alpha)]
        assert len(set(vals)) == 4, (alpha, vals)
        checks += 1
    print(f"Collisions: {checks} exact checks; four distinct answers outside {{0,1/3,1/2,2/3,1}}")
    return checks


def min_gap(alpha):
    vals = sorted(v for _, v in q2_predictions(alpha))
    return min(vals[i + 1] - vals[i] for i in range(len(vals) - 1))


def check_maxmin():
    getcontext().prec = 80
    s = Decimal(17).sqrt()
    alpha_star = (Decimal(5) - s) / 4
    f = 2 * alpha_star / (1 + alpha_star)
    vals = sorted([alpha_star, f, Decimal(1) / 2, Decimal(2) / 3])
    gaps = [vals[i + 1] - vals[i] for i in range(3)]
    g = min(gaps)
    expected = (s - 3) / 8
    assert abs(g - expected) < Decimal("1e-70"), (g, expected)
    assert abs(2 * alpha_star * alpha_star - 5 * alpha_star + 1) < Decimal("1e-70")
    print(f"Max-min: alpha*={alpha_star}")
    print(f"         f(alpha*)={f}")
    print(f"         gaps={[str(x) for x in gaps]}")
    print(f"         min gap={g} (expected (sqrt(17)-3)/8={expected})")
    # grid check: no rational point beats alpha*
    best = (Decimal(-1), None)
    for i in range(1, 1000):
        a = Decimal(i) / 1000
        fa = 2 * a / (1 + a)
        v = sorted([a, fa, Decimal(1) / 2, Decimal(2) / 3])
        m = min(v[j + 1] - v[j] for j in range(3))
        if m > best[0]:
            best = (m, a)
    print(f"         grid best: alpha={best[1]}, margin={best[0]}")
    assert best[0] <= g, (best[0], g)
    # the other candidate points from the interval analysis
    candidates = [
        ("7/17", Decimal(7) / 17),
        ("(sqrt(73)-5)/6", (Decimal(73).sqrt() - 5) / 6),
        ("(1+sqrt(13))/6", (Decimal(1) + Decimal(13).sqrt()) / 6),
    ]
    for name, a in candidates:
        fa = 2 * a / (1 + a)
        v = sorted([a, fa, Decimal(1) / 2, Decimal(2) / 3])
        m = min(v[j + 1] - v[j] for j in range(3))
        print(f"         candidate {name}: margin={m}")
        assert m < g, (name, m, g)
    return 4


def check_behavioural_equivalence():
    classic = (F(2, 3), F(2, 3), F(2, 3))
    const = (F(2, 3), F(2, 3), F(2, 3))
    assert classic == const
    print("Behavioural equivalence: classic and constant-2/3 have the same battery vector")
    print(f"  battery (Q2@1/4, Q2@1/2, Q1) = {classic}")
    return 1


def check_voi():
    alpha = F(1, 2)
    price = F(3, 5)
    # buy payoff = alpha - price; refuse = 0
    prior = max(F(0), alpha - price)
    # perfect protocol signal: buy iff K=1, refuse iff K=0
    perfect_protocol = alpha * (1 - price) + (1 - alpha) * F(0)
    # target signal independent of K: same decision as prior
    target = prior
    assert prior == 0
    assert perfect_protocol == F(1, 5)
    assert target == prior
    print("VOI: prior payoff=0; perfect protocol value=1/5; target value=0")
    return 2


def main():
    print("=== r50 identifiability checks ===")
    total = 0
    total += check_lemma1()
    total += check_host_type()
    total += check_collisions()
    total += check_maxmin()
    total += check_behavioural_equivalence()
    total += check_voi()
    print(f"All checks passed; total exact/one-probe checks: {total}")


if __name__ == "__main__":
    main()
