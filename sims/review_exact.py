from fractions import Fraction as F
from itertools import permutations, product


def joint_reports(n, a, b, alphabet=(0, 1)):
    rows = []
    for outcomes in product(alphabet, repeat=n):
        weights = []
        for target in range(n):
            weight = F(1, n)
            for i, outcome in enumerate(outcomes):
                probabilities = a if i == target else b
                weight *= probabilities[outcome]
            weights.append(weight)
        rows.append((outcomes, weights))
    return rows


def value(rows, k, reward=None):
    grouped = {}
    for outcomes, weights in rows:
        total = grouped.setdefault(outcomes[:k], [F(0)] * len(weights))
        for i, weight in enumerate(weights):
            total[i] += weight
    if reward is None:
        return sum((max(weights) for weights in grouped.values()), F(0))
    return sum(
        (max(F(0), (1 + reward) * max(w) - reward * sum(w))
         for w in grouped.values()), F(0)
    )


def binary_rows(n, a, b):
    return joint_reports(n, (1-a, a), (1-b, b))


checks = 0
parameters = [(F(0), F(0)), (F(1, 5), F(1, 10)),
              (F(3, 4), F(1, 4)), (F(9, 10), F(1, 10)),
              (F(1), F(1, 2)), (F(1), F(0)),
              (F(1), F(1)), (F(1, 2), F(1, 2)),
              (F(4, 5), F(1, 2))]
for n in range(2, 8):
    for a, b in parameters:
        rows = binary_rows(n, a, b)
        for k in range(n + 1):
            m = min(k, n - 1)
            expected = (a * sum(((1-b)**j for j in range(m)), F(0))
                        + (1-b)**m) / n
            assert value(rows, k) == expected, (n, a, b, k)
            checks += 1
print(f'Binary tests: {checks} exact comparisons passed (n=2..7).')

checks = 0
for n in range(2, 8):
    for q in [F(0), F(1, 3), F(1, 2), F(2, 3), F(1)]:
        rows = binary_rows(n, F(1), 1-q)
        full = q**(n-1)
        partial = (full + (n-1)*q**(n-2)*max(2*q-1, F(0))) / n
        assert value(rows, n, reward=2) == full
        assert value(rows, n-1, reward=2) == partial
        checks += 2
print(f'Abstention (+1/-2/0): {checks} exact comparisons passed.')

for r in [F(0), F(1, 4), F(1, 2), F(2, 3), F(3, 4), F(1)]:
    totals = [F(0)] * 4
    types = {'W': (1, 1), 'P': (1, 0), 'C': (0, 1)}
    for a, x, y in permutations(types):
        bad = [v for v in (x, y) if v != 'W']
        for d in bad:
            probability = (F(1) if len(bad) == 1
                           else r if d == 'C' else 1-r) / 6
            b = y if d == x else x
            cpu = types[a][0]
            psu_b, psu_d = types[b][1], types[d][1]
            for i, outcome in enumerate((psu_b, psu_d, cpu*psu_b, cpu*psu_d)):
                totals[i] += probability*outcome
    assert totals == [1-r/3, (1+r)/3, (2-r)/3, (1+r)/3], (r, totals)
print('Donor: 6 rational parameter values, all exact formulas passed.')

rows = binary_rows(3, F(3, 4), F(1, 4))


def binary_target_accuracy(rows, k):
    grouped = {}
    for outcomes, weights in rows:
        total = grouped.setdefault(outcomes[-k:], [F(0), F(0)])
        total[0] += weights[0]
        total[1] += sum(weights[1:])
    return sum((max(w) for w in grouped.values()), F(0))


assert value(rows, 3) == value(rows, 2) == F(5, 8)
assert binary_target_accuracy(rows, 3) == F(149, 192)
assert binary_target_accuracy(rows, 2) == F(35, 48)
print('Changed objective: 5/8 = 5/8; binary-query loss = 3/64, exact.')

ternary = joint_reports(2, (F(1, 5), F(2, 5), F(2, 5)),
                       (F(2, 5), F(2, 5), F(1, 5)), alphabet=(0, 1, 2))
assert value(ternary, 1) == F(3, 5)
assert value(ternary, 2) == F(16, 25)
print('Three-outcome counterexample: 3/5 -> 16/25; binary assumption needed.')

for g, b, h in [(F(9, 10), F(1, 10), F(1, 2)),
                (F(3, 4), F(1, 4), F(2, 3)),
                (F(1), F(1, 2), F(1, 4))]:
    gh, bh = g+(1-g)*h, b+(1-b)*h
    rows = []
    for outcomes in product((0, 1), repeat=3):
        weights = []
        for target in range(3):
            weight = F(1, 3)
            for i, outcome in enumerate(outcomes):
                p = (gh if i == target else bh) if i < 2 else (g if i == target else b)
                weight *= p if outcome else 1-p
            weights.append(weight)
        rows.append((outcomes, weights))
    assert value(rows, 3) == (1+(g-b)*(2-b-h*(1-b)))/3
print('Two masked tests: exact formula verified at 3 parameter triples.')
print('ALL CHECKS PASSED. Finite checks supplement, not replace, the written proofs.')
