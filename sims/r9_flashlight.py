from fractions import Fraction as F
from itertools import permutations
from random import Random


def outcomes(order, lamp_life=1.0, battery_life=2.0):
    lives = {'W': (3600.0, 3600.0),
             'L': (lamp_life, 3600.0),
             'B': (3600.0, battery_life)}
    a, x, y = order
    tx, ty = min(lives[x]), min(lives[y])
    stop = min(tx, ty)
    assert tx != ty
    dead, live = (x, y) if tx < ty else (y, x)
    battery_dead = lives[dead][1] - stop
    battery_live = lives[live][1] - stop
    good_dead = battery_dead >= 60
    good_live = battery_live >= 60
    success_dead = min(lives[a][0], battery_dead) >= 60
    success_live = min(lives[a][0], battery_live) >= 60
    return (good_dead, good_live, success_dead, success_live), stop


totals = [F(0)] * 4
conditional = {}
for order in permutations('WLB'):
    values, stop = outcomes(order)
    for i, value in enumerate(values):
        totals[i] += F(int(value), 6)
    group = conditional.setdefault(stop, [])
    group.append(values)
assert totals == [F(2, 3), F(2, 3), F(2, 3), F(1, 3)]
print('Exact: quality(dead,live)=2/3,2/3; success(dead,live)=2/3,1/3.')
for stop, rows in sorted(conditional.items()):
    values = [sum(F(int(row[i]), len(rows)) for row in rows) for i in range(4)]
    print(f'Given time={stop:g}s: quality(dead,live)={values[:2]}; success={values[2:]}.')
assert [sum(F(int(row[i]), len(conditional[1])) for row in conditional[1])
        for i in (2, 3)] == [F(1), F(1, 2)]
assert all(not row[2] and not row[3] for row in conditional[2])

rng = Random(20261015)
n = 1_000_000
counts = [0] * 4
race_wins = 0
for _ in range(n):
    lamp_life = 2 * rng.random()
    battery_life = 4 * rng.random()
    race_wins += lamp_life < battery_life
    a = rng.randrange(3)
    order = [('W', 'L', 'B'), ('L', 'W', 'B'), ('B', 'W', 'L')][a]
    values, _ = outcomes(order, lamp_life, battery_life)
    for i, value in enumerate(values):
        counts[i] += value
expected = [F(7, 12), F(3, 4), F(7, 12), F(5, 12)]
print(f'Continuous lifetimes: lamp U(0,2), battery U(0,4); {n} trials.')
print(f'P(lamp fails earlier): MC={race_wins/n:.6f}; exact=3/4.')
for name, count, probability in zip(('quality_dead', 'quality_live', 'success_dead', 'success_live'),
                                   counts, expected):
    estimate = count / n
    tolerance = 5 * (float(probability*(1-probability)) / n)**0.5
    assert abs(estimate-float(probability)) < tolerance
    print(f'{name}: MC={estimate:.6f}, exact={probability}.')
print('All checks passed. Analytic derivation is in rounds/r9-flashlight.md.')
