"""r61: rational collision geometry — degree bound and resultant check.

For a_h=P_h/Q_h, a_h=a_h' iff P_h Q_h' - P_h' Q_h = 0.  The cross polynomial
has degree at most deg P_h + deg Q_h' (<= 2d), so a pair has at most 2d roots
on a line unless the difference is identically zero.  Exact checks on random
rational functions and on the lazy-host family.
"""
import sys
import random
from fractions import Fraction as F

sys.dont_write_bytecode = True


def trim(p):
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def pmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def padd(a, b):
    n = max(len(a), len(b))
    out = [F(0)] * n
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    return trim(out)


def pneg(a):
    return [-x for x in a]


def cross(p1, q1, p2, q2):
    return padd(pmul(p1, q2), pneg(pmul(p2, q1)))


def degree(p):
    return len(trim(list(p))) - 1


def random_poly(rng, d):
    return [F(rng.randint(-5, 5)) for _ in range(d + 1)]


def main():
    print("=== r61 rational collision geometry ===")
    rng = random.Random(0)
    checks = 0
    for d in (1, 2, 3):
        for _ in range(50):
            p1, q1 = random_poly(rng, d), random_poly(rng, d)
            p2, q2 = random_poly(rng, d), random_poly(rng, d)
            if q1 == [F(0)] or q2 == [F(0)]:
                continue
            c = cross(p1, q1, p2, q2)
            assert degree(c) <= 2 * d, (d, degree(c), c)
            checks += 1
    print(f"degree bound: {checks} random pairs passed (deg <= 2d)")

    # lazy-host family: f = alpha(q+1)/(1+alpha q); collision with 1/2 at alpha=1/(q+2)
    # cross with 1/2: 2(q+1) alpha - (1+alpha q) = (q+2) alpha - 1
    print("lazy-host collision with equal:")
    for q in (F(1, 4), F(1, 2), F(1), F(2)):
        alpha = 1 / (q + 2)
        f = alpha * (q + 1) / (1 + alpha * q)
        assert f == F(1, 2), (q, alpha, f)
        print(f"  q={q}: alpha=1/(q+2)={alpha}, f={f}")
        checks += 1
    # collision with classic 2/3: 3(q+1) alpha - 2(1+alpha q)= (q+3) alpha - 2
    print("lazy-host collision with classic:")
    for q in (F(1, 2), F(1), F(2)):
        alpha = 2 / (q + 3)
        f = alpha * (q + 1) / (1 + alpha * q)
        assert f == F(2, 3), (q, alpha, f)
        print(f"  q={q}: alpha=2/(q+3)={alpha}, f={f}")
        checks += 1
    print(f"All checks passed; total: {checks}")


if __name__ == "__main__":
    main()
