from fractions import Fraction as Q
from itertools import product


def value(priors, a, b, checked, penalty=None):
    result = Q(0)
    for xs in product((0, 1), repeat=len(checked)):
        masses = []
        for h, prior in enumerate(priors):
            w = prior
            for i, x in zip(checked, xs):
                chance = a if i == h else b
                w *= chance if x else 1 - chance
            masses.append(w)
        best = max(masses)
        result += best if penalty is None else max(Q(0), (1 + penalty) * best - penalty * sum(masses))
    return result


priors = (Q(1, 7), Q(3, 7), Q(3, 7))
a, b = Q(3, 4), Q(1, 4)
assert value(priors, a, b, (1, 2)) == Q(9, 14)
assert value(priors, a, b, (0, 1, 2)) == Q(153, 224)
assert 3 * value(priors, a, b, (1, 2)) - 2 == -Q(1, 14)
assert 3 * value(priors, a, b, (0, 1, 2)) - 2 == Q(11, 224)
assert value(priors, a, b, (1, 2), Q(2)) == Q(15, 56)
assert value(priors, a, b, (0, 1, 2), Q(2)) == Q(15, 56)

count = 0
for c in (Q(3, 2), Q(2), Q(3), Q(5)):
    for a in (Q(3, 4), Q(4, 5), Q(9, 10)):
        b = 1 - a
        low, high = (1 - a) / (1 - b), a / b
        z = low / high
        upper = min(2 * c * z, 1 / c - z, Q(1))
        if upper <= z:
            continue
        for t in (Q(1, 4), Q(1, 2), Q(3, 4)):
            r = z + t * (upper - z)
            priors = (r / (r + 2), 1 / (r + 2), 1 / (r + 2))
            partial = value(priors, a, b, (1, 2), c)
            full = value(priors, a, b, (0, 1, 2), c)
            assert partial == full > 0
            assert value(priors, a, b, (0, 1, 2)) > value(priors, a, b, (1, 2))
            count += 1

print(f"PASS: original -2 example and {count} general-penalty mirror cases")
