from fractions import Fraction as F
from itertools import product


counts = {"schedules": 0, "mixtures": 0, "sharp_bounds": 0, "two_queries": 0}
for lengths in product(range(1, 9), repeat=3):
    n = len(lengths)
    mu = F(sum(lengths), n)
    variance = sum((F(x) - mu) ** 2 for x in lengths) / n
    interval_wait = sum(F(x, 2 * n) for x in lengths)
    time_wait = sum(F(x, sum(lengths)) * F(x, 2) for x in lengths)
    assert time_wait - interval_wait == variance / (2 * mu)
    assert (time_wait == interval_wait) == (len(set(lengths)) == 1)
    counts["schedules"] += 1
assert (F(5) ** 2 + F(15) ** 2) / (2 * (5 + 15)) == F(25, 4)

for a, b, u, v, alpha in product(
    [F(i, 5) for i in range(1, 6)],
    [F(i, 5) for i in range(1, 6)],
    [F(i, 4) for i in range(5)],
    [F(i, 4) for i in range(5)],
    [F(i, 10) for i in range(11)],
):
    joint_y_e = alpha * a * u + (1 - alpha) * b * v
    event = alpha * a + (1 - alpha) * b
    correct = joint_y_e / event
    naive = alpha * u + (1 - alpha) * v
    assert correct - naive == alpha * (1 - alpha) * (a - b) * (u - v) / event
    if 0 < alpha < 1:
        assert (correct == naive) == (a == b or u == v)
    counts["mixtures"] += 1

for s, t in product([F(i, 6) for i in range(1, 7)], repeat=2):
    a, b = s * s, t * t
    bound = abs(s - t) / (s + t)
    optimum = t / (s + t)
    assert abs(optimum * a / (optimum * a + (1 - optimum) * b) - optimum) == bound
    for alpha in [F(i, 20) for i in range(21)]:
        denominator = alpha * a + (1 - alpha) * b
        gap = abs(alpha * a / denominator - alpha)
        remainder = bound * (alpha * (s + t) - t) ** 2 / denominator
        assert bound - gap == remainder >= 0
        counts["sharp_bounds"] += 1


def aware(x):
    return 2 * x / (1 + x)


for left, right in product([F(i, 20) for i in range(1, 20)], repeat=2):
    if left >= right:
        continue
    assert aware(left) < aware(right)
    assert aware(left) > left and aware(right) > right
    counts["two_queries"] += 1

aware_pair = (aware(F(1, 4)), aware(F(3, 4)))
prior_pair = (F(1, 4), F(3, 4))
distance = max(abs(x - y) for x, y in zip(aware_pair, prior_pair))
assert distance == F(3, 20)
assert (aware_pair[1] - aware_pair[0]) / 2 == F(8, 35)
assert (prior_pair[1] - prior_pair[0]) / 2 == F(1, 4)
midpoint = tuple((x + y) / 2 for x, y in zip(aware_pair, prior_pair))
assert max(abs(x - y) for x, y in zip(midpoint, aware_pair)) == F(3, 40)
assert max(abs(x - y) for x, y in zip(midpoint, prior_pair)) == F(3, 40)
print("PASS", counts, "robust noise threshold = 3/40")
