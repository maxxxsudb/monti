import random

rng = random.Random(20261015)
n = 1_000_000
remaining_live = protected_live = initial_remaining = 0
for _ in range(n):
    target = rng.randrange(3)
    first = rng.choice((1, 2))
    second = 3 - first
    if first == target:
        remaining = first
        live = False
    else:
        remaining = second
        live = remaining == target
    remaining_live += live
    protected_live += target == 0
    initial_remaining += remaining == target
print('foreign usable: exact 1/3, MC', remaining_live / n)
print('protected usable: exact 1/3, MC', protected_live / n)
print('foreign originally charged: exact 2/3, MC', initial_remaining / n)
