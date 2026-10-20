#!/usr/bin/env python3
"""Exact calculations supporting DEEP-FIVE-TASKS-2026-10-20.md.
Pure Python 3, no dependencies. An arithmetic check is not a proof of theorems.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial, ceil, log
from itertools import combinations

PARTITIONS = (
    ((0,), (1,), (2,), (3,)),   # Q2(alpha=1/4), 4 labels
    ((0, 3), (1, 2)),          # Q2(alpha=1/2), 2 labels
    ((0, 2), (1,), (3,)),     # Q1, prior returns 1/3, not r64's 1/2
)

def make_channel(groups):
    n = len(groups)
    label = {h: i for i, group in enumerate(groups) for h in group}
    return tuple(tuple(F(9, 10) if a == label[h]
                      else F(1, 10 * (n - 1)) for a in range(n))
                 for h in range(4))

CHANNELS = tuple(make_channel(g) for g in PARTITIONS)


def dp(price, horizon):
    @lru_cache(None)
    def recurse(belief, steps):
        baseline = 1 - max(belief)
        if not steps:
            return baseline
        optimum = baseline
        for kernel in CHANNELS:
            risk = price
            for output in range(len(kernel[0])):
                weights = [belief[h] * kernel[h][output] for h in range(4)]
                mass = sum(weights)
                if mass:
                    risk += mass * recurse(tuple(w / mass for w in weights), steps - 1)
            optimum = min(optimum, risk)
        return optimum
    return recurse((F(1, 4),) * 4, horizon)


def verify_dp():
    expected = {
        F(1, 10): [F(1, 5)] * 5,
        F(1, 20): [F(3, 20), F(3, 20), F(197, 1500), F(5483, 45000), F(27307, 225000)],
        F(0): [F(1, 10), F(1, 10), F(11, 500), F(29, 2500), F(203, 50000)],
    }
    for price, target in expected.items():
        observed = [dp(price, h) for h in range(1, 6)]
        assert observed == target, (price, observed, target)
        print(f"POMDP c={price}: {', '.join(map(str, observed))} — OK")


def polynomial(theta, roots, multiplier=F(1, 4)):
    out = multiplier
    for root in roots:
        out *= theta - root
    return out


def verify_polynomial_witness():
    for n in range(1, 9):
        grid = [F(i, n) for i in range(n + 1)]
        roots = grid[:n]
        assert all(polynomial(x, roots) == 0 for x in grid[:n])
        bound = F(factorial(n), 4 * 2**n * n**n)
        assert max(abs(polynomial(x, roots)) for x in grid) >= bound
        # Exact identity: sum of Lagrange leading coefficients = 1
        samples = [polynomial(x, roots, F(1)) for x in grid]
        interpolation_sum = sum(samples[i] * (-1) ** (n - i)
                                * F(n**n, factorial(i) * factorial(n - i))
                                for i in range(n + 1))
        assert interpolation_sum == 1
        print(f"Analytic classes N={n}: {n} questions can fail; "
              f"N+1={n+1} grid questions guarantee gap >= {bound}")


def verify_collision_curves():
    for q in [F(1, 100), F(1, 4), F(1, 2), F(3, 4), F(99, 100)]:
        boundaries = [F(1, q + 2), F(1, 2), F(2, q + 3), F(2, 3)]
        assert all(a < b for a, b in zip(boundaries, boundaries[1:]))
        a_f_half, _, a_f_two_thirds, _ = boundaries
        f = lambda alpha: alpha * (1 + q) / (1 + alpha * q)
        assert f(a_f_half) == F(1, 2)
        assert f(a_f_two_thirds) == F(2, 3)
    print('Collision curves: symbolic formulas verified on rational samples')


def smallest_battery(profiles, names):
    """Exact exhaustive separation of finite deterministic response profiles.
    Each profile is a tuple of response labels in the order given by names.
    """
    profiles = list(profiles.items())
    width = len(names)
    for size in range(1, width + 1):
        for chosen in combinations(range(width), size):
            seen = {tuple(row[i] for i in chosen) for _, row in profiles}
            if len(seen) == len(profiles):
                return tuple(names[i] for i in chosen)
    return None


def verify_relational_battery():
    tests = ('low_low', 'high_assoc_only', 'role_bridge_only', 'both_high')
    profiles = {
        'correct':       (0, 0, 0, 0),
        'association':   (0, 1, 0, 1),
        'role_transfer': (0, 0, 1, 1),
        'both':          (0, 1, 1, 1),
        'always_unknown':(2, 2, 2, 2),
    }
    battery = smallest_battery(profiles, tests)
    assert battery == ('high_assoc_only', 'role_bridge_only'), battery
    print('Minimal synthetic factorial battery:', battery)


def print_budget_examples():
    for k, min_cost, eta in [(4, .1, .001), (3, .05, .01)]:
        max_stop_risk = 1 - 1/k
        block = ceil(2 * max_stop_risk / min_cost)
        horizon = block * ceil(log(1 / eta, 2))
        print(f"k={k}, cmin={min_cost}, target<={eta}: sufficient T={horizon} "
              f"(block {block}; valid for 0-1 terminal loss)")

if __name__ == '__main__':
    verify_dp()
    verify_polynomial_witness()
    verify_collision_curves()
    verify_relational_battery()
    print_budget_examples()
    print('ALL CHECKS PASS')
