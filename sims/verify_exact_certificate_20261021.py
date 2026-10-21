"""Independent nine-bit verification of the supplied minimax certificate."""
from fractions import Fraction as F
from itertools import product
from math import comb


def main():
    names = ("N", "L", "W", "E", "LW")
    probabilities = ((F(1),) * 3, (F(9, 10), F(1, 10), F(1, 10)),
                     (F(1, 10), F(9, 10), F(1, 10)),
                     (F(1, 10), F(1, 10), F(9, 10)),
                     (F(9, 100), F(9, 100), F(1, 100)))
    ratio, anchor = F(91273273091, 729000000000), F(729, 1000000000)
    z = 1 / (1 + 3 * ratio + anchor * ratio)
    y = ratio * z
    prior = (anchor * y, y, y, y, z)
    assert all(p > 0 for p in prior) and sum(prior) == 1
    randomizations = {
        (0, 2, 0): (2, 4, F(166772659224244268732865365, 177646534311799495515253833)),
        (2, 0, 0): (1, 4, F(159310463205922869055269013, 177646534311799495515253833)),
        (3, 0, 3): (1, 3, F(611976287197017606944062, 731055696756376524754131)),
        (3, 3, 3): (0, 2, F(319970344592073815640, 334273295270405361113)),
    }
    overrides = {(2, 2, 2): 2, (3, 3, 0): 2, (3, 3, 1): 2}
    mass, correct = [F(0)] * 5, [F(0)] * 5
    bayes_correct = F(0)
    # No binomial count likelihoods: enumerate all 2^9 raw answer histories.
    for answers in product((0, 1), repeat=9):
        counts = tuple(sum(answers[3 * i:3 * i + 3]) for i in range(3))
        likelihood = []
        for ps in probabilities:
            prob = F(1)
            for i, bit in enumerate(answers):
                p = ps[i // 3]
                prob *= p if bit else 1 - p
            likelihood.append(prob)
        weighted = [prior[i] * likelihood[i] for i in range(5)]
        winners = {i for i, value in enumerate(weighted) if value == max(weighted)}
        bayes_correct += max(weighted)
        decision = [F(0)] * 5
        if counts in randomizations:
            first, second, probability = randomizations[counts]
            assert 0 <= probability <= 1 and {first, second} <= winners
            decision[first], decision[second] = probability, 1 - probability
        else:
            chosen = overrides.get(counts, min(winners))
            assert chosen in winners
            decision[chosen] = 1
        assert all(p >= 0 for p in decision) and sum(decision) == 1
        for i in range(5):
            mass[i] += likelihood[i]
            correct[i] += likelihood[i] * decision[i]
    assert mass == [F(1)] * 5
    risks = [1 - value for value in correct]
    exact = F(14302950678331545473, 334273295270405361113)
    assert risks == [exact] * 5
    assert 1 - bayes_correct == exact
    print("512 raw answer histories: probability normalization and feasible rule PASS")
    print("All five risks:", dict(zip(names, map(str, risks))))
    print("Bayes lower bound = minimax rule upper bound =", exact)
    print("Percent:", format(float(100 * exact), ".12f"))

    for m in range(2, 41):
        C, Cp = comb(2 * m, m), comb(2 * m, m + 1)
        center = F(C * (C - 2), (C + 1) * (2 * C - 1))
        shift = F(Cp - 1, 2 * (Cp + 1))
        numerator = (m - 4) * C**2 + (2 * m + 3) * C + m + 1
        denominator = 2 * (C + 1) * (2 * C - 1) * (m * C + m + 1)
        assert shift - center == F(numerator, denominator)
        assert F(1, 2) - center == F(5 * C - 1, 2 * (C + 1) * (2 * C - 1))
        assert (shift > center) == (m >= 4)
    print("Exact branch-difference identity, center deficit and crossover for m=2..40 PASS")

    checks = 0
    for n in range(3, 23):
        best = F(0)
        for k in range(1, n + 1):
            denom = comb(n, k)
            for a in range(1, n):
                for b in range(a + 1, n + 1):
                    def uv(w):
                        u = F(comb(w, k) if w >= k else 0, denom)
                        v = 1 - F(comb(n - w, k) if n - w >= k else 0, denom)
                        return u, v
                    ua, va = uv(a)
                    ub, vb = uv(b)
                    pf, pw = F(b, a + b), vb / (va + vb)
                    if ua:
                        pb = ub / (ua + ub)
                        assert pb >= pf >= pw
                        best = max(best, pb - pw)
                    else:
                        assert pf >= pw
                        assert pf - pw <= F(n - 1, 2 * (n + 1))
                    checks += 1
        if n % 2:
            C = comb(n, n // 2)
            maximum = F(C - 1, 2 * (C + 1))
        else:
            C, Cp = comb(n, n // 2), comb(n, n // 2 + 1)
            maximum = max(F(C * (C - 2), (C + 1) * (2 * C - 1)),
                          F(Cp - 1, 2 * (Cp + 1)))
        assert best == maximum
        assert maximum >= F(n - 1, 2 * (n + 1))
    print("General-composition checks and extension to common-k F/W/B:", checks, "PASS")
    print("PASS; finite checks supplement the general proof")


if __name__ == "__main__":
    main()
