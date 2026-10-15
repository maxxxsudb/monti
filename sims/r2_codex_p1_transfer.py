import random

random.seed(26101421)
n = 1_000_000
stay = switch = 0
for _ in range(n):
    token = random.randrange(3)
    inspected = random.choice((1, 2))
    if token == inspected:
        token = 0
    survivor = 3 - inspected
    assert token != inspected
    stay += token == 0
    switch += token == survivor
print(f"trials={n}")
print(f"stay exact={2 / 3:.6f} empirical={stay / n:.6f}")
print(f"switch exact={1 / 3:.6f} empirical={switch / n:.6f}")
