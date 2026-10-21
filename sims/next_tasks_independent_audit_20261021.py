"""Independent standard-library checks; interval certificate for allocation."""
from dataclasses import dataclass
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from itertools import combinations
from math import isqrt

getcontext().prec = 60


def dec(x):
    return D(x.numerator) / D(x.denominator) if isinstance(x, F) else D(x)


def lagrange_rows(nodes):
    rows = []
    for i, x in enumerate(nodes):
        y, z = [v for j, v in enumerate(nodes) if j != i]
        v = (1 + x) / ((x - y) * (x - z))
        g0, g1 = v * y * z, v * (1 - y) * (1 - z)
        rows.append((v, -2 * (g0 + g1), 3 * g0 + F(3, 2) * g1))
    return list(zip(*rows))


def weights(nodes, t):
    result = []
    for i, x in enumerate(nodes):
        y, z = [v for j, v in enumerate(nodes) if j != i]
        result.append((1 + x) * (t - y) * (t - z)
                      / ((1 + t) * (x - y) * (x - z)))
    return result


def prediction_norm(nodes):
    points = sorted(set([D(0), *nodes, D(1)]))
    candidates = list(points)
    for left, right in zip(points, points[1:]):
        if left == right:
            continue
        mid = (left + right) / 2
        co = [D(0)] * 3
        for i, x in enumerate(nodes):
            y, z = [v for j, v in enumerate(nodes) if j != i]
            v = (1 + x) / ((x - y) * (x - z))
            sign = 1 if v * (mid - y) * (mid - z) >= 0 else -1
            for j, value in enumerate([v, -v * (y + z), v * y * z]):
                co[j] += sign * value
        a, b, c = co
        if a:
            disc = 1 - (b - c) / a
            if disc >= 0:
                for root in (-1 - disc.sqrt(), -1 + disc.sqrt()):
                    if left < root < right:
                        candidates.append(root)
    return max(sum(abs(v) for v in weights(nodes, t)) for t in candidates)


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    @staticmethod
    def point(v):
        return Interval(F(v), F(v))

    def __add__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -other if isinstance(other, Interval) else self + -self.point(other)

    def __rsub__(self, other):
        return self.point(other) + -self

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        vals = [x * y for x in (self.lo, self.hi) for y in (other.lo, other.hi)]
        return Interval(min(vals), max(vals))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        assert not other.lo <= 0 <= other.hi
        return self * Interval(1 / other.hi, 1 / other.lo)

    def sqrt(self):
        assert self.lo >= 0
        scale = 10**35
        lower = isqrt(self.lo.numerator * scale**2 // self.lo.denominator)
        upper = isqrt(self.hi.numerator * scale**2 // self.hi.denominator) + 1
        return Interval(F(lower, scale), F(upper, scale))


def main():
    for nodes in combinations([F(i, 10) for i in range(11)], 3):
        rows = lagrange_rows(nodes)
        a, b, c = nodes
        assert sum(abs(v) for v in rows[0]) == 2 * (1 + b) / ((b - a) * (c - b))
        for t in (F(1, 5), F(3, 8), F(3, 4)):
            w = weights(nodes, t)
            assert sum(w) == 1
            assert sum(wi * 2 * x / (1 + x) for wi, x in zip(w, nodes)) == 2 * t / (1 + t)
    print('165 rational triples: coefficient-row identity and reproduction PASS')

    r = D(2).sqrt()
    full = [D(0), r - 1, D(1)]
    inner = [D('0.1'), D('2.09').sqrt() - 1, D('0.9')]
    norm_full = 1 + 2 * r / ((r.sqrt() + 1)**2 * (r + 1))
    for nodes, expected in [(full, norm_full),
                            (inner, 1 + D('0.09') * (75 + 5 * D(209).sqrt()) / 8),
                            ([D(0), D('0.25'), D('0.5')], D(11))]:
        actual = prediction_norm(nodes)
        assert abs(actual - expected) < D('1e-45')
        print('Analytic-extrema prediction norm:', str(actual)[:24])
    for nodes in combinations([D(i) / 8 for i in range(9)], 3):
        assert prediction_norm(nodes) >= norm_full - D('1e-45')
    print('84 grid triples: no contradiction to analytic global bound PASS')

    # Every operation in this primal/dual certificate has rational outward bounds.
    inodes = [Interval.point(0), Interval.point(2).sqrt() - 1, Interval.point(1)]
    hold = [F(1, 5), F(3, 8), F(3, 4)]
    w = [weights(inodes, Interval.point(t)) for t in hold]
    u = [[v * v for v in row] for row in w]
    pi = list(map(F, ['0.4810793581630027', '0.12203417601129614', '0.39688646582570114']))
    alloc = list(map(F, ['0.18920827701248713', '0.568204554483491', '0.2425871685040217']))
    pi_total, alloc_total = sum(pi), sum(alloc)
    pi, alloc = [v / pi_total for v in pi], [v / alloc_total for v in alloc]
    root_sum = sum(sum(pi[j] * u[j][i] for j in range(3)).sqrt() for i in range(3))
    lower = (root_sum * root_sum).lo
    upper = max(sum(u[j][i] / alloc[i] for i in range(3)).hi for j in range(3))
    assert 0 < upper - lower < F(1, 10**7)
    print('RIGOROUS allocation optimum enclosure:', float(lower), float(upper))
    print('RIGOROUS allocation primal-dual gap <', float(upper - lower))

    k = 2 * (1 / (F(28, 100) * F(84, 100))
             + 1 / (F(28, 100) * F(48, 100))
             + 1 / (F(48, 100) * F(84, 100)))
    assert k < 31
    eta, beta, omega = D('.2'), D('.05'), D('.2')
    ceil = lambda x: int(x.to_integral_value(rounding='ROUND_CEILING'))
    train = ceil(32 * norm_full**2 / eta**2 * (18 / beta).ln())
    m = ceil((3 / beta).ln() / -(1 - omega).ln())
    repeats = ceil(8 / eta**2 * (6 * m / beta).ln())
    assert (train, m, repeats, 3 * train + m * repeats) == (7293, 19, 1547, 51272)
    print('UNKNOWN anchor bound:', k, '<31; budget:', 3 * train + m * repeats)

    probes = [F(0), F(1, 3), F(2, 3), F(1)]
    coefficients = [-1, 4, -5, 2]
    for fn in (lambda x: 2 * x / (1 + x), lambda x: x,
               lambda x: F(1, 2), lambda x: F(2, 3)):
        assert sum(c * fn(x) for c, x in zip(coefficients, probes)) == 0
    eps = F(1, 5)
    attack = lambda x: F(1, 2) + eps * x**3 / (1 + x)
    assert sum(c * attack(x) for c, x in zip(coefficients, probes)) == 2 * eps / 9
    print('NEW four-query contrast: catalogue identity and outside-family attack PASS')
    print('PASS; rational interval bounds certify allocation; no empirical trap data')


if __name__ == '__main__':
    main()
