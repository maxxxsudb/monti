from fractions import Fraction
from itertools import permutations
import random

types = {'W': (1, 1), 'P': (1, 0), 'C': (0, 1)}
exact = [Fraction(0) for _ in range(4)]
for state in permutations('WPC'):
    bad = [j for j in (1, 2) if state[j] != 'W']
    for removed in bad:
        weight = Fraction(1, 6 * len(bad))
        other = 3 - removed
        cpu_a, supply_a = types[state[0]]
        cpu_b, supply_b = types[state[other]]
        supply_donor = types[state[removed]][1]
        outcomes = (
            (cpu_a and supply_donor) or (cpu_b and supply_b),
            supply_a and (cpu_a or cpu_b),
            supply_b and (cpu_a or cpu_b),
            cpu_a and supply_b,
        )
        for i, value in enumerate(outcomes):
            exact[i] += weight * bool(value)

rng = random.Random(4142026)
n = 1_000_000
counts = [0] * 4
for _ in range(n):
    state = rng.sample('WPC', 3)
    removed = rng.choice([j for j in (1, 2) if state[j] != 'W'])
    other = 3 - removed
    ca, pa = types[state[0]]
    cb, pb = types[state[other]]
    pd = types[state[removed]][1]
    outcomes = ((ca and pd) or (cb and pb), pa and (ca or cb), pb and (ca or cb), ca and pb)
    for i, value in enumerate(outcomes):
        counts[i] += bool(value)

for label, e, count in zip(('donor, at least one works', 'shared reserved supply', 'shared survivor supply', 'CPU reserve + supply survivor'), exact, counts):
    print(f'{label}: exact={e}, MC={count/n:.6f}')
