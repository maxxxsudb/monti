"""Exact checks for the October 19 counterintuition review."""

from fractions import Fraction as F
from itertools import product


def enumerate_observation(alpha):
    total = F(0)
    event = F(0)
    prize_c = F(0)
    informed = F(0)
    for knows, type_weight in ((True, alpha), (False, 1 - alpha)):
        for prize in "ABC":
            doors = [d for d in "BC" if not knows or d != prize]
            for opened in doors:
                weight = type_weight / 3 / len(doors)
                total += weight
                if opened == "B" and prize != "B":
                    event += weight
                    prize_c += weight * (prize == "C")
                    informed += weight * knows
    assert total == 1
    return event, prize_c / event, informed / event


def buy_set(probability, price):
    if probability == price:
        return {False, True}
    return {probability > price}


def integrated_regret(p, q):
    lo, hi = sorted((p, q))
    if q > p:
        return (hi**2 - lo**2) / 2 - p * (hi - lo)
    return p * (hi - lo) - (hi**2 - lo**2) / 2


alphas = sorted({F(k, n) for n in range(1, 51) for k in range(n + 1)})
for alpha in alphas:
    event, p, posterior_type = enumerate_observation(alpha)
    q = F(1, 2) + alpha / 6
    assert event == (2 + alpha) / 6
    assert p == (1 + alpha) / (2 + alpha)
    assert posterior_type == 3 * alpha / (2 + alpha)
    assert p - q == alpha * (1 - alpha) / (6 * (2 + alpha))
    assert (p > F(3, 5)) == (alpha > F(1, 2))
    assert (q > F(3, 5)) == (alpha > F(3, 5))
    assert buy_set(p, F(3, 5)).isdisjoint(buy_set(q, F(3, 5))) == (
        F(1, 2) < alpha < F(3, 5)
    )
    assert p >= 1 - p
    assert (p > 1 - p) == (alpha > 0)

expected = {
    F(0): (F(1, 2), F(1, 2), False),
    F(1, 3): (F(4, 7), F(5, 9), False),
    F(11, 20): (F(31, 51), F(71, 120), True),
    F(2, 3): (F(5, 8), F(11, 18), True),
    F(1): (F(2, 3), F(2, 3), True),
}
for alpha, (p_gold, q_gold, buy_gold) in expected.items():
    _, p, _ = enumerate_observation(alpha)
    q = F(1, 2) + alpha / 6
    assert (p, q, p > F(3, 5)) == (p_gold, q_gold, buy_gold)
assert 100 * F(31, 51) - 60 == F(40, 51)
assert 100 * F(71, 120) - 60 == -F(5, 6)
assert 100 * F(2, 3) - 60 == F(20, 3)
assert 100 * F(1, 2) - 60 == -10

grid = [F(k, 30) for k in range(31)]
for p, q in product(grid, repeat=2):
    assert integrated_regret(p, q) == (p - q) ** 2 / 2

# The midpoint minimizes squared loss for an indistinguishable balanced pair.
for p1, p2, reported in product(grid, repeat=3):
    midpoint = (p1 + p2) / 2
    mse = ((reported - p1) ** 2 + (reported - p2) ** 2) / 2
    assert mse == (reported - midpoint) ** 2 + (p1 - p2) ** 2 / 4

print(f"PASS: {len(alphas)} exact protocol mixtures; 5 pilot rows; "
      f"{len(grid) ** 2} price-loss pairs; {len(grid) ** 3} compression-loss cases")
