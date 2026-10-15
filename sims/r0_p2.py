import random
from fractions import Fraction

rng = random.Random(20261014)
n = 1_000_000
early = late = 0
for _ in range(n):
    target = rng.randrange(4)
    opened = rng.choice([i for i in range(1, 4) if i != target])
    survivors = [i for i in range(1, 4) if i != opened]
    new_protected = rng.choice(survivors)
    early += target != new_protected
    late += target != 0
print('current leader:', 'exact', Fraction(5, 8), 'MC', early / n)
print('wait:', 'exact', Fraction(3, 4), 'MC', late / n)

accepted_once = good_once = accepted_twice = good_twice = 0
for _ in range(n):
    good = rng.random() < .5
    p = .9 if good else .3
    if rng.random() < p:
        accepted_once += 1
        good_once += good
    elif rng.random() < p:
        accepted_twice += 1
        good_twice += good
print('one test:', 'exact', Fraction(3, 4), 'MC', good_once / accepted_once)
print('two tests:', 'exact', Fraction(3, 10), 'MC', good_twice / accepted_twice)

events = professional_b = 0
for _ in range(n):
    b = rng.random() < .5
    # A has answers; B passes exactly when professional.
    if b:
        events += 1
        professional_b += b
print('cheat sheet:', 'exact', 1, 'MC', professional_b / events)
