"""Проверки центральных чисел; только стандартная библиотека."""
from fractions import Fraction
from random import Random

N = 1_000_000
rng = Random(20261014)


def report(label, exact, hits, total=N):
    empirical = hits / total
    print(f"{label}: exact={exact} ({float(exact):.6f}), MC={empirical:.6f}, n={total}")
    assert abs(empirical - float(exact)) < 0.005


stay = 0
for _ in range(N):
    fixed = rng.randrange(4) != 0
    winner = rng.randrange(3) if fixed else 0
    stay += winner == 0
report("temporal threshold stay, lambda=3/4 phi=1", Fraction(1, 2), stay)

hits = 0
for _ in range(N):
    target = rng.randrange(100)
    if target < 20:
        survivors = rng.sample(range(20, 100), 5)
    else:
        survivors = [target] + rng.sample([i for i in range(20, 100) if i != target], 4)
    hits += rng.choice(survivors) == target
report("one survivor N=100 k=20 m=5", Fraction(4, 25), hits)

hits = total = 0
for _ in range(N):
    target = rng.randrange(4)
    survivors = ((1, 2), (1, 2), (1, 3), (2, 3))[target]
    if survivors == (1, 2):
        total += 1
        hits += target == 0
report("biased labelled survivors, own target", Fraction(1, 2), hits, total)

hits = total = 0
for _ in range(N):
    target = rng.randrange(3)
    survivor = rng.randrange(1, 3)
    if survivor == 1:
        total += 1
        hits += target == survivor
report("exchangeable blind filter survivor", Fraction(1, 3), hits, total)
