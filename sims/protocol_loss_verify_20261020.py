"""Independent exact audit of protocol-loss examples and search scopes."""
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb
from functools import lru_cache


def likelihood(n, w, mode, k):
    if mode == "F":
        return F(w, n)
    if mode == "W":
        return 1 - F(comb(n - w, k) if n - w >= k else 0, comb(n, k))
    return F(comb(w, k) if w >= k else 0, comb(n, k))


def brute(n, w, mode, k):
    wins = total = 0
    for path in permutations(range(n), k):
        for position in path:
            white = position < w
            if (mode == "W" and white) or (mode == "B" and not white):
                break
        wins += white
        total += 1
    return F(wins, total)


def posterior(prior, low, high):
    return prior * high / (prior * high + (1 - prior) * low)


def enumeration():
    unrestricted = [F(0), F(1, 6), F(1, 4), F(5, 14), F(9, 22)]
    common_limit = [F(0), F(1, 6), F(1, 4), F(24, 77), F(9, 22)]
    same_stop = [F(0), F(0), F(1, 4), F(24, 77), F(9, 22)]
    count = 0
    for n in range(1, 6):
        for w in range(n + 1):
            for k in range(1, n + 1):
                for mode in "FWB":
                    assert brute(n, w, mode, k) == likelihood(n, w, mode, k)
                    count += 1
        maxima = [F(0)] * 3
        for low, high in combinations(range(n + 1), 2):
            rules = [(mode, k) for k in range(1, n + 1) for mode in "FWB"
                     if likelihood(n, low, mode, k) > 0]
            for (a, ka), (b, kb) in combinations(rules, 2):
                pa = posterior(F(1, 2), likelihood(n, low, a, ka),
                               likelihood(n, high, a, ka))
                pb = posterior(F(1, 2), likelihood(n, low, b, kb),
                               likelihood(n, high, b, kb))
                gap = abs(pa - pb)
                maxima[0] = max(maxima[0], gap)
                if ka == kb:
                    maxima[1] = max(maxima[1], gap)
                    if {a, b} == {"W", "B"}:
                        maxima[2] = max(maxima[2], gap)
        assert maxima == [unrestricted[n - 1], common_limit[n - 1], same_stop[n - 1]], maxima
        print(f"n={n}: free-k={maxima[0]}, common-k={maxima[1]}, W/B-common-k={maxima[2]}")
    print(f"Exact ordered-path checks: {count}")


def formulas():
    assert posterior(F(1, 2), F(1, 10), F(1)) == F(10, 11)
    assert posterior(F(1, 4), F(1, 10), F(1)) == F(10, 13)
    for error in [F(0), F(1, 10), F(7, 34), F(1, 4)]:
        p = posterior(F(1, 4), F(1, 10) + F(4, 5) * error, 1 - error)
        assert p == 10 * (1 - error) / (13 + 14 * error)
        assert (p > F(1, 2)) == (error < F(7, 34))
    # Hidden independent fair protocol: normalize the mixture likelihood first.
    assert posterior(F(1, 2), (F(1, 3) + 1) / 2, F(1)) == F(3, 5)
    assert (F(1, 2) * F(2, 3)) / (F(1, 2) * F(2, 3) + F(1, 2)) == F(2, 5)
    for t in [F(1, 2), F(1, 3), F(1, 10), F(1, 100)]:
        s, prior = t * t, t / (1 + t)
        p = posterior(prior, s, F(1))
        assert p == 1 / (1 + t)
        assert p - prior == (1 - t) / (1 + t)
        assert prior + (1 - prior) * s == t
    print("Five-ticket probabilities, noise threshold, hidden protocol and rare-event cost: PASS")


def covariance_and_criterion():
    vectors = [v for v in product([F(0), F(1, 2), F(1)], repeat=3) if any(v)]
    ys = (0, 0, 1)
    mu = (F(1, 6), F(1, 3), F(1, 2))
    count = 0
    for a in vectors:
        for b in vectors:
            cross = all(a[i] * b[j] == b[i] * a[j]
                        for i in range(3) for j in range(3) if ys[i] != ys[j])
            proportional = all(a[i] * b[j] == b[i] * a[j]
                               for i in range(3) for j in range(3))
            one_layer = len({ys[i] for i in range(3) if a[i] + b[i] > 0}) == 1
            assert cross == (proportional or one_layer)
            A = sum(mu[i] * a[i] for i in range(3))
            B = sum(mu[i] * b[i] for i in range(3))
            rho = [mu[i] * (a[i] + b[i]) / (A + B) for i in range(3)]
            ts = [b[i] / (a[i] + b[i]) if a[i] + b[i] else F(0) for i in range(3)]
            q = B / (A + B)
            covariance = sum(rho[i] * ys[i] * ts[i] for i in range(3)) - sum(
                rho[i] * ys[i] for i in range(3)) * q
            difference = sum(mu[i] * ys[i] * b[i] for i in range(3)) / B - sum(
                mu[i] * ys[i] * a[i] for i in range(3)) / A
            assert difference == covariance / (q * (1 - q))
            count += 1
    print(f"Covariance and structural criterion: {count} exact cases PASS")


def master_audit():
    profiles = {
        "N": (1, 1, 1, 1), "L": (1, 0, 0, 1),
        "W": (0, 1, 0, 1), "E": (0, 0, 1, 0), "LW": (0, 0, 0, 1),
    }
    separating = []
    for size in range(1, 5):
        separating = [cols for cols in combinations(range(4), size)
                      if len({tuple(row[j] for j in cols) for row in profiles.values()}) == 5]
        if separating:
            break
    assert size == 3 and (0, 1, 3) in separating
    print("Five intervention profiles: minimum=3; IZ,IR,IZ+IR separates all")
    assert F(1, 5) - F(1, 10) == F(1, 10)
    assert F(1, 5) > F(1, 10) + F(1, 10) * F(1, 10)
    # A collision in one representation layer need not be an error at x0.
    f, g, answer = (0, 1), (0, 0), (0, 0)
    assert g[0] == g[1] and f[0] != f[1] and answer[0] == f[0]
    # The example's right derivative at 1/4 is 52/25, exceeding 2.
    derivative = 2 / (1 + F(1, 4)) ** 2 + F(4, 5)
    assert derivative == F(52, 25) and derivative > 2
    # A norm ball without a common continuity bound need not be compact.
    # Use only the repaired finite, Lipschitz-restricted classes in the report.
    print("TV scaling, pointwise witness and Lipschitz counterexamples: PASS")


def parity_checks():
    for n in range(2, 13):
        cross = same = F(0)
        for low, high in combinations(range(1, n + 1), 2):
            candidates = []
            for k in range(1, n + 1):
                within = []
                for mode in "FWB":
                    lo, hi = likelihood(n, low, mode, k), likelihood(n, high, mode, k)
                    if lo:
                        within.append(posterior(F(1, 2), lo, hi))
                if within:
                    same = max(same, max(within) - min(within))
                candidates.extend(within)
            if candidates:
                cross = max(cross, max(candidates) - min(candidates))
        C = comb(n, n // 2)
        expected_cross = F(C - 1, 2 * (C + 1))
        if n % 2:
            expected_same = expected_cross
        elif n == 2:
            expected_same = F(1, 6)
        else:
            shifted = comb(n, n // 2 + 1)
            expected_same = max(F(C * (C - 2), (C + 1) * (2 * C - 1)),
                                F(shifted - 1, 2 * (shifted + 1)))
        assert (cross, same) == (expected_cross, expected_same)
        print(f"Parity finite check n={n}: cross={cross}, same={same}")


def dp_both_models():
    def make(labels):
        m = max(labels) + 1
        return tuple(tuple(F(9, 10) if j == label else F(1, 10 * (m - 1))
                           for j in range(m)) for label in labels)

    def run(prior_label, price, include_identifier):
        kernels = [make((0, 1, 1, 0)), make(prior_label)]
        if include_identifier:
            kernels.append(make((0, 1, 2, 3)))

        @lru_cache(None)
        def dp(b, t):
            best = 1 - max(b)
            if not t:
                return best
            for kernel in kernels:
                value = price
                for col in zip(*kernel):
                    weights = tuple(x * y for x, y in zip(b, col))
                    mass = sum(weights)
                    value += mass * dp(tuple(x / mass for x in weights), t - 1)
                best = min(best, value)
            return best
        return [dp((F(1, 4),) * 4, t) for t in range(1, 6)]

    for price in (F(0), F(1, 20), F(1, 10)):
        a = run((0, 1, 0, 2), price, True)
        b = run((0, 0, 0, 1), price, True)
        assert a == b
        print("Both Q1 models, full menu, cost", price, ":", ", ".join(map(str, a)))
    a = run((0, 1, 0, 2), F(1, 10), False)
    b = run((0, 0, 0, 1), F(1, 10), False)
    assert a == [F(17, 40)] + [F(117, 400)] * 4
    assert b == [F(13, 20)] + [F(13, 25)] * 4
    print("Without identifier: Q1-new", a, "; Q1-r64", b)


if __name__ == "__main__":
    enumeration()
    formulas()
    covariance_and_criterion()
    master_audit()
    parity_checks()
    dp_both_models()
    print("ALL CHECKS PASSED; finite checks do not replace general proofs")
