from fractions import Fraction
from itertools import permutations
import random

types = {'W': (1, 1), 'P': (1, 0), 'C': (0, 1)}
labels = ('supply B good', 'supply D good', 'assembly B', 'assembly D')

def outcome(state, discarded):
    survivor = 3 - discarded
    cpu = types[state[0]][0]
    sb = types[state[survivor]][1]
    sd = types[state[discarded]][1]
    return sb, sd, cpu and sb, cpu and sd

for rule in ('uniform', 'discard C first'):
    exact = [Fraction(0) for _ in labels]
    for state in permutations('WPC'):
        bad = [j for j in (1, 2) if state[j] != 'W']
        allowed = bad if rule == 'uniform' else [next((j for j in bad if state[j] == 'C'), bad[0])]
        for discarded in allowed:
            for i, value in enumerate(outcome(state, discarded)):
                exact[i] += Fraction(bool(value), 6 * len(allowed))
    rng = random.Random(4142027)
    n = 1_000_000
    count = [0 for _ in labels]
    for _ in range(n):
        state = rng.sample('WPC', 3)
        bad = [j for j in (1, 2) if state[j] != 'W']
        discarded = rng.choice(bad) if rule == 'uniform' else next((j for j in bad if state[j] == 'C'), bad[0])
        for i, value in enumerate(outcome(state, discarded)):
            count[i] += value
    print(rule)
    for label, value, observed in zip(labels, exact, count):
        print(f'{label}: exact={value}, MC={observed/n:.6f}')
