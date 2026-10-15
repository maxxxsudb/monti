import random

random.seed(1401026)
n = 1_000_000
lam = 0.75
stay = switch = 0
for _ in range(n):
    fixed = random.random() < lam
    prize = random.randrange(3) if fixed else 0
    opened = random.choice([i for i in (1, 2) if i != prize])
    other = 3 - opened
    stay += prize == 0
    switch += prize == other
print(f"trials={n} lambda={lam}")
print(f"stay exact={1 - 2 * lam / 3:.6f} empirical={stay / n:.6f}")
print(f"switch exact={2 * lam / 3:.6f} empirical={switch / n:.6f}")
