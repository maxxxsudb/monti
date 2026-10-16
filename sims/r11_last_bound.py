from fractions import Fraction as Q
from itertools import product


def exact_values(p0, p1, n, skipped=1):
    ratios = tuple(b / a for a, b in zip(p0, p1))
    full = Q(0)
    partial = Q(0)
    for xs in product(range(len(p0)), repeat=n):
        weight = Q(1)
        for x in xs:
            weight *= p0[x]
        full += weight * max(ratios[x] for x in xs) / n
    for xs in product(range(len(p0)), repeat=n - skipped):
        weight = Q(1)
        for x in xs:
            weight *= p0[x]
        partial += weight * max((Q(1), *(ratios[x] for x in xs))) / n
    return full, partial


def integrated_gap(p0, p1, n, skipped=1):
    pairs = sorted(zip((b / a for a, b in zip(p0, p1)), p0))
    endpoints = sorted({Q(0), Q(1), *(x for x, _ in pairs)})
    value = Q(0)
    for left, right in zip(endpoints, endpoints[1:]):
        cdf = sum((p for x, p in pairs if x <= left), Q(0))
        if right <= 1:
            value -= (right - left) * cdf**n
        else:
            value += (right - left) * (cdf ** (n - skipped) - cdf**n)
    return value / n


def compositions(total, positive=False):
    start = int(positive)
    for a in range(start, total + 1):
        for b in range(start, total - a + 1):
            c = total - a - b
            if c >= start:
                yield tuple(Q(x, total) for x in (a, b, c))


def check():
    count = 0
    for p0 in compositions(5, positive=True):
        for p1 in compositions(5):
            ratios = {b / a for a, b in zip(p0, p1)}
            for n in range(2, 6):
                full, partial = exact_values(p0, p1, n)
                gap = full - partial
                assert gap == integrated_gap(p0, p1, n)
                assert gap >= 0
                assert (gap == 0) == (len(ratios) <= 2)
                assert (Q(n * n, n - 1) * gap) ** (n - 1) < Q(1, n)
                count += 1

    construction_count = 0
    for n in range(2, 6):
        for a in (Q(1, 3), Q(1, 2), Q(2, 3)):
            for eps in (Q(1, 20), Q(1, 10)):
                p0 = (a, 1 - a - eps, eps)
                p1 = (Q(0), 1 - a - eps, a + eps)
                for skipped in range(1, n + 1):
                    full, partial = exact_values(p0, p1, n, skipped)
                    gap = full - partial
                    predicted = (
                        a / eps * (1 - eps) ** (n - skipped)
                        * (1 - (1 - eps) ** skipped) - a**n
                    ) / n
                    assert gap == predicted == integrated_gap(p0, p1, n, skipped)
                    scaled = Q(n * n, skipped * (n - 1)) * gap
                    assert scaled ** (n - 1) < Q(skipped, n)
                    construction_count += 1

    assert Q(1, 2) - Q(17, 36) == Q(1, 36)
    print(f"PASS: {count} exact laws, {construction_count} sharpness constructions")


if __name__ == "__main__":
    check()
