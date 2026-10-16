from fractions import Fraction as F
from itertools import combinations


def vertices(a, delta):
    # Equalities for the boundary of 0<=x<=a, 0<=y<=1-a,
    # (1-delta)*x >= (1+delta)*y.
    lines = [(F(1), F(0), F(0)), (F(1), F(0), a),
             (F(0), F(1), F(0)), (F(0), F(1), 1-a),
             (1-delta, -(1+delta), F(0))]
    for (u, v, w), (r, s, t) in combinations(lines, 2):
        det = u*s-v*r
        if not det:
            continue
        x, y = (w*s-v*t)/det, (u*t-w*r)/det
        if 0 <= x <= a and 0 <= y <= 1-a and (1-delta)*x >= (1+delta)*y:
            yield x, y


if __name__ == '__main__':
    cases = 0
    for numerator in range(51, 100):
        a = F(numerator, 100)
        for delta in (F(0), F(1, 10), F(1, 2), F(9, 10), F(1)):
            value = max(abs((1-a)*x-a*y) for x, y in vertices(a, delta))
            assert value == a*(1-a)
            cases += 1
    naive_margin = F(1, 5)
    a = (1+naive_margin)/2
    assert a*(1-a) == (1-naive_margin**2)/4
    print(f'PASS: {cases} exact polygon optima; true-posterior margin alone does not lower n=2 rent')
