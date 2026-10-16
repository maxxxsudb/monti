"""Round 10: rank-only rewards keep the last binary test worthless.

Prediction from P11: if the reward depends only on the rank the target gets in
your ordering (top-k choice, weighted ranking), the envelope sum_r w_r l_(r)
has kinks only at the other options' l values (atoms), so a two-valued l never
straddles a kink. A threshold (walk away) adds kinks elsewhere.
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from r10_envelope import bayes_value  # noqa: E402


def rank_reward(w):
    def pay(joint):
        return sum(wr * p for wr, p in zip(w, sorted(joint, reverse=True)))
    return pay


TESTS = [
    ("coin Monty q=1/2", [F(1), F(0)], [F(1, 2), F(1, 2)]),
    ("binary a=3/4 b=1/3", [F(3, 4), F(1, 4)], [F(1, 3), F(2, 3)]),
    ("3 LR values", [F(1, 2), F(1, 3), F(1, 6)], [F(1, 6), F(1, 3), F(1, 2)]),
]
REWARDS = {
    "top-2 of n": lambda n: [1, 1] + [0] * (n - 2),
    "rank weights 3,1,0..": lambda n: [3, 1] + [0] * (n - 2),
    "rank weights n..1": lambda n: list(range(n, 0, -1)),
}
ok = True
for name, g1, g0 in TESTS:
    two = len({a / b for a, b in zip(g1, g0) if b}) + any(b == 0 for b in g0) <= 2
    for rname, wf in REWARDS.items():
        for n in (3, 4):
            pay = rank_reward(wf(n))
            gain = bayes_value(n, n, g1, g0, pay) - bayes_value(n, n - 1, g1, g0, pay)
            if two:
                ok &= gain == 0
            print(f"{name:20s} {rname:22s} n={n} last-test gain={gain}")
print("RANK CHECKS PASSED" if ok else "RANK CHECK FAILED")
