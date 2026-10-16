"""Round 12 (cell G x I2): a perfect whole-unit test is worthless for the assembly.

Flashlights of R03: types W (all good), L (bad lamp), B (bad battery), one of
each, six equally likely placements. Unit A is kept; we must use A's lamp and
pick a battery from donor 1 or donor 2. Compare what the player observes
before choosing the donor:
  none        - nothing;
  unit_test   - perfect pass/fail of each donor as a whole flashlight;
  first_dark  - which donor goes dark first (weak lamp dies before weak battery);
  batteries   - perfect knowledge of both donor batteries;
  everything  - full types.
Value = P(A's lamp + chosen battery works) under the best choice given the
observation, exact fractions.
"""
from fractions import Fraction as F
from itertools import permutations

LAMP = {"W": 1, "L": 0, "B": 1}
BATT = {"W": 1, "L": 1, "B": 0}
DIES = {"W": 9, "L": 1, "B": 2}  # W never dies during the run; L before B


def observe(kind, d1, d2):
    if kind == "none":
        return ()
    if kind == "unit_test":
        return (d1 == "W", d2 == "W")
    if kind == "first_dark":
        return 1 if DIES[d1] < DIES[d2] else 2
    if kind == "batteries":
        return (BATT[d1], BATT[d2])
    if kind == "everything":
        return (d1, d2)


def value(kind):
    groups = {}
    for a, d1, d2 in permutations("WLB"):
        obs = observe(kind, d1, d2)
        g = groups.setdefault(obs, [F(0), F(0)])
        g[0] += F(1, 6) * LAMP[a] * BATT[d1]
        g[1] += F(1, 6) * LAMP[a] * BATT[d2]
    return sum(max(g) for g in groups.values())


vals = {k: value(k) for k in ("none", "unit_test", "first_dark", "batteries", "everything")}
for k, v in vals.items():
    print(f"{k:11s} {v}")
assert vals["none"] == F(1, 2)
assert vals["unit_test"] == F(1, 2)          # perfect whole-unit test: zero value
assert vals["first_dark"] == F(2, 3)         # crude ordering: +1/6
assert vals["batteries"] == F(2, 3) == vals["everything"]
print("ALL OK: unit test worth 0, first-dark worth 1/6 = full information")
