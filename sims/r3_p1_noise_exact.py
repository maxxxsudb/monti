from fractions import Fraction as F
from itertools import product
from math import prod


def value(priors, good, bad, visible):
    return sum(
        max(priors[t] * prod(
            (good[j] if j == t else bad[j]) if result else
            1 - (good[j] if j == t else bad[j])
            for j, result in zip(visible, results)
        ) for t in range(3))
        for results in product((0, 1), repeat=len(visible))
    )


priors = [F(1, 3)] * 3
g, b = F(9, 10), F(1, 10)
for h in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
    gh, bh = g + (1 - g) * h, b + (1 - b) * h
    actual = value(priors, [gh, gh, g], [bh, bh, b], [0, 1, 2])
    linear = F(21, 25) - F(6, 25) * h
    print(f"h={h}: enumerated={actual}, formula={linear}")
print("erase A:", value(priors, [g] * 3, [b] * 3, [1, 2]))
unequal = [F(4, 5), F(1, 10), F(1, 10)]
print("unequal full:", value(unequal, [g] * 3, [b] * 3, [0, 1, 2]))
print("unequal erase A:", value(unequal, [g] * 3, [b] * 3, [1, 2]))
good, bad = [g, F(1, 2), F(1, 2)], [b, F(1, 2), F(1, 2)]
print("heterogeneous full:", value(priors, good, bad, [0, 1, 2]))
print("heterogeneous erase A:", value(priors, good, bad, [1, 2]))
