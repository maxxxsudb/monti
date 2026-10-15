from fractions import Fraction as F
import random

rng = random.Random(20261016)
def prime_factors(n):
    return [p for p in range(2, n + 1) if n % p == 0 and all(p % d for d in range(2, int(p**.5) + 1))]

cases = [
    ('prime', list(range(2, 31)), prime_factors, 2, lambda n:n%3==0),
    ('bit', list(range(1,16)), lambda n:[b for b in [1,2,4,8] if n&b], 8, lambda n:n==15),
]
for name, states, messages, observed, target in cases:
    choices = {n: messages(n) for n in states}
    weights = {n: F(1,len(ms)) if observed in ms else F(0) for n,ms in choices.items()}
    denominator = sum(weights.values())
    numerator = sum(w for n,w in weights.items() if target(n))
    exact = numerator/denominator
    accepted=hit=0
    for _ in range(1_000_000):
        n=rng.choice(states)
        if rng.choice(choices[n])==observed:
            accepted+=1
            hit+=target(n)
    print(name, 'exact', exact, 'MC', hit/accepted, 'accepted', accepted, 'weights', weights)
