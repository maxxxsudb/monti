"""Exact checks of contrast decomposition and two/three-probe results."""
from fractions import Fraction as F
from itertools import product, combinations


def f(alpha):
    return 2 * alpha / (1 + alpha)


def p(alpha, weights):
    lp, le, lc = weights
    norm = f(alpha)
    return norm + lp * (alpha - norm) + le * (F(1, 2) - norm) + lc * (F(2, 3) - norm)


def recover(observations):
    y0, yq, yh = observations[0], observations[1] - F(2, 5), observations[2] - F(2, 3)
    return (8 * y0 - 20 * yq + 12 * yh,
            -8 * y0 + 20 * yq - 18 * yh,
            F(15, 2) * y0 - 15 * yq + F(27, 2) * yh)


def main():
    values = [F(i, 4) for i in range(5)]
    count = 0
    for p0, p1, m0, m1 in product(values, repeat=4):
        contrast = (m1 - m0) - (p1 - p0)
        e0, e1 = m0 - p0, m1 - p1
        common = (e0 + e1) / 2
        assert (abs(e0) + abs(e1)) / 2 >= abs(contrast) / 2
        assert (e0**2 + e1**2) / 2 == common**2 + contrast**2 / 4
        count += 1
    print('Contrast lower bound and squared-error identity:', count, 'exact cases PASS')

    count = 0
    for i, j, k in product(range(11), repeat=3):
        if i + j + k > 10:
            continue
        weights = (F(i, 10), F(j, 10), F(k, 10))
        observations = [p(alpha, weights) for alpha in (F(0), F(1, 4), F(1, 2))]
        inferred = recover(observations)
        assert inferred == weights
        for alpha in (F(1, 5), F(3, 8), F(3, 4)):
            assert p(alpha, inferred) == p(alpha, weights)
        count += 1
    print('Three-probe inversion and held-out predictions:', count, 'simplex points PASS')

    left, right = (F(0), F(1, 2), F(0)), (F(2, 5), F(1, 10), F(3, 10))
    assert all(p(alpha, left) == p(alpha, right) for alpha in (F(0), F(1, 2)))
    assert (p(F(1, 4), left), p(F(1, 4), right)) == (F(9, 20), F(43, 100))
    print('Two-probe ambiguity for simultaneous mixtures: PASS')

    eta = F(1, 20)
    strengths = {F(i, 20) for i in range(1, 21)} | {2 * eta, F(3, 2) * eta, 6 * eta}
    vectors = {'N': [(F(0), F(0))], 'P': [], 'E': [], 'C': []}
    for strength in strengths:
        if strength >= 6 * eta:
            vectors['P'].append((F(0), -strength / 6))
        if strength >= 2 * eta:
            vectors['E'].append((strength / 2, -strength / 6))
        if strength >= F(3, 2) * eta:
            vectors['C'].append((F(2, 3) * strength, F(0)))
    gaps = [max(abs(x - y) for x, y in zip(a, b))
            for (_, va), (_, vb) in combinations(vectors.items(), 2)
            for a in va for b in vb]
    assert min(gaps) == eta / 3
    print('Two-probe interclass margin on a conservative finite subfamily:', eta / 3, 'PASS')
    print('PASS; exact checks supplement the general proofs, not empirical validation')


if __name__ == '__main__':
    main()
