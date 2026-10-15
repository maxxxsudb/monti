import math
import random

rng = random.Random(3142026)
n = 1_000_000

def show(label, exact, good, total):
    value = good / total
    se = math.sqrt(exact * (1 - exact) / total)
    print(f'{label}: exact={exact:.8f} MC={value:.8f} accepted={total} z={(value-exact)/se:.2f}')

p = .9
counts = [0, 0]
for _ in range(n):
    empty = rng.randrange(3)
    b = empty != 1 and rng.random() < p
    c = empty != 2 and rng.random() < p
    if c and not b:
        counts[1] += 1
        counts[0] += empty == 1
show('reliable switch p=.9', 1 / (2-p), *counts)

beta = .5
lo, hi = 1, 1.2
counts = [0, 0]
for _ in range(n):
    empty = rng.randrange(3)
    clocks = [math.inf if i == empty else rng.expovariate(1-beta if i == 0 else 1) for i in range(3)]
    if clocks[2] == min(clocks) and lo <= clocks[2] < hi:
        counts[1] += 1
        counts[0] += empty == 0
w_a = (math.exp(-2*lo)-math.exp(-2*hi))/2
w_b = (math.exp(-(2-beta)*lo)-math.exp(-(2-beta)*hi))/(2-beta)
show('partial shield first-C in [1,1.2), stay', w_a/(w_a+w_b), *counts)

counts = [0, 0]
for _ in range(n):
    empty = rng.randrange(4)
    c = empty != 2 and rng.random() < p
    d = empty != 3 and rng.random() < p
    if d and not c:
        counts[1] += 1
        counts[0] += empty == 1
show('two shields, neighbor empty p=.9', (1-p)/(3-2*p), *counts)

counts = [0, 0]
for _ in range(n):
    prize = rng.randrange(3)
    informed = rng.random() < .5
    opened = rng.choice([i for i in (1,2) if i != prize]) if informed else rng.choice((1,2))
    if opened != prize:
        counts[1] += 1
        counts[0] += prize != 0
show('half-informed, switch given goat', .6, *counts)

counts = [0, 0]
for _ in range(n):
    u = rng.random()
    prize = 0 if u < .5 else 1 if u < .75 else 2
    no_budget = rng.random() < 1/3
    if no_budget or prize == 1:
        counts[1] += 1
        counts[0] += prize == 1
show('resource pass, prize B', .5, *counts)
