from fractions import Fraction as F
from itertools import product
from functools import reduce
import random

rng = random.Random(20261017)
for h in (F(0), F(1, 2), F(1)):
    weights = {}
    for x in product((0, 1), repeat=3):
        weights[x] = []
        for t in range(3):
            ps = [F(9,10) if j == t else F(1,10) for j in range(3)]
            ps = [p + (1-p)*h if j < 2 else p for j,p in enumerate(ps)]
            weights[x].append(F(1,3)*reduce(lambda a,b:a*b, (p if bit else 1-p for bit,p in zip(x,ps)), F(1)))
    policy = {x:max(range(3), key=lambda t:weights[x][t]) for x in weights}
    exact = sum(max(w) for w in weights.values())
    wins=0
    for _ in range(1_000_000):
        t=rng.randrange(3)
        x=[]
        for j in range(3):
            passed=rng.random() < (.9 if j==t else .1)
            if j < 2 and not passed:
                passed=rng.random() < float(h)
            x.append(int(passed))
        wins += policy[tuple(x)] == t
    print('help', h, 'exact', exact, 'MC', wins/1_000_000)
    print('scaled likelihood-max contributions', [max(weights[x])*12000 for x in weights])
